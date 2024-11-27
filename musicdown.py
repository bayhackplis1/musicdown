import yt_dlp as youtube_dl
import os

def descargar_cancion():
    busqueda = input("Ingresa el nombre de la canción que deseas descargar: ")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': r'C:\Users\User\Music\MEmu Music\%(title)s.%(ext)s',  # Ruta de salida
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Buscar y extraer información de la primera entrada
            resultados = ydl.extract_info(f"ytsearch1:{busqueda}", download=False)
            if 'entries' in resultados:
                cancion = resultados['entries'][0]
                url = cancion['webpage_url']
                print(f"Descargando: {cancion['title']}")
                ydl.download([url])
                print("Canción descargada con éxito.")
            else:
                print("No se encontraron resultados.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

# Llama a la función para iniciar la descarga
descargar_cancion()