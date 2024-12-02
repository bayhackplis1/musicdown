import yt_dlp as youtube_dl
from pathlib import Path
import os
import json

# Ruta del archivo de configuración
CONFIG_PATH = Path.home() / ".cancion_downloader_config.json"

def cargar_configuracion():
    """Carga la configuración guardada, si existe."""
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, 'r') as config_file:
            return json.load(config_file)
    return {'download_path': str(Path.home() / "Music" / "MEmu Music"), 'quality': '192'}

def guardar_configuracion(config):
    """Guarda la configuración en un archivo JSON."""
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config, config_file)

def validar_entrada(busqueda):
    """Valida que la entrada no esté vacía o contenga solo espacios."""
    return bool(busqueda.strip())

def obtener_ruta_descarga(config):
    """Permite al usuario especificar la ruta de descarga o usar la predeterminada."""
    respuesta = input("¿Quieres usar la ruta de descarga predeterminada? (s/n): ")
    if respuesta.lower() == 'n':
        ruta = input("Ingresa la ruta completa de la carpeta donde deseas guardar las canciones: ")
        config['download_path'] = str(Path(ruta).expanduser())
        guardar_configuracion(config)
    return Path(config['download_path'])

def mostrar_resultados(resultados):
    """Muestra los resultados de búsqueda al usuario."""
    print("Resultados encontrados:")
    for i, entry in enumerate(resultados['entries']):
        print(f"{i + 1}: {entry['title']}")

def verificar_archivo_existente(salida, title):
    """Verifica si el archivo ya existe en la ruta de salida."""
    return Path(salida / f"{title}.mp3").is_file()

def descargar_cancion():
    config = cargar_configuracion()
    salida = obtener_ruta_descarga(config)
    salida.mkdir(parents=True, exist_ok=True)

    busqueda = input("Ingresa el nombre de la canción que deseas descargar: ")
    
    if not validar_entrada(busqueda):
        print("La búsqueda no puede estar vacía.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': config['quality'],
        }],
        'outtmpl': str(salida / '%(title)s.%(ext)s'),
        'progress_hooks': [hook],
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            resultados = ydl.extract_info(f"ytsearch10:{busqueda}", download=False)
            if 'entries' in resultados and len(resultados['entries']) > 0:
                mostrar_resultados(resultados)

                # Permitir al usuario elegir cuáles canciones descargar
                seleccion = input("Ingresa los números de las canciones que deseas descargar (separados por comas): ")
                indices = [int(num.strip()) - 1 for num in seleccion.split(",") if num.strip().isdigit()]

                if indices:
                    for i in indices:
                        cancion = resultados['entries'][i]
                        title = cancion['title']
                        if verificar_archivo_existente(salida, title):
                            respuesta = input(f"El archivo '{title}.mp3' ya existe. ¿Deseas reemplazarlo? (s/n): ")
                            if respuesta.lower() == 'n':
                                print(f"Saltar descarga de '{title}'.")
                                continue

                        url = cancion['webpage_url']
                        print(f"Descargando: {title}")
                        ydl.download([url])
                    print("Descargas completadas con éxito.")
                else:
                    print("No se seleccionó ninguna canción válida.")
            else:
                print("No se encontraron resultados.")
        except youtube_dl.DownloadError:
            print("Error al descargar la canción. Verifica la conexión o el nombre de la canción.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

def hook(d):
    """Proporciona información sobre el progreso de la descarga."""
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        print(f"Descargando: {percent:.2f}% completado")
    elif d['status'] == 'finished':
        print(f"Descarga completa: {d['filename']}")

if __name__ == "__main__":
    descargar_cancion()
