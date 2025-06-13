import os
import subprocess
import tempfile

# 1) Ajuste o PATH para incluir a pasta do FFmpeg:
os.environ["PATH"] += os.pathsep + r"E:\Programas instalados- Leves\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\bin"

import whisper
from deep_translator import GoogleTranslator
translator = GoogleTranslator(source='en', target='pt')
from gtts import gTTS

# Diretórios (ajuste conforme necessário)
INPUT_DIR       = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\SOUNDS- EDIT\PARA TRADUZIR"
OUTPUT_BASE_DIR = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\SOUNDS- EDIT\TRADUZIDOS"

# Carrega o modelo Whisper (escolha "base", "small", "tiny" etc. para equilibrar velocidade vs. qualidade)
model = whisper.load_model("base")

def ffmpeg_convert(input_path: str, output_path: str, extra_args: list = None):
    """Chama ffmpeg para converter um arquivo."""
    cmd = ["ffmpeg", "-y", "-i", input_path]
    if extra_args:
        cmd += extra_args
    cmd.append(output_path)
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def process_file(src_path: str, dst_path: str):
    """
    Pipeline:
      1) extrai áudio → WAV mono 16kHz
      2) Whisper transcribe
      3) traduz texto
      4) gTTS sintetiza para MP3
      5) ffmpeg converte MP3 → OGG opus
    """
    with tempfile.TemporaryDirectory() as tmp:
        # 1) WAV temporário
        wav_path = os.path.join(tmp, "audio.wav")
        ffmpeg_convert(src_path, wav_path, extra_args=["-ar", "16000", "-ac", "1", "-vn"])

        # 2) Whisper
        res = model.transcribe(wav_path, language="en", task="transcribe")
        texto_en = res["text"].strip()

        # 3) Tradução
        texto_pt = translator.translate(texto_en)

        # 4) Síntese TTS
        mp3_path = os.path.join(tmp, "audio.mp3")
        tts = gTTS(text=texto_pt, lang="pt")
        tts.save(mp3_path)

        # 5) MP3 → OGG opus
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        ffmpeg_convert(mp3_path, dst_path, extra_args=["-c:a", "libopus", "-b:a", "128k"])

        print(f"[OK] {os.path.basename(src_path)} → {os.path.basename(dst_path)}")

def main():
    for root, _, files in os.walk(INPUT_DIR):
        for fn in files:
            if fn.lower().endswith((".ogg", ".mp4")):
                src = os.path.join(root, fn)
                rel = os.path.relpath(root, INPUT_DIR)
                base = os.path.splitext(fn)[0] + ".ogg"
                dst = os.path.join(OUTPUT_BASE_DIR, rel, base)
                try:
                    process_file(src, dst)
                except Exception as e:
                    print(f"[ERRO] {src}: {e}")

if __name__ == "__main__":
    main()
