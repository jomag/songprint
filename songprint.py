
import json
import os
import sys
import argparse
import time

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import Pattern, SimpleTagPattern
from markdown.extensions import Extension
from markdown.util import etree

from weasyprint import HTML, CSS

import colorama

BRIGHT = colorama.Style.BRIGHT
GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED
RESET = colorama.Style.RESET_ALL

default_stylesheet = """
h1.song-title {
    font-family: "operator mono";
    font-style: italic;
    font-weight: normal;
    margin-bottom: 0;
}

ul.song-meta {
    font-family: "operator mono light";
    font-style: italic;
    list-style: none;
    padding: 0;
    margin: 0;
}

p {
    font-family: "operator mono book";
}

p.with-chords {
    line-height: 2.3;
}

p.chorus {
    margin-left: 2em;
}

p.comment {
    font-size: 80%;
    font-style: italic;
}

span.chord {
  position: relative;
  top: -1em;
  display: inline-block;
  width: 0;
  overflow: visible;
  font-family: "operator mono light";
}
"""


class Task:
    BULLET = BRIGHT + YELLOW + " * " + RESET
    wip = ": "

    def __init__(self, description):
        self.description = description
        self.finished = False

    def __enter__(self):
        print(Task.BULLET + self.description + self.wip, flush=True, end="")
        return self

    def __exit__(self, type, value, tb):
        if not self.finished:
            self.ok()

    def ok(self, message="OK"):
        print(("\b" * len(self.wip)) + ": " + BRIGHT + GREEN + message + RESET)
        self.finished = True

    def error(self, message="failed"):
        print(("\b" * len(self.wip)) + ": " + BRIGHT + RED + message + RESET)
        self.finished = True

class ChordPattern(Pattern):
    CHORD_RE = r'(\[)([CDEFGABC][#b]?[79]?m?)(\])'

    def __init__(self):
        super().__init__(self.CHORD_RE)

    def handleMatch(self, m):
        el = etree.Element("span", attrib={"class": "chord"})
        el.text = m.group(3)
        return el


class SongMetaTreeprocessor(Treeprocessor):
    CHORUS_KEYWORDS = ("chorus", "refr", "refräng")

    def __init__(self, md):
        super().__init__()
        self.md = md

    def run(self, root):
        song_title = self.get_meta("title")

        artist = self.get_meta("artist")
        author = self.get_meta("author")
        year = self.get_meta("year")

        if artist or author or year:
            meta_block = etree.Element("ul", attrib={"class": "song-meta"})
            for x in [("Artist", artist), ("Author", author), ("Year", year)]:
                if x[1] is not None:
                    e = etree.Element("li")
                    e.text = "{}: {}".format(x[0], x[1])
                    meta_block.append(e)
            root.insert(0, meta_block)

        if song_title:
            title_header = etree.Element("h1", attrib={"class": "song-title"})
            title_header.text = song_title
            root.insert(0, title_header)

        for child in root:
            if child.tag == "p":
                classes = []
                if child.text:
                    lines = child.text.splitlines()
                    first_line = lines[0].strip().lower()
                    if first_line[-1] == ":":
                        first_line = first_line[0:-1]
                    if first_line in self.CHORUS_KEYWORDS:
                        classes.append("chorus")
                        child.text = "\n".join(lines[1:])
                    elif first_line in ["comment"]:
                        classes.append("comment")
                        child.text = "\n".join(lines[1:])
                    else:
                        classes.append("verse")

                # There is a problem: lines is always
                # of length 1 since it only contains the
                # text up to the first <br/> tag.
                # So we need to remove the <br/> tag as well.

                if child.findall("span[@class='chord']"):
                    classes.append("with-chords")

                if classes:
                    child.attrib["class"] = " ".join(classes)


    def get_meta(self, key):
        try:
            return self.md.Meta[key][0]
        except KeyError:
            pass


class SongMarkdownExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        # md.blockprocessors.add("song-chorus-and-verse", VerseAndChorusBlockProcessor(), ">inline")
        md.inlinePatterns["chord"] = ChordPattern()
        md.treeprocessors.add("song-meta", SongMetaTreeprocessor(md), ">inline")


class Song:
    def __init__(self, path=None):
        self.path = path
        if path:
            self.load(path)

    def load(self, path):
        with open(path, "r") as f:
            self.file_content = f.read()

    def html(self):
        ext = ["markdown.extensions.nl2br", "markdown.extensions.meta", SongMarkdownExtension()]
        h = markdown.markdown(self.file_content, extensions=ext)
        return h


class Songbook:
    title = "Songbook"
    base_path = "."

    def __init__(self, configfile=None):
        self.songs = []

        if configfile:
            self.load(path=configfile)

    def load(self, path):
        with open(path, "r") as f:
            content = f.read()
            config = json.loads(content)
            songs = []

            for key, value in config.items():
                if key == "title":
                    self.title = value
                elif key == "prefix":
                    self.base_path = value
                elif key == "songs":
                    songs = value

            for song in songs:
                with Task(song) as task:
                    try:
                        self.load_song(song)
                    except FileNotFoundError:
                        task.error("not found")

            #for song in self.songs:
            #    print(str(song))

    def load_song(self, path):
        full_path = os.path.join(self.base_path, path)
        song = Song(full_path)
        self.songs.append(song)

    def render(self, destination):
        br = '<p style="page-break-before: always" ></p>'
        first_page = "<h1>{}</h1>".format(self.title)
        song_contents = br.join(song.html() for song in self.songs)
        html_content = first_page + br + song_contents
        css_doc = default_stylesheet
        html = HTML(string=html_content)
        css = CSS(string=css_doc)
        html.write_pdf(destination, stylesheets=[css])


def main():
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("songbook", help="songbook definition file")
    args = parser.parse_args()

    songbook = Songbook(args.songbook)
    songbook.render("output.pdf")


if __name__ == "__main__":
    main()
