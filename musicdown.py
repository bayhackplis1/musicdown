import yt_dlp as youtube_dl
from pathlib import Path
import os
import json
import re
import time
from random import choice

# Ruta del archivo de configuración
CONFIG_PATH = Path.home() / ".cancion_downloader_config.json"

# Colores ANSI
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# Funciones de diseño
def hacker_titulo():
    """Muestra un banner estilo hacker."""
    lines = [
         " █████╗ ███╗   ██╗████████╗██╗   ██╗ █████╗ ███╗   ██╗",
        "██╔══██╗████╗  ██║╚══██╔══╝██║   ██║██╔══██╗████╗  ██║",
        "███████║██╔██╗ ██║   ██║   ██║   ██║███████║██╔██╗ ██║",
        "██╔══██║██║╚██╗██║   ██║   ██║   ██║██╔══██║██║╚██╗██║",
        "██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║  ██║██║ ╚████║",
        "╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝",
         "                ANTUAN Downloader"
    ]
    print(GREEN + "=" * 60 + RESET)
    for line in lines:
        print(choice([GREEN, BLUE, YELLOW]) + line.center(60) + RESET)
    print(GREEN + "=" * 60 + RESET)

def hacker_menu():
    """Muestra un menú principal con estilo."""
    options = [
        "[1] Buscar por nombre",
        "[2] Ingresar enlace directo",
        "[3] Salir"
    ]
    print(BLUE + "\nSelecciona una opción:\n" + RESET)
    for option in options:
        print(choice([GREEN, BLUE, YELLOW]) + option.center(60) + RESET)
    print()

def hacker_cargando(mensaje):
    """Simula un mensaje de carga estilo hacker."""
    print(YELLOW + mensaje, end="")
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print(RESET)

def cargar_configuracion():
    """Carga la configuración guardada, si existe, y asegura valores predeterminados."""
    default_config = {'download_path': str(Path.home() / "Music" / "MEmu Music"), 'quality': '192', 'search_limit': 10}
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, 'r') as config_file:
            user_config = json.load(config_file)
            for key, value in default_config.items():
                if key not in user_config:
                    user_config[key] = value
                    guardar_configuracion(user_config)
            return user_config
    return default_config

def guardar_configuracion(config):
    """Guarda la configuración en un archivo JSON."""
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config, config_file)

def obtener_ruta_descarga(config):
    """Permite al usuario especificar la ruta de descarga o usar la predeterminada."""
    print(GREEN + "Ruta de descarga actual: " + RESET, config["download_path"])
    respuesta = input(YELLOW + "¿Deseas cambiar la ruta? (si/no): " + RESET).strip().lower()
    if respuesta == "s":
        ruta = input(BLUE + "Ingresa la nueva ruta de descarga: " + RESET).strip()
        if ruta:
            config["download_path"] = str(Path(ruta).expanduser())
            guardar_configuracion(config)
    return Path(config["download_path"])

def obtener_formato():
    """Permite al usuario seleccionar un formato de salida."""
    formatos = ["mp3", "mp4"]
    print("\nFormatos disponibles:")
    for i, formato in enumerate(formatos, 1):
        print(f"[{i}] {formato}")
    seleccion = input(YELLOW + "Selecciona un formato: " + RESET).strip()
    if seleccion.isdigit() and 1 <= int(seleccion) <= len(formatos):
        return formatos[int(seleccion) - 1]
    print(RED + "Selección inválida, se usará mp3 por defecto." + RESET)
    return "mp3"

def mostrar_resultados(resultados):
    """Muestra los resultados de búsqueda al usuario."""
    print("\n" + GREEN + "Resultados encontrados:" + RESET)
    for i, entry in enumerate(resultados['entries']):
        duracion = entry.get("duration", "??")
        duracion = f"{duracion // 60}:{duracion % 60:02d}" if isinstance(duracion, int) else "??:??"
        print(f"[{i + 1}] {entry['title']} | Duración: {duracion} | Autor: {entry.get('uploader', 'Desconocido')}")

def verificar_archivo_existente(salida, title, ext):
    """Verifica si el archivo ya existe en la ruta de salida."""
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    return Path(salida / f"{safe_title}.{ext}").is_file()

def hook(d):
    """Proporciona información sobre el progreso de la descarga."""
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        print(f"Descargando: {percent:.2f}% completado", end="\r")
    elif d['status'] == 'finished':
        print(f"\n{GREEN}Descarga completa: {d['filename']}{RESET}")

def descargar_cancion():
    hacker_titulo()
    config = cargar_configuracion()
    salida = obtener_ruta_descarga(config)
    salida.mkdir(parents=True, exist_ok=True)
    formato = obtener_formato()

    while True:
        hacker_menu()
        opcion = input(GREEN + "Elige una opción: " + RESET).strip()

        if opcion == "1":
            busqueda = input(BLUE + "Ingresa el nombre de la canción o video: " + RESET).strip()
            if not busqueda:
                print(RED + "Error: La búsqueda no puede estar vacía." + RESET)
                continue

            hacker_cargando("Buscando canciones")
            ydl_opts = {
                'format': 'bestaudio/best' if formato == "mp3" else 'bestvideo+bestaudio',
                'outtmpl': str(salida / f'%(title)s.{formato}'),
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': config["quality"]}] if formato == "mp3" else [],
                'noplaylist': True,
                'progress_hooks': [hook]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                resultados = ydl.extract_info(f"ytsearch{config['search_limit']}:{busqueda}", download=False)
                if 'entries' in resultados and len(resultados['entries']) > 0:
                    mostrar_resultados(resultados)
                    seleccion = input(BLUE + "Selecciona los videos a descargar (separados por comas): " + RESET).strip()
                    indices = [int(x) - 1 for x in seleccion.split(",") if x.strip().isdigit() and 0 <= int(x) - 1 < len(resultados['entries'])]
                    for i in indices:
                        video = resultados['entries'][i]
                        if verificar_archivo_existente(salida, video['title'], formato):
                            print(YELLOW + f"Saltando {video['title']}: ya existe." + RESET)
                            continue
                        ydl.download([video['webpage_url']])
                else:
                    print(RED + "No se encontraron resultados." + RESET)

        elif opcion == "2":
            enlace = input(BLUE + "Ingresa el enlace directo: " + RESET).strip()
            if not enlace:
                print(RED + "Error: El enlace no puede estar vacío." + RESET)
                continue
            hacker_cargando("Iniciando descarga")
            ydl_opts = {
                'format': 'bestaudio/best' if formato == "mp3" else 'bestvideo+bestaudio',
                'outtmpl': str(salida / f'%(title)s.{formato}'),
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': config["quality"]}] if formato == "mp3" else [],
                'progress_hooks': [hook]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([enlace])

        elif opcion == "3":
            print(YELLOW + "¡Hasta luego, !" + RESET)
            break

        else:
            print(RED + "Opción inválida, intenta de nuevo." + RESET)

if __name__ == "__main__":
    descargar_cancion()
