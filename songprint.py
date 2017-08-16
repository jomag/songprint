
import json
import os

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.util import etree

from weasyprint import HTML, CSS

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
    font-family: "operator mono book"
}
"""


class SongMetaTreeprocessor(Treeprocessor):
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

    def get_meta(self, key):
        try:
            return self.md.Meta[key][0]
        except KeyError:
            pass


class SongMarkdownExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
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
        print(h)
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
                self.load_song(song)

            for song in self.songs:
                print(str(song))

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
    songbook = Songbook("example.json")
    songbook.render("output.pdf")


if __name__ == "__main__":
    main()
