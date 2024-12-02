import yt_dlp as youtube_dl
from pathlib import Path
import os
import json
import re

# Ruta del archivo de configuración
CONFIG_PATH = Path.home() / ".cancion_downloader_config.json"

def cargar_configuracion():
    """Carga la configuración guardada, si existe, y asegura valores predeterminados."""
    default_config = {'download_path': str(Path.home() / "Music" / "MEmu Music"), 'quality': '192', 'search_limit': 10}
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, 'r') as config_file:
            user_config = json.load(config_file)
            # Asegura que existan todas las claves predeterminadas
            for key, value in default_config.items():
                if key not in user_config:
                    user_config[key] = value
                    guardar_configuracion(user_config)
            return user_config
    return default_config

def guardar_configuracion(config):
    """Guarda la configuración en un archivo JSON."""
    try:
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(config, config_file)
    except IOError as e:
        print(f"Error al guardar la configuración: {e}")

def validar_entrada(busqueda):
    """Valida que la entrada no esté vacía o contenga solo espacios."""
    return bool(busqueda.strip())

def obtener_ruta_descarga(config):
    """Permite al usuario especificar la ruta de descarga o usar la predeterminada."""
    respuesta = input("¿Quieres usar la ruta de descarga predeterminada? (s/n): ")
    if respuesta.lower() == 'n':
        ruta = input("Ingresa la ruta completa de la carpeta donde deseas guardar los archivos: ")
        config['download_path'] = str(Path(ruta).expanduser())
        guardar_configuracion(config)
    return Path(config['download_path'])

def mostrar_resultados(resultados):
    """Muestra los resultados de búsqueda al usuario."""
    print("Resultados encontrados:")
    for i, entry in enumerate(resultados['entries']):
        print(f"{i + 1}: {entry['title']}")

def verificar_archivo_existente(salida, title, ext):
    """Verifica si el archivo ya existe en la ruta de salida."""
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)  # Limpia caracteres no válidos
    return Path(salida / f"{safe_title}.{ext}").is_file()

def hook(d):
    """Proporciona información sobre el progreso de la descarga."""
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        print(f"Descargando: {percent:.2f}% completado", end="\r")
    elif d['status'] == 'finished':
        print(f"\nDescarga completa: {d['filename']}")

def descargar_cancion():
    config = cargar_configuracion()
    salida = obtener_ruta_descarga(config)
    salida.mkdir(parents=True, exist_ok=True)

    # Elegir modo de entrada
    modo = input("¿Deseas buscar por nombre (1) o ingresar un enlace directo (2)? Ingresa 1 o 2: ")
    if modo == '1':
        busqueda = input("Ingresa el nombre de la canción o video que deseas descargar: ")
        if not validar_entrada(busqueda):
            print("La búsqueda no puede estar vacía.")
            return
    elif modo == '2':
        busqueda = input("Ingresa el enlace directo del video: ")
        if not validar_entrada(busqueda):
            print("El enlace no puede estar vacío.")
            return
    else:
        print("Opción inválida. Inténtalo de nuevo.")
        return

    # Elegir formato
    formato = input("¿Qué formato deseas descargar? Ingresa 'mp3' o 'mp4': ").lower()
    if formato not in ['mp3', 'mp4']:
        print("Formato inválido. Inténtalo de nuevo.")
        return

    ydl_opts = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': config['quality'],
        }] if formato == 'mp3' else [],
        'outtmpl': str(salida / '%(title)s.%(ext)s'),
        'progress_hooks': [hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            if modo == '1':
                resultados = ydl.extract_info(f"ytsearch{config['search_limit']}:{busqueda}", download=False)
                if 'entries' in resultados and len(resultados['entries']) > 0:
                    mostrar_resultados(resultados)

                    seleccion = input("Ingresa los números de los videos que deseas descargar (separados por comas): ")
                    try:
                        indices = [int(num.strip()) - 1 for num in seleccion.split(",") if num.strip().isdigit()]
                        if any(i < 0 or i >= len(resultados['entries']) for i in indices):
                            raise ValueError("Índice fuera de rango")
                    except ValueError:
                        print("Entrada inválida. Inténtalo de nuevo.")
                        return

                    for i in indices:
                        video = resultados['entries'][i]
                        title = video['title']
                        if verificar_archivo_existente(salida, title, formato):
                            respuesta = input(f"El archivo '{title}.{formato}' ya existe. ¿Deseas reemplazarlo? (s/n): ")
                            if respuesta.lower() == 'n':
                                print(f"Saltar descarga de '{title}'.")
                                continue

                        url = video['webpage_url']
                        print(f"Descargando: {title}")
                        ydl.download([url])
                else:
                    print("No se encontraron resultados.")
            else:
                # Descargar directamente desde el enlace
                ydl.download([busqueda])

            print("Descargas completadas con éxito.")
        except youtube_dl.DownloadError:
            print("Error al descargar. Verifica el enlace o tu conexión a internet.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    descargar_cancion()
