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

    # Construir la URL para la lista de Billboard Hot 100 basada en la fecha proporcionada
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    print(f"Fetching data from: {url}")

    # Intentar realizar la solicitud HTTP con un tiempo de espera de 10 segundos
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Asegurar que se recibe una respuesta exitosa
    except requests.exceptions.Timeout:
        print("The request timed out. Please try again or check your connection.")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []


    # Usar BeautifulSoup para analizar el contenido de la página
    web_page = response.text
    soup = BeautifulSoup(web_page, "html.parser")

    # Inicializar listas para almacenar los títulos de las canciones y los artistas
    songs = []
    artists = []

    # Encontrar todos los elementos que contienen los datos de las canciones
    tag = soup.find_all(name="li", class_="lrv-u-width-100p")

    # Procesar cada entrada de canción y artista
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

    # Asumir que cada 16 elementos en la lista de artistas corresponde al artista de la canción
    artists = artists[::16]

    # Combinar canciones y artistas en una lista de strings
    combined_song_artist = [f"{songs[i]} by {artists[i]}" for i in range(len(songs))]
    return combined_song_artist