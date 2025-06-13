import os
from pydub import AudioSegment

# Caminhos
PASTA_ORIGEM = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT - CLIENT FILES\SOUNDS - EDIT\Z - convertidos para MP3\cutscene\df2a\voice"
PASTA_DESTINO = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT - CLIENT FILES\SOUNDS - EDIT\TRADUZIDOS - VOZ SUAVE 02\cutscene\df2a\voice"

# Garante que a pasta destino exista
os.makedirs(PASTA_DESTINO, exist_ok=True)

# Lista os arquivos existentes em ambas as pastas (sem extensão)
nomes_origem = {os.path.splitext(f)[0].lower(): f for f in os.listdir(PASTA_ORIGEM) if f.lower().endswith(".mp3")}
nomes_destino = {os.path.splitext(f)[0].lower() for f in os.listdir(PASTA_DESTINO) if f.lower().endswith(".ogg")}

# Arquivos que existem na origem mas não estão na pasta destino
faltando = [nome for nome in nomes_origem if nome not in nomes_destino]

print(f"Total de arquivos faltando: {len(faltando)}\n")

for nome_base in faltando:
    mp3_filename = nomes_origem[nome_base]
    mp3_path = os.path.join(PASTA_ORIGEM, mp3_filename)
    ogg_path = os.path.join(PASTA_DESTINO, f"{nome_base}.ogg")

    try:
        AudioSegment.converter = r"E:\Programas instalados - Leves\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\bin\ffmpeg.exe"
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(ogg_path, format="ogg")
        print(f"[✓] Convertido: {mp3_filename} → {nome_base}.ogg")
    except Exception as e:
        print(f"[ERRO] Falha ao converter {mp3_filename}: {e}")

print("\nProcesso concluído.")
