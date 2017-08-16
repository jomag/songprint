
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
    "title": "My First Songbook",
    "prefix": "./songs/",
    "songs": [
        "gentle_on_my_mind.song.md",
        "make_you_feel_my_love.md"
    ]
}
~~~

File format
-----------

The song file format is based on Markdown. Many of the markup methods
used in Markdown works here as well but there's also many extensions
specific for the use case.

Each song is stored in a single file, and a file can only hold one song.

Meta data may be supplied for each song to show extra information and
customize the layout. The meta data should be placed at the very top
of each song file.

Example:

~~~
Title: Gentle On My Mind
Artist: Glenn Campbell
Author: John Hartford

It's knowing that your door is always open
and your path is free to walk ...
~~~
