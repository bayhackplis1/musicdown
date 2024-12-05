import yt_dlp as youtube_dl
from pathlib import Path
import os
import json
import re
import time
from random import choice
from mutagen.easyid3 import EasyID3

# Ruta del archivo de configuración
CONFIG_PATH = Path.home() / ".cancion_downloader_config.json"

# Colores ANSI
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BLINK = "\033[5m"

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
        "             ANTUAN DOWNLOADER v2.0"
    ]
    border = MAGENTA + "=" * 60 + RESET
    print(border)
    for line in lines:
        print(choice([GREEN, BLUE, YELLOW, CYAN]) + line.center(60) + RESET)
    print(border)

def hacker_menu():
    """Muestra un menú principal con un diseño visual dinámico."""
    options = [
        "[1] 🔍 Buscar por nombre",
        "[2] 🔗 Ingresar enlace directo",
        "[3] 📜 Descargar lista de reproducción",
        "[4] ⚙️  Configuración de descarga",
        "[5] 🎵 Seleccionar formato (MP3/MP4)",
        "[6] ❌ Salir"
    ]

    print(f"\n{MAGENTA}{BLINK}Bienvenido, selecciona una opción:{RESET}\n")
    border = CYAN + "-" * 60 + RESET
    print(border)

    for option in options:
        print(choice([GREEN, YELLOW, MAGENTA, CYAN]) + option.center(60) + RESET)

    print(border)

def hacker_cargando(mensaje):
    """Simula un mensaje de carga estilo hacker."""
    print(YELLOW + mensaje, end="")
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print(RESET)

def cargar_configuracion():
    """Carga la configuración guardada o asegura valores predeterminados."""
    default_config = {
        'download_path': str(Path.home() / "Music" / "Downloads"),
        'quality': '192',
        'search_limit': 10,
        'format': 'mp3'  # Valor predeterminado
    }
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, 'r') as config_file:
            user_config = json.load(config_file)
            return {**default_config, **user_config}
    return default_config

def guardar_configuracion(config):
    """Guarda la configuración en un archivo JSON."""
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config, config_file)

def obtener_ruta_descarga(config):
    """Permite al usuario especificar la ruta de descarga o usar la predeterminada."""
    print(GREEN + "Ruta de descarga actual: " + RESET, config["download_path"])
    respuesta = input(YELLOW + "¿Deseas cambiar la ruta? (si/no): " + RESET).strip().lower()
    if respuesta == "si":
        ruta = input(BLUE + "Ingresa la nueva ruta de descarga: " + RESET).strip()
        if ruta:
            config["download_path"] = str(Path(ruta).expanduser())
            guardar_configuracion(config)
    return Path(config["download_path"])

def mostrar_resultados(resultados):
    """Muestra los resultados de búsqueda al usuario."""
    print("\n" + GREEN + "Resultados encontrados:" + RESET)
    for i, entry in enumerate(resultados['entries']):
        duracion = entry.get("duration", "??")
        duracion = f"{duracion // 60}:{duracion % 60:02d}" if isinstance(duracion, int) else "??:??"
        print(f"[{i + 1}] {entry['title']} | Duración: {duracion} | Autor: {entry.get('uploader', 'Desconocido')}")

def agregar_metadatos(archivo, metadatos):
    """Agrega etiquetas ID3 a un archivo MP3."""
    try:
        audio = EasyID3(archivo)
        for clave, valor in metadatos.items():
            audio[clave] = valor
        audio.save()
        print(f"{GREEN}Metadatos añadidos a {archivo}{RESET}")
    except Exception as e:
        print(f"{RED}Error al agregar metadatos: {e}{RESET}")

def hook(d):
    """Proporciona información sobre el progreso de la descarga."""
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        print(f"Descargando: {percent:.2f}% completado", end="\r")
    elif d['status'] == 'finished':
        print(f"\n{GREEN}Descarga completa: {d['filename']}{RESET}")

def seleccionar_formato(config):
    """Permite al usuario seleccionar entre formato MP3 o MP4."""
    print(BLUE + "Formato actual: " + RESET, config["format"].upper())
    print(YELLOW + "Opciones disponibles: MP3, MP4" + RESET)
    nuevo_formato = input(BLUE + "Selecciona el nuevo formato: " + RESET).strip().lower()
    if nuevo_formato in ["mp3", "mp4"]:
        config["format"] = nuevo_formato
        guardar_configuracion(config)
        print(GREEN + f"Formato cambiado a {nuevo_formato.upper()} correctamente." + RESET)
    else:
        print(RED + "Formato inválido. No se realizaron cambios." + RESET)

def descargar_cancion():
    hacker_titulo()
    config = cargar_configuracion()
    salida = obtener_ruta_descarga(config)
    salida.mkdir(parents=True, exist_ok=True)

    while True:
        hacker_menu()
        opcion = input(GREEN + "Elige una opción: " + RESET).strip()

        if opcion == "1":
            # Lógica de búsqueda por nombre
            busqueda = input(BLUE + "Ingresa el nombre de la canción o video: " + RESET).strip()
            if not busqueda:
                print(RED + "Error: La búsqueda no puede estar vacía." + RESET)
                continue

            hacker_cargando("Buscando canciones")
            ydl_opts = {
                'format': 'bestaudio/best' if config["format"] == "mp3" else 'bestvideo+bestaudio',
                'noplaylist': True,
                'outtmpl': str(salida / f'%(title)s.{"mp3" if config["format"] == "mp3" else "mp4"}'),
                'progress_hooks': [hook]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                resultados = ydl.extract_info(f"ytsearch{config['search_limit']}:{busqueda}", download=False)
                if 'entries' in resultados and len(resultados['entries']) > 0:
                    mostrar_resultados(resultados)
                    seleccion = input(BLUE + "Selecciona los videos a descargar (separados por comas): " + RESET).strip()
                    indices = [int(x) - 1 for x in seleccion.split(",") if x.strip().isdigit()]
                    for i in indices:
                        video = resultados['entries'][i]
                        ydl.download([video['webpage_url']])
                else:
                    print(RED + "No se encontraron resultados." + RESET)

        elif opcion == "2":
            # Lógica para descargar desde enlace directo
            enlace = input(BLUE + "Ingresa el enlace directo: " + RESET).strip()
            if not enlace:
                print(RED + "Error: El enlace no puede estar vacío." + RESET)
                continue
            hacker_cargando("Iniciando descarga")
            ydl_opts = {
                'format': 'bestaudio/best' if config["format"] == "mp3" else 'bestvideo+bestaudio',
                'outtmpl': str(salida / f'%(title)s.{"mp3" if config["format"] == "mp3" else "mp4"}'),
                'progress_hooks': [hook]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([enlace])

        elif opcion == "3":
            # Lógica para listas de reproducción
            enlace = input(BLUE + "Ingresa el enlace de la lista de reproducción: " + RESET).strip()
            hacker_cargando("Descargando lista de reproducción")
            ydl_opts = {
                'format': 'bestaudio/best' if config["format"] == "mp3" else 'bestvideo+bestaudio',
                'outtmpl': str(salida / f'%(playlist_title)s/%(title)s.{"mp3" if config["format"] == "mp3" else "mp4"}'),
                'progress_hooks': [hook],
                'noplaylist': False
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([enlace])

        elif opcion == "4":
            # Configuración de descarga
            salida = obtener_ruta_descarga(config)

        elif opcion == "5":
            # Selección de formato
            seleccionar_formato(config)

        elif opcion == "6":
            # Salir del programa
            print(MAGENTA + "¡Gracias por usar el downloader! Hasta luego." + RESET)
            break

        else:
            print(RED + "Opción inválida. Por favor, intenta de nuevo." + RESET)

# Inicia la aplicación
if __name__ == "__main__":
    descargar_cancion()
