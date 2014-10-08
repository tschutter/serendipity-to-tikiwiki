serendipity-to-tikiwiki
=======================

Converts Serendipity (s9y) blogs into Tiki Wiki blogs.

Synopsis
--------

``import-s9y.py`` may be a helpful start for automating the process of
converting your Serendipity <http://www.s9y.org> blog posts into
Tikiwiki blogs.  I wrote it to do the job on my particular
installation (serendipity-1.3.1 and tikiwiki-2.3).  Although I expect
the code to be reasonably portable, I make no guarantees. Expect to
get your hands dirty.

Features
--------

* Serendipity markup translation is fully implemented.
* Textile markup translation is partly implemented.
* Optional filter on author.
* Optional filter on category.

Shortcomings
------------

* Serendipity blog post comments are ignored.
* Serendipity extended bodies are ignored.
* Serendipity trackbacks are ignored.
* Textile markup translation is only partly implemented.
* bbcode markup translation not implemented.
* textwiki markup translation not implemented.
* Destination blogs must be created by hand in Tikiwiki.  This script
  cannot create Tikiwiki blogs.

Import Procedure
----------------

1. MAKE A BACKUP OF YOUR DATABASE.

2. Create blogs in tikiwiki.  ``import-s9y.py`` cannot create blogs,
   it can only import posts into existing blogs.

3. Create an .ini file.  Use ``import-s9y.ini`` as a starting point.
   Read the description of the INI file below.

4. Make a dry run.  This will read the .ini file and scan the s9y
   database, but not make any changes to the Tikiwiki database::

    import-s9y.py --dry-run import-s9y.py

5. Do it for real::

    import-s9y.py import-s9y.py

INI File
--------

The configuration file consists of sections, led by a \[section\]
header and followed by name: value entries; name=value is also
accepted. Note that leading whitespace is removed from values.  Lines
beginning with '#' or ';' are ignored and may be used to provide
comments.

Each section of the .ini file (except for the \[DEFAULT\] section)
corresponds to an import pass from the s9y database.  The name of each
section is irrelevant as long as they are unique.  Parameters in the
\[DEFAULT\] section are used as defaults for the rest of the sections.

For each section, these parameters are mandatory:

s9yDriver
  : Type of database hosting Serendipity.  Can be mysql, postgres, or
  sqlite.

s9yHost
  : Hostname of the machine serving the Serendipity database.

s9yUser
  : Username with read access to the Serendipity database.

s9yPassword
  : Password for the Serendipity database.

s9yDatabase
  : Name of the Serendipity database.

s9yMarkup
  : Markup plugin installed in Serendipity.  Can be none, s9y,
  textile, bbcode, or textwiki.

tikiDriver
  : Type of database hosting Tikiwiki.  Can be mysql, postgres, or
  sqlite.  (Note that tikiwiki 2.3 does not support postgres or
  sqlite).

tikiHost
  : Hostname of the machine serving the Tikiwiki database.

tikiUser
  : Username with write access to the Tikiwiki database.

tikiPassword
  : Password for the Tikiwiki database.

tikiDatabase
  : Name of the Tikiwiki database.

tikiBlogName
  : Name of the Tikiwiki blog to import the posts into.

And these parameters are optional:

skip
  : If "1", or "True", then this section will be skipped.  Useful for
  debugging purposes.

s9yFilterAuthor
  : If defined, only posts by this Serendipity author will be
  imported.

s9yFilterCategory
  : If defined, only posts in this Serendipity category will be
  imported.  Use a colon to specify a sub category, like this:
  ``tom:sysadm``.  If you specify a category filter, posts in a
  subcategory will not be imported.  So a filter of ``tom`` will not
  import posts in the ``tom:sysadm`` category.

Relevant Links
--------------

* Inspiration for ``import-s9y.py``: <http://tikiwiki.org/ConversionFromTWiki>
* Tiki Wiki bug 2415 - CODE block cannot contain $ followed by any digit: <http://dev.tikiwiki.org/tiki-view_tracker_item.php?itemId=2415>
* Tikiwiki syntax: <http://doc.tikiwiki.org/wiki+syntax>
* Serendipity markup plugins: <http://s9y.org/50.html>
* PEAR Text_Wiki: <http://pear.php.net/package/Text_Wiki>
* Text_Wiki samples: <http://pear.reversefold.com/dokuwiki/text_wiki:samplepage>
* ADOdb for Python: <http://phplens.com/lens/adodb/adodb-py-docs.htm>
