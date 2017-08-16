
Song Print Project
==================

This is a project to organize the song texts and chords I keep collecting
in files all over the place in various formats.

Songbook configuration
----------------------

The songbook configuration is stored in a JSON file. An example configuration
(example.json) is included.

~~~json
{
    "title": "...",     // Name of the songbook
    "prefix": "./",     // Path prefix for all songs
    "songs": [
        // List of songs. The full path is 'prefix' plus the file name
        "gentle_on_my_mind.song.md",
        "make_you_feel_my_love.md"
    ]
}
~~

File format
-----------

The song file format is based on Markdown. Many of the markup methods
used in Markdown works here as well but there's also many extensions
specific for the use case.

Each song is stored in a single file, and a file can only hold one song.

Lines starting with a key word followed by two colons are treated as
key values, where the key is the word before the first colon
and the value is whatever is stored after the last colon:

Example:

~~~
Artist:: Glenn Campbell
Author:: John Hartford
~~~
