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
        # Si hay un error de valor, significa que la fecha no era válida.
        return False

def main():
    """
    Función principal que ejecuta el programa. Gestiona la autenticación de Spotify, 
    obtiene la lista de canciones de Billboard y crea la playlist en Spotify.
    """
    # Inicializar el gestor de Spotify
    spotify_manager = SpotifyManager()

    while True:
        # Pedir al usuario que ingrese una fecha
        week_date = input("Enter the date you want to check (YYYY-MM-DD): ")

        # Comprobar si la fecha ingresada es válida
        if is_valid_date(week_date):
            # Obtener la lista de canciones de Billboard para la fecha dada
            song_artist_list = fetch_songs_from_billboard(week_date)

            if song_artist_list:
                # Obtener el ID de usuario de Spotify del usuario actual
                user_id = spotify_manager.sp.current_user()["id"]

                # Crear una playlist en Spotify con las canciones obtenidas
                spotify_manager.create_spotify_playlist(user_id, week_date, song_artist_list)

                # Notificar al usuario que la playlist fue creada
                print(f"Playlist created for date {week_date}")
            else:
                # Notificar al usuario que no se encontraron canciones para la fecha dada
                print("No songs found for the given date. Please check the date and try again.")

            # Salir del bucle después de procesar una fecha válida
            break
        else:
            # Notificar al usuario que la fecha ingresada es inválida
            print("Invalid date or format. Please enter a valid date in YYYY-MM-DD format and make sure it's not in the future.")

# Comprobar si el script se está ejecutando directamente
if __name__ == "__main__":
    # Si es así, ejecutar la función main
    main()
