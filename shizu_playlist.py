import os
from pathlib import Path

class ShizuPlaylist:

    allowed_extensions = ["mp3", "wav", "ogg", "webm"]
    playlist_path = ""
    playlist = []

    def __init__(self, playlist_path):
        self.playlist_path = playlist_path
        self.load_playlist()

    def load_playlist(self):
        try:
        # open the playlist located at self.playlist_path, if doesn't exists it creates a new one
            with open(self.playlist_path, "r", encoding="utf-8") as pl:
                self.playlist = pl.read().split("|")
        except FileNotFoundError:
            print("Playlist path doesn't exists. Attempt to create a new playlist...")
            self.create_playlist()

    def create_playlist(self, music_path="/music"):
        # creates a playlist.sz from the specified path, the default path is the music folder
        try:
            for root, directories, files in os.walk(files):
                for song_path in files:
                    if Path(song_path).suffix in self.allowed_extensions:
                        self.playlist.append(root + "\\" + song_path)
            self.save_playlist()
        except FileNotFoundError:
            print("Can't create a playlist, the specified playlist path doesn't exists")

    def save_playlist(self):
        # saves the playlist to the script folder
        if len(self.playlist) > 0:
            playlist_joined = "|".join(self.playlist)
            with open(os.path.dirname(__file__) + "\\playlist.sz", "w+", encoding="utf-8") as pl:
                pl.write(playlist_joined)
        else:
            print("The specified playlist is empty, can't save playlist.")



        