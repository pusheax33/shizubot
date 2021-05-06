

class ShizuPlaylist:

    """
        Ejemplo playlist:
        {
            "server_id" : 125854735687834,
            "loop" : True,
            "tracklist" : [{
                'filepath': 'voice\\b01d9824c196e382Pokemon_Black_White_Sound_Gamerip_-_Berry_Obtained.m4a',
                'url' : 'https://www.youtube.com/watch?v=k84np4BslNI',
                'title': 'Pokémon Black & White Sound Gamerip: Berry Obtained',
                'duration': 3, 'view_count': 3581
            },
            {
                ...
            }]
        }
    """

    def __init__(self):
        self.playlists = []

    def create(self, server_id):
        """
            Crea una nueva playlist enlazada al server_id pasada por parametro. Si el server ya tiene una playlist
            registrada, la devuelve.
        """
        server_playlist = self.get(server_id)
        if server_playlist:
            print(f"La playlist que se intenta crear ya existe para el server {server_id}, retornando la existente.")
            return server_playlist

        server_playlist = {
            "server_id" : server_id,
            "loop" : False,
            "tracklist" : []
        }
        self.playlists.append(server_playlist)
        return server_playlist

    def add(self, server_id, youtube_result_data):
        """
            Agrega un diccionario con la data del audio a una playlist existente. Si la playlist no existe
            se la crea, se agrega la data y se retorna la playlist.
        """
        if not youtube_result_data:
            raise ShizuPlaylistException("ERROR: youtube_result_data es None")

        playlist = self.get(server_id)
        if not playlist:
            print("Se intenta agregar en una playlist que no existe, se procede a crear una nueva playlist y agregar.")
            playlist = self.create(server_id)

        playlist["tracklist"].append(youtube_result_data)
        print(self.playlists)
        return playlist

    def get(self, guild_id):
        """
            Devuelve la playlist correspondiente a la guild_id pasada por parametro
        """
        for playlist in self.playlists:
            if playlist["server_id"] == guild_id:
                return playlist

    def get_next_song(self, guild_id):
        """
            Devuelve un diccionario con la informacion de la siguiente cancion de la playlist
        """
        playlist = self.get(guild_id)
        if not playlist:
            return
        if not playlist["tracklist"]:
            return

        if playlist["loop"]:
            # Loop activado, coloco la cancion actual al final de la playlist
            track = playlist["tracklist"][0]
            del playlist["tracklist"][0]
            playlist["tracklist"].append(track)

        else:
            del playlist["tracklist"][0]

        if playlist["tracklist"]:
            # Retorno la primera cancion de la playlist
            return playlist["tracklist"][0]

    def get_current_song(self, guild_id):
        """
            Devuelve un diccionario con la informacion de la cancion actual
        """
        playlist = self.get(guild_id)
        if playlist:
            return playlist["tracklist"][0]

    def remove(self, guild_id):
        """
            Elimina la playlist correspondiente al guild_id pasado por parametro
        """
        playlist = self.get(guild_id)
        if playlist:
            del self.playlists[self.playlists.index(playlist)]
            return True
        return False

    def save_guild_playlist(self, guild_id):
        """
            Guarda la playlist en la base de datos de la guild
        """
        pass

    def save_member_playlist(self, member_id):
        """
            Guarda la playlist en la base de datos del miembro
        """
        pass


class ShizuPlaylistException(Exception):
    def __init__(self, message):
        self.message = message
        print(self.__str__)

    def __str__(self):
        return str(self.message)
        