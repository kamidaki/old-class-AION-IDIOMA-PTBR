import os
from pydub import AudioSegment
from pathlib import Path

# Configuração do FFmpeg (ajuste o caminho conforme necessário)
os.environ["PATH"] += os.pathsep + r"E:\Programas instalados- Leves\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\bin"

# Pasta de origem (onde estão os MP3)
origem = r"F:\OBS- VIDEOS\MP3"

def converter_mp3_para_ogg(arquivo_mp3, arquivo_ogg):
    try:
        # Carrega o arquivo MP3
        audio = AudioSegment.from_mp3(arquivo_mp3)

        # Configurações para OGG de boa qualidade
        audio.export(
            arquivo_ogg,
            format="ogg",
            codec="libopus",
            bitrate="160k",
            parameters=["-application", "audio"]  # Otimizado para voz/áudio
        )
        return True
    except Exception as e:
        print(f"Erro ao converter {arquivo_mp3}: {str(e)}")
        return False

def main():
    print("Iniciando conversão de MP3 para OGG...")

    # Contadores para relatório
    total_arquivos = 0
    convertidos = 0
    falhas = 0

    for root, _, files in os.walk(origem):
        for file in files:
            if file.lower().endswith('.mp3'):
                total_arquivos += 1
                mp3_path = os.path.join(root, file)
                ogg_path = os.path.join(root, os.path.splitext(file)[0] + '.ogg')

                # Verifica se o OGG já existe
                if os.path.exists(ogg_path):
                    print(f"Pulando {file}- OGG já existe")
                    continue

                print(f"Convertendo: {file}")
                if converter_mp3_para_ogg(mp3_path, ogg_path):
                    convertidos += 1
                else:
                    falhas += 1

    print("\nRelatório de conversão:")
    print(f"Total de arquivos MP3 encontrados: {total_arquivos}")
    print(f"Arquivos convertidos para OGG: {convertidos}")
    print(f"Falhas na conversão: {falhas}")

if __name__ == "__main__":
    main()