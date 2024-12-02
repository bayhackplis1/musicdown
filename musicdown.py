import yt_dlp as youtube_dl
from pathlib import Path
import os
import json
import re

# Ruta del archivo de configuración
CONFIG_PATH = Path.home() / ".cancion_downloader_config.json"

def mostrar_titulo():
    """Muestra el banner estilo hacker."""
    print("\033[92m" + "=" * 50)
    print("            CANCIÓN DOWNLOADER v2.0")
    print("          (Powered by yt-dlp & Python)")
    print("=" * 50 + "\033[0m")

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
    print("\033[93mRuta de descarga actual: \033[0m", config["download_path"])
    respuesta = input("\033[94m¿Deseas cambiar la ruta? (s/n): \033[0m").strip().lower()
    if respuesta == "s":
        ruta = input("\033[94mIngresa la nueva ruta de descarga: \033[0m").strip()
        if ruta:
            config["download_path"] = str(Path(ruta).expanduser())
            guardar_configuracion(config)
    return Path(config["download_path"])

def mostrar_resultados(resultados):
    """Muestra los resultados de búsqueda al usuario."""
    print("\n\033[92mResultados encontrados:\033[0m")
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
        print(f"\n\033[92mDescarga completa: {d['filename']}\033[0m")

def descargar_cancion():
    mostrar_titulo()
    config = cargar_configuracion()
    salida = obtener_ruta_descarga(config)
    salida.mkdir(parents=True, exist_ok=True)

    print("\n\033[93mSelecciona un modo:\033[0m")
    print("[1] Buscar por nombre")
    print("[2] Ingresar enlace directo")
    modo = input("\033[94mElige una opción (1 o 2): \033[0m").strip()

    if modo == "1":
        busqueda = input("\033[94mIngresa el nombre de la canción o video: \033[0m").strip()
        if not busqueda:
            print("\033[91mError: La búsqueda no puede estar vacía.\033[0m")
            return
    elif modo == "2":
        busqueda = input("\033[94mIngresa el enlace directo: \033[0m").strip()
        if not busqueda:
            print("\033[91mError: El enlace no puede estar vacío.\033[0m")
            return
    else:
        print("\033[91mOpción inválida.\033[0m")
        return

    formato = input("\033[94m¿Formato de descarga (mp3/mp4)? \033[0m").strip().lower()
    if formato not in ["mp3", "mp4"]:
        print("\033[91mError: Formato no reconocido.\033[0m")
        return

    ydl_opts = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
        'postprocessors': [({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': config['quality'],
        })] if formato == 'mp3' else [],
        'outtmpl': str(salida / '%(title)s.%(ext)s'),
        'progress_hooks': [hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            if modo == "1":
                resultados = ydl.extract_info(f"ytsearch{config['search_limit']}:{busqueda}", download=False)
                if 'entries' in resultados and len(resultados['entries']) > 0:
                    mostrar_resultados(resultados)
                    seleccion = input("\033[94mSelecciona los videos a descargar (separados por comas): \033[0m").strip()
                    indices = [int(x) - 1 for x in seleccion.split(",") if x.strip().isdigit()]
                    for i in indices:
                        video = resultados['entries'][i]
                        title = video['title']
                        if verificar_archivo_existente(salida, title, formato):
                            print(f"\033[93mSaltando {title}: ya existe.\033[0m")
                            continue
                        ydl.download([video['webpage_url']])
                else:
                    print("\033[91mNo se encontraron resultados.\033[0m")
            else:
                ydl.download([busqueda])
            print("\033[92mDescargas completadas con éxito.\033[0m")
        except Exception as e:
            print(f"\033[91mError: {e}\033[0m")

if __name__ == "__main__":
    descargar_cancion()
