import os
import subprocess
import tempfile
import time  # Importante para o delay!

# 1) Ajuste o PATH para incluir a pasta do FFmpeg:
os.environ["PATH"] += os.pathsep + r"E:\Programas instalados- Leves\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\bin"

import whisper
from deep_translator import GoogleTranslator
translator = GoogleTranslator(source='en', target='pt')
from gtts import gTTS

# Diretórios (ajuste conforme necessário)
INPUT_DIR       = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\SOUNDS- EDIT\PARA TRADUZIR- VOZ SUAVE 02"
OUTPUT_BASE_DIR = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\SOUNDS- EDIT\TRADUZIDOS- VOZ SUAVE 02"

# Carrega o modelo Whisper
model = whisper.load_model("base")

def ffmpeg_convert(input_path: str, output_path: str, extra_args: list = None):
    cmd = ["ffmpeg", "-y", "-i", input_path]
    if extra_args:
        cmd += extra_args
    cmd.append(output_path)
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def adjust_speech_rate_and_pitch(input_path, output_path, speed=1.32, pitch=0.63): # Reduzindo a velocidade e subindo o tom
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-af", f"atempo={speed},asetrate=44100*{pitch},aresample=44100",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def improve_voice_effect(input_path, output_path):
    # Ajusta graves, equalização e compressão para uma voz mais calma e sem eco.
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-af", "equalizer=f=500:width_type=h:width=200:g=1.5, "  # Realça médios para clareza (levemente)
               "equalizer=f=200:width_type=h:width=100:g=1, "    # Reforça graves suaves (mais leve)
               "compand=attacks=0.3:decays=0.6:points=-90/-90|-60/-60|-30/-27|-20/-18|-10/-7|0/-3|20/0, "  # Compressão para uniformidade
               "highpass=f=80, "      # Remove frequências muito baixas (roncos e ruídos)
               "lowpass=f=7000"          # Atenua altas frequências (sibilância e aspereza)
        ,output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def process_file(src_path: str, dst_path: str):
    with tempfile.TemporaryDirectory() as tmp:
        # 1) WAV temporário
        wav_path = os.path.join(tmp, "audio.wav")
        ffmpeg_convert(src_path, wav_path, extra_args=["-ar", "16000", "-ac", "1", "-vn"])

        # 2) Whisper
        res = model.transcribe(wav_path, language="en", task="transcribe", temperature=0.2)
        texto_en = res["text"].strip()

        # 3) Tradução (delay adicionado!)
        texto_pt = translator.translate(texto_en)
        time.sleep(2)  # Aguarda 2 segundos após a tradução

        # 4) Síntese TTS (delay adicionado!)
        mp3_path = os.path.join(tmp, "audio.mp3")
        tts = gTTS(text=texto_pt, lang="pt")
        tts.save(mp3_path)
        time.sleep(2)  # Aguarda 2 segundos após salvar o TTS

        # 5) Ajustar velocidade e tom
        adjusted_mp3_path = os.path.join(tmp, "audio_adjusted.mp3")
        adjust_speech_rate_and_pitch(mp3_path, adjusted_mp3_path, speed=1.32, pitch=0.63)

        # 6) Melhorar naturalidade com equalização e eco
        improved_audio_path = os.path.join(tmp, "audio_improved.mp3")
        improve_voice_effect(adjusted_mp3_path, improved_audio_path)

        # 7) MP3 → OGG opus
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        ffmpeg_convert(improved_audio_path, dst_path, extra_args=["-c:a", "libopus", "-b:a", "160k"])

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
                    time.sleep(5)  # Delay geral entre áudios para evitar sobrecarga!
                except Exception as e:
                    print(f"[ERRO] {src}: {e}")

if __name__ == "__main__":
    main()