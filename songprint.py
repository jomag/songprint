
import json
import os

import markdown

from weasyprint import HTML, CSS


class Song:
    def __init__(self, path=None):
        if path:
            self.load(path)

    def load(self, path):
        with open(path, "r") as f:
            self.file_content = f.read()

    def html(self):
        ext = ["markdown.extensions.nl2br"]
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
                self.load_song(song)

    def load_song(self, path):
        full_path = os.path.join(self.base_path, path)
        song = Song(full_path)
        self.songs.append(song)

    def render(self, destination):
        first_page = "<h1>{}</h1>".format(self.title)
        song_contents = "".join(song.html() for song in self.songs)
        html_content = first_page + song_contents
        css_doc = "h1 { color: #f00 }"
        html = HTML(string=html_content)
        css = CSS(string=css_doc)
        html.write_pdf(destination, stylesheets=[css])


def main():
    songbook = Songbook("example.json")
    songbook.render("output.pdf")


if __name__ == "__main__":
    main()
