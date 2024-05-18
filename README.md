# Billboard to Spotify Playlist

Este programa permite generar una playlist en Spotify con las canciones del Billboard Hot 100 de una fecha específica. Utiliza la API de Spotify para autenticarse y crear la playlist, y la página web de Billboard para obtener las canciones.

## Requisitos

- Python 3.x
- Paquetes de Python: `requests`, `beautifulsoup4`, `spotipy`
- Credenciales de la API de Spotify ([ver cómo obtenerlas](##notas-adicionales))
  
## Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/tu-usuario/billboard-to-spotify.git
   cd billboard-to-spotify
   ```

2. **Instala las dependencias:**

   ```bash
   pip install requests beautifulsoup4 spotipy
   ```

3. **Configura las credenciales de Spotify:**

   Crea un archivo llamado `config.py` en el directorio raíz del proyecto y añade tus credenciales de Spotify:

   ```python
   SPOTIFY_CLIENT_ID = 'tu_client_id'
   SPOTIFY_CLIENT_SECRET = 'tu_client_secret'
   SPOTIFY_REDIRECT_URI = 'tu_redirect_uri'
   SPOTIFY_USER_NAME = 'tu_usuario'
   ```

## Uso

1. **Ejecuta el programa:**

   ```bash
   python main.py
   ```

2. **Introduce una fecha:**

   Cuando se te solicite, introduce una fecha en el formato `YYYY-MM-DD` para obtener las canciones del Billboard Hot 100 de esa fecha.

3. **Autenticación de Spotify:**

   Se abrirá una ventana del navegador para que inicies sesión en Spotify y concedas permisos al programa.

4. **Generación de la Playlist:**

   El programa obtendrá las canciones de Billboard, las buscará en Spotify y creará una playlist en tu cuenta de Spotify con las canciones encontradas.

## Archivos

- `main.py`: Contiene la lógica principal del programa.
- `billboard_scraper.py`: Contiene la función para obtener las canciones de Billboard.
- `spotify_manager.py`: Contiene la clase `SpotifyManager` para gestionar la interacción con la API de Spotify.
- `config.py`: Archivo de configuración con las credenciales de Spotify.

## Código

### main.py

```python
from datetime import datetime
from billboard_scraper import fetch_songs_from_billboard
from spotify_manager import SpotifyManager

def is_valid_date(date_str):
    """
    Comprueba si la cadena de fecha proporcionada es una fecha válida y si es menor o igual a la fecha actual.

    Parameters:
        date_str (str): La fecha en formato de cadena "YYYY-MM-DD".

    Returns:
        bool: True si la fecha es válida y no está en el futuro, False en caso contrario.
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj <= datetime.now()
    except ValueError:
        return False

def main():
    """
    Función principal que ejecuta el programa. Gestiona la autenticación de Spotify, 
    obtiene la lista de canciones de Billboard y crea la playlist en Spotify.
    """
    spotify_manager = SpotifyManager()

    while True:
        week_date = input("Enter the date you want to check (YYYY-MM-DD): ")

        if is_valid_date(week_date):
            song_artist_list = fetch_songs_from_billboard(week_date)

            if song_artist_list:
                user_id = spotify_manager.sp.current_user()["id"]
                spotify_manager.create_spotify_playlist(user_id, week_date, song_artist_list)
                print(f"Playlist created for date {week_date}")
            else:
                print("No songs found for the given date. Please check the date and try again.")
            break
        else:
            print("Invalid date or format. Please enter a valid date in YYYY-MM-DD format and make sure it's not in the future.")

if __name__ == "__main__":
    main()
```

### billboard_scraper.py

```python
import requests
from bs4 import BeautifulSoup

def fetch_songs_from_billboard(date):
    """
    Fetch the list of top 100 songs from the Billboard Hot 100 chart for a given date.

    Parameters:
        date (str): The date in YYYY-MM-DD format to fetch the songs for.

    Returns:
        list of str: A list of strings, each containing "song title by artist", or an empty list if an error occurs.
    """

    url = f"https://www.billboard.com/charts/hot-100/{date}"
    print(f"Fetching data from: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("The request timed out. Please try again or check your connection.")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []

    web_page = response.text
    soup = BeautifulSoup(web_page, "html.parser")

    songs = []
    artists = []

    tag = soup.find_all(name="li", class_="lrv-u-width-100p")

    for i in tag:
        t = i.find_all(name="ul")
        for j in t:
            t1 = j.find_all(name="li")
            for k in t1:
                t2 = k.find_all(name="h3")
                for l in t2:
                    t3 = l.get_text()
                    songs.append(str(t3).strip("\n\t"))
                t4 = k.find_all(name="span")
                for m in t4:
                    t5 = m.get_text()
                    artists.append(str(t5).strip("\n\t"))

    artists = artists[::16]
    combined_song_artist = [f"{songs[i]} by {artists[i]}" for i in range(len(songs))]
    return combined_song_artist
```

### spotify_manager.py

```python
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
        self.auth_manager = SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri=SPOTIFY_REDIRECT_URI,
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt",
            username=SPOTIFY_USER_NAME
        )
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
            return tracks[0]['uri']
        else:
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
        playlist_name = f"Billboard Top 100 - {date}"
        playlist_description = "Playlist generada con las 100 mejores canciones de Billboard."

        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        playlist_id = playlist['id']

        uris = []
        for song_artist in song_artist_list:
            song_name, artist_name = song_artist.split(" by ")
            uri = self.search_song(song_name, artist_name)
            if uri:
                uris.append(uri)

        if uris:
            self.sp.playlist_add_items(playlist_id=playlist_id, items=uris)
            print(f"Se agregaron {len(uris)} canciones a la playlist '{playlist_name}'.")
        else:
            print("No se pudo agregar ninguna canción a la playlist.")
```

## Notas Adicionales

- Asegúrate de tener las credenciales correctas para la API de Spotify en el archivo `config.py`.
- Puedes modificar los scripts según tus necesidades, como cambiar el nombre de la playlist o ajustar la lógica de búsqueda de canciones.

  Para usar la API de Spotify y conseguir las credenciales necesarias (Client ID, Client Secret, Redirect URI y User Name), sigue estos pasos:

### Paso 1: Crear una Aplicación en Spotify Developer Dashboard

1. **Visita el Spotify Developer Dashboard:**
   Ve a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).

2. **Inicia Sesión:**
   Inicia sesión con tu cuenta de Spotify. Si no tienes una, deberás crear una.

3. **Crea una Nueva Aplicación:**
   - Haz clic en el botón `Create an App`.
   - Completa los campos requeridos:
     - **App name:** Un nombre para tu aplicación (puede ser cualquier cosa relevante para tu proyecto).
     - **App description:** Una descripción breve de tu aplicación.
   - Acepta los términos y condiciones y haz clic en `Create`.

4. **Obtén tus Credenciales:**
   - Después de crear la aplicación, serás redirigido a la página de detalles de la aplicación.
   - Aquí encontrarás tu **Client ID** y **Client Secret**.

### Paso 2: Configurar el Redirect URI

1. **Configura el Redirect URI:**
   - En la página de detalles de tu aplicación, haz clic en `Edit Settings`.
   - En la sección `Redirect URIs`, agrega un URI de redirección. Un ejemplo común es `http://localhost:8888/callback`, pero puedes usar cualquier URI que manejes en tu aplicación.
   - Haz clic en `Add` y luego en `Save`.

2. **Nota sobre el Redirect URI:**
   - El Redirect URI debe coincidir exactamente con el que uses en tu aplicación. Asegúrate de configurarlo correctamente tanto en la consola de desarrollador como en tu código.

### Paso 3: Obtener tu Nombre de Usuario de Spotify

1. **Encuentra tu Nombre de Usuario:**
   - Abre la aplicación de Spotify en tu computadora o ve a la [web player de Spotify](https://open.spotify.com/).
   - Haz clic en tu nombre de perfil en la esquina superior derecha y selecciona `Cuenta`.
   - En la página de tu cuenta, verás tu nombre de usuario de Spotify. Este es el que necesitas.

### Configuración en el Archivo `config.py`

Crea un archivo llamado `config.py` en tu proyecto y añade las credenciales obtenidas:

```python
# config.py
SPOTIFY_CLIENT_ID = 'tu_client_id'
SPOTIFY_CLIENT_SECRET = 'tu_client_secret'
SPOTIFY_REDIRECT_URI = 'tu_redirect_uri'
SPOTIFY_USER_NAME = 'tu_usuario'
```

### Resumen

1. **Crear una Aplicación en Spotify Developer Dashboard** para obtener el Client ID y Client Secret.
2. **Configurar el Redirect URI** en la configuración de la aplicación en el dashboard.
3. **Obtener tu Nombre de Usuario de Spotify** desde tu cuenta de Spotify.
4. **Añadir las credenciales al archivo `config.py`** en tu proyecto.

Estos pasos te permitirán obtener y configurar las credenciales necesarias para utilizar la API de Spotify en tu proyecto.
