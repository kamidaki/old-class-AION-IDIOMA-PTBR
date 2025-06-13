import os
from pydub import AudioSegment

# Caminhos
PASTA_ORIGEM = r"F:\OBS - VIDEOS\MP3\ATAQUES\ogg\FINAL\ULTIMA CONVERSAO\ULTIMA CONVERSAO"
PASTA_DESTINO = os.path.join(PASTA_ORIGEM, "F:\OBS - VIDEOS\MP3\ATAQUES\ogg\AQ")

# Defina o caminho do ffmpeg.exe se necessário
AudioSegment.converter = r"E:\Programas instalados - Leves\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\bin\ffmpeg.exe"

# Conta quantos arquivos foram processados
total_convertidos = 0
total_erros = 0

for raiz, _, arquivos in os.walk(PASTA_ORIGEM):
    for nome_arquivo in arquivos:
        if nome_arquivo.lower().endswith(".ogg"):
            caminho_ogg = os.path.join(raiz, nome_arquivo)

            # Define o caminho de saída equivalente
            caminho_relativo = os.path.relpath(caminho_ogg, PASTA_ORIGEM)
            caminho_saida = os.path.join(PASTA_DESTINO, caminho_relativo)

            # Garante que a pasta de destino exista
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

            try:
                audio = AudioSegment.from_ogg(caminho_ogg)

                # Aumenta o volume em +6 dB (ajuste conforme necessário)
                audio = audio.apply_gain(4)
                audio.export(
                    caminho_saida,
                    format="ogg",
                    parameters=["-ac", "1", "-ar", "44100", "-c:a", "libvorbis"]
                )
                total_convertidos += 1
                print(f"[✓] Convertido: {caminho_relativo}")
            except Exception as e:
                total_erros += 1
                print(f"[ERRO] Falha ao converter {caminho_relativo}: {e}")

print(f"\nConversão concluída. Total convertidos: {total_convertidos}, erros: {total_erros}")
