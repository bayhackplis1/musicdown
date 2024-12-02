import yt_dlp as youtube_dl
from pathlib import Path
import sys

def validar_entrada(busqueda):
    """Valida que la entrada no esté vacía o contenga solo espacios."""
    return bool(busqueda.strip())

def obtener_ruta_descarga():
    """Permite al usuario especificar la ruta de descarga o usar la predeterminada."""
    respuesta = input("¿Quieres usar la ruta de descarga predeterminada? (s/n): ")
    if respuesta.lower() == 'n':
        ruta = input("Ingresa la ruta completa de la carpeta donde deseas guardar las canciones: ")
        return Path(ruta).expanduser()
    return Path.home() / "Music" / "MEmu Music"

def descargar_cancion():
    salida = obtener_ruta_descarga()
    salida.mkdir(parents=True, exist_ok=True)  # Crear la ruta si no existe

    busqueda = input("Ingresa el nombre de la canción que deseas descargar: ")
    
    # Validar entrada
    if not validar_entrada(busqueda):
        print("La búsqueda no puede estar vacía.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': str(salida / '%(title)s.%(ext)s'),  # Ruta de salida
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Buscar y extraer información de la primera entrada
            resultados = ydl.extract_info(f"ytsearch1:{busqueda}", download=False)
            if 'entries' in resultados and len(resultados['entries']) > 0:
                cancion = resultados['entries'][0]
                url = cancion['webpage_url']
                print(f"Descargando: {cancion['title']}")
                ydl.download([url])
                print("Canción descargada con éxito.")
            else:
                print("No se encontraron resultados.")
        except youtube_dl.DownloadError:
            print("Error al descargar la canción. Verifica la conexión o el nombre de la canción.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

# Llama a la función para iniciar la descarga
if __name__ == "__main__":
    descargar_cancion()
