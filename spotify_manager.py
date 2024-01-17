import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_USER_NAME

class SpotifyManager:
    """
    Esta clase maneja la interacción con la API de Spotify.
    Permite buscar canciones y crear playlists en una cuenta de usuario de Spotify.
    """

    def __init__(self):
        """
        Inicializa la instancia de SpotifyManager autenticándose con la API de Spotify.
        """
        # Configuración del gestor de autenticación OAuth con los parámetros necesarios.
        self.auth_manager = SpotifyOAuth(
            scope="playlist-modify-private",  # Define los permisos requeridos.
            redirect_uri=SPOTIFY_REDIRECT_URI,  # URI de redirección registrada en la aplicación de Spotify.
            client_id=SPOTIFY_CLIENT_ID,  # ID de cliente de la aplicación de Spotify.
            client_secret=SPOTIFY_CLIENT_SECRET,  # Secreto de cliente de la aplicación de Spotify.
            show_dialog=True,  # Muestra el diálogo de autenticación cada vez.
            cache_path="token.txt",  # Archivo donde se almacena el token de acceso.
            username=SPOTIFY_USER_NAME  # Nombre de usuario de Spotify.
        )
        # Crea el cliente de Spotify usando el gestor de autenticación.
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def search_song(self, song_name, artist_name):
        """
        Busca una canción en Spotify por nombre y artista y devuelve su URI de Spotify.

        Parameters:
            song_name (str): Nombre de la canción a buscar.
            artist_name (str): Nombre del artista de la canción a buscar.

        Returns:
            str: URI de Spotify de la canción encontrada, o None si no se encuentra.
        """
        query = f"track:{song_name} artist:{artist_name}"
        result = self.sp.search(q=query, type='track', limit=1)
        tracks = result['tracks']['items']
        if tracks:
            # Si se encuentra la canción, devuelve el URI de Spotify.
            return tracks[0]['uri']
        else:
            # Si no se encuentra la canción, imprime un mensaje y devuelve None.
            print(f"No se encontró la canción: {song_name} de {artist_name}")
            return None

    def create_spotify_playlist(self, user_id, date, song_artist_list):
        """
        Crea una playlist en la cuenta del usuario de Spotify y agrega las canciones proporcionadas.

        Parameters:
            user_id (str): ID de usuario de Spotify.
            date (str): Fecha que se utilizará en el nombre de la playlist.
            song_artist_list (list): Lista de canciones y artistas a agregar a la playlist.
        """
        # Define el nombre y la descripción de la nueva playlist.
        playlist_name = f"Billboard Top 100 - {date}"
        playlist_description = "Playlist generada con las 100 mejores canciones de Billboard."

        # Crea la playlist en Spotify y obtiene su ID.
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        playlist_id = playlist['id']

        # Busca las URIs de Spotify de las canciones y las agrega a la playlist.
        uris = []
        for song_artist in song_artist_list:
            song_name, artist_name = song_artist.split(" by ")
            uri = self.search_song(song_name, artist_name)
            if uri:
                uris.append(uri)

        # Agrega las canciones a la playlist y notifica al usuario.
        if uris:
            self.sp.playlist_add_items(playlist_id=playlist_id, items=uris)
            print(f"Se agregaron {len(uris)} canciones a la playlist '{playlist_name}'.")
        else:
            print("No se pudo agregar ninguna canción a la playlist.")
