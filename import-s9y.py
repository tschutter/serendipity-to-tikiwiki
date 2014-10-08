#!/usr/bin/python
#
# Script to import blog entries from Serendipity 1.3.1 to Tikiwiki 2.3.
#
# Copyright (c) 2009-2009 Tom Schutter
# All rights reserved.
#

"""Converts Serendipity (s9y) blogs into Tiki Wiki blogs."""

from __future__ import print_function
from optparse import OptionParser
import ConfigParser
import adodb  # sudo apt-get install python-adodb
import os
import re
import sys


def sql_quote(str_val):
    """Quote a string to be imbedded in a SQL command."""
    # Escape single quote characters.
    str_val = str_val.replace("'", "''")

    # Enclose the entire string in single quotes.
    return "'" + str_val + "'"


def get_s9y_categoryid(s9y_connection, s9y_category_name):
    """Returns the categoryid for the Serendipity category."""
    subnames = s9y_category_name.split(":")
    categoryid = None
    for subname in subnames:
        statement =\
            "SELECT categoryid FROM s9y_category" +\
            " WHERE category_name = " + sql_quote(subname)
        if categoryid is not None:
            statement += " AND parentid = " + str(categoryid)
        cursor = s9y_connection.Execute(statement)
        categoryid = None
        for row in cursor:
            categoryid = row[0]
        if categoryid is None:
            return None

    return categoryid


def get_tiki_blog_id(tiki_connection, tiki_blog_name):
    """Returns the blog id for the Tikiwiki blog."""
    statement =\
        "SELECT blogId FROM `tiki_blogs`" +\
        " WHERE title = " + sql_quote(tiki_blog_name)
    cursor = tiki_connection.Execute(statement)
    for row in cursor:
        return row[0]

    return None


def translate_none(body):
    """Fallback translation."""
    body = body.replace("<p>", "")

    # WARNING: I prefer using {CODE(0)} over ~pp~, but any dollar
    # signs in the block will make the post unreadable.
    body = body.replace("<pre>", "{CODE(0)}\n")
    body = body.replace("</pre>", "\n{CODE}")
    # body = body.replace("<pre>", "~pp~")
    # body = body.replace("</pre>", "~/pp~")

    return body


def translate_s9y(body):
    """See serendipity_event_s9ymarkup/serendipity_event_s9ymarkup.php"""

    # _underlined text_
    body = body.replace(r'\_', chr(1))
    body = re.sub(r'\b_([\S ]+?)_\b', r'===\1===', body)
    body = body.replace(chr(1), r'\_')

    # #yyy# embeds #yyy# as an html entity, (#gt#, #lt# and #amp# for instance)
    body = re.sub(r'#([a-zA-Z0-9]+?)#', r'&\1;', body)

    # *bolded text*
    body = body.replace(r'\*', chr(1))
    body = body.replace(r'**', chr(2))
    body = re.sub(r'(\S)\*(\S)', r'\1' + chr(1) + r'\2', body)
    body = re.sub(r'\B\*([^*]+)\*\B', r'__\1__', body)
    body = body.replace(chr(2), r'**')
    body = body.replace(chr(1), r'\*')

    # |color|text|
    # commented out in
    # serendipity_event_s9ymarkup/serendipity_event_s9ymarkup.php
    # body = re.sub(r'\|([0-9a-fA-F]+?)\|([\S ]+?)\|', r'~~#\1:\2~~', body)

    # ^superscript^
    body = re.sub(r'\^([a-zA-Z0-9]+?)\^', r'{TAG(tag=>sup)}\1{TAG}', body)

    # @subscript@
    body = re.sub(r'@([a-zA-Z0-9]+?)@', r'{TAG(tag=>sub)}\1{TAG}', body)

    # escaped chars?
    body = re.sub(r'([\\])([*#_|^@%])', r'\2', body)

    return translate_none(body)


def translate_textile(body):
    """See serendipity_event_textile/textile.php"""

    # __italic__, _emphasis_
    body = body.replace(r'\_', chr(1))
    body = re.sub(r"\b__([\S ]+?)__\b", r"''\1''", body)
    body = re.sub(r"\b_([\S ]+?)_\b", r"''\1''", body)
    body = body.replace(chr(1), r'\_')

    # **bold**
    # We don't do *strong*, because it is too risky.
    body = body.replace(r'\*', chr(1))
    body = re.sub(r'\B\*\*([^*\n]+)\*\*\B', r'__\1__', body)
    body = body.replace(chr(1), r'\*')

    # ^superscript^
    body = re.sub(r'\^([a-zA-Z0-9]+?)\^', r'{TAG(tag=>sup)}\1{TAG}', body)

    # ~subscript~
    body = re.sub(r'~([a-zA-Z0-9]+?)~', r'{TAG(tag=>sub)}\1{TAG}', body)

    # @code@
    body = re.sub(
        r'@([-a-zA-Z0-9_/\.\\: ]+?)@',
        r'{MONO(font=>)}\1{MONO}',
        body
    )

    # ==notextile==
    body = re.sub(r'==([a-zA-Z0-9_]+?)==', r'~np~\1~/np~', body)

    return translate_none(body)


def translate_bbcode(body):
    """Translate BBcode markup."""
    return translate_none(body)


def translate_text_wiki(body):
    """Translate PEAR Text_Wiki markup."""
    return translate_none(body)


def check_params(params):
    """Check a single section of an .ini file."""
    skip = False

    # Check for required parameters.
    required_param_names = [
        "s9yDriver",
        "s9yHost",
        "s9yUser",
        "s9yPassword",
        "s9yDatabase",
        "s9yMarkup",
        "tikiDriver",
        "tikiHost",
        "tikiUser",
        "tikiPassword",
        "tikiDatabase",
        "tiki_blog_name"
    ]
    for param_name in required_param_names:
        if param_name not in params:
            print("ERROR: Missing parameter '{}'.".format(param_name))
            skip = True

    # Check for unknown parameters.
    optional_param_names = [
        "skip",
        "s9yFilterCategory",
        "s9yFilterAuthor"
    ]
    for param_name in params.keys():
        if not (
            param_name == "iniSection" or
            param_name in required_param_names or
            param_name in optional_param_names
        ):
            print("ERROR: Unknown parameter '{}'.".format(param_name))
            skip = True

    # Check for unsupported stuff.
    if params["s9yMarkup"] == "textile":
        print(
            "WARNING: textile markup translation is only partly implemented."
        )
    elif params["s9yMarkup"] == "bbcode":
        print("WARNING: bbcode markup translation not implemented.")
    elif params["s9yMarkup"] == "textwiki":
        print("WARNING: textwiki markup translation not implemented.")

    if "skip" in params:
        skip_value = params["skip"].lower()
        if skip_value not in ["0", "false", "no", "off"]:
            skip = True

    return skip


def do_import(options, params):
    """Import a blog based upon a section from the .ini file."""
    print("[{}]".format(params["iniSection"]))

    # Check to see if this section should be skipped.
    if check_params(params):
        return

    # Create a connection to the Serendipity database.
    s9y_connection = adodb.NewADOConnection(params["s9yDriver"])
    s9y_connection.Connect(
        params["s9yHost"],
        params["s9yUser"],
        params["s9yPassword"],
        params["s9yDatabase"]
    )

    # Create a connection to the Tikiwiki database.
    tiki_connection = adodb.NewADOConnection(params["tikiDriver"])
    tiki_connection.Connect(
        params["tikiHost"],
        params["tikiUser"],
        params["tikiPassword"],
        params["tikiDatabase"]
    )

    # Find the blog in Tikiwiki.
    blog_id = get_tiki_blog_id(tiki_connection, params["tiki_blog_name"])
    if blog_id is None:
        print(
            "ERROR: No Tikiwiki blog titled '" + params["tiki_blog_name"] +
            "' was found."
        )
        return 1

    # Build the query to fetch posts from Serendipity.
    join_clauses = []
    where_clauses = []

    if "s9yFilterAuthor" in params:
        where_clauses.append("author='" + params["s9yFilterAuthor"] + "'")

    if "s9yFilterCategory" in params:
        categoryid = get_s9y_categoryid(
            s9y_connection,
            params["s9yFilterCategory"]
        )
        join_clauses.append(
            "INNER JOIN s9y_entrycat" +
            " ON s9y_entries.id = s9y_entrycat.entryid"
        )
        where_clauses.append("s9y_entrycat.categoryid=" + str(categoryid))

    join_statement = " " + " ".join(join_clauses)
    if len(where_clauses) > 0:
        where_statement = " WHERE (" + " AND ".join(where_clauses) + ")"
    else:
        where_statement = ""
    statement =\
        "SELECT title,timestamp,body,author" +\
        " FROM s9y_entries" +\
        join_statement +\
        where_statement +\
        " ORDER BY id"

    # Loop through the Serendipity posts.
    n_posts = 0
    for row in s9y_connection.Execute(statement):
        # Extract the fields that we can import.
        (title, timestamp, body, author) = row

        if params["s9yMarkup"] == "none":
            body = translate_none(body)
        elif params["s9yMarkup"] == "s9y":
            body = translate_s9y(body)
        elif params["s9yMarkup"] == "textile":
            body = translate_textile(body)
        elif params["s9yMarkup"] == "bbcode":
            body = translate_bbcode(body)
        elif params["s9yMarkup"] == "textwiki":
            body = translate_text_wiki(body)
        else:
            print("ERROR: Unknown markup '{}'".format(params["s9yMarkup"]))
            return 1

        # Add the post to the tikiwiki database.
        statement =\
            "INSERT INTO `tiki_blog_posts`" +\
            " (blogId, data, data_size, created, user, title, priv)" +\
            " VALUES(" +\
            str(blog_id) + "," +\
            sql_quote(body) + "," + \
            "0," +\
            str(timestamp) + "," +\
            sql_quote(author) + "," +\
            sql_quote(title) + "," +\
            sql_quote("n") + ")"
        if not options.dryRun:
            tiki_connection.Execute(statement)
        n_posts += 1

        # Update the number of posts field in the tikiwiki database.
        statement =\
            "UPDATE tiki_blogs SET posts = posts + 1 WHERE blogId = " +\
            str(blog_id)
        if not options.dryRun:
            tiki_connection.Execute(statement)

    # Print some statistics.
    if options.dryRun:
        print("{} posts would be imported".format(n_posts))
    else:
        print("{} posts imported".format(n_posts))


def process_config_file(config_file):
    """Process the .ini file."""
    params_list = []
    config_parser = ConfigParser.ConfigParser()
    config_parser.optionxform = str  # Make the parser case sensitive.
    config_parser.read(config_file)
    ini_sections = config_parser.sections()
    for ini_section in ini_sections:
        # Collect the parameters into a dictionary.
        params = {"iniSection": ini_section}
        for (param_name, value) in config_parser.items(ini_section):
            # print(iniSection + ", " + param_name + ", " + value)
            params[param_name] = value
        params_list.append(params)

    return params_list


def main():
    """main"""

    # Process the command line.
    option_parser = OptionParser(usage="usage: %prog [options] INI_FILE")
    option_parser.set_defaults(dryRun=False)
    option_parser.add_option(
        "-n",
        "--dry-run",
        action="store_true",
        dest="dryRun",
        help="go through the motions, but do not change the Tikiwiki DB"
    )

    (options, args) = option_parser.parse_args()

    if len(args) != 1:
        option_parser.error("INI_FILE not specified")
    if not os.path.isfile(args[0]):
        option_parser.error("INI_FILE '" + args[0] + "' does not exist.")

    # Read the ini file.
    params_list = process_config_file(args[0])

    # Import each of the sections.
    for params in params_list:
        do_import(options, params)

    return 0


if __name__ == "__main__":
    sys.exit(main())
