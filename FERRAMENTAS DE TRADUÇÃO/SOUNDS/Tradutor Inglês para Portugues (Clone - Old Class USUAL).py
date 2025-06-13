import os
import subprocess
import tempfile
import time
import whisper
from deep_translator import GoogleTranslator
from TTS.api import TTS

# Ajusta o PATH para incluir a pasta do FFmpeg
os.environ["PATH"] += os.pathsep + r"E:\Programas instalados- Leves\ffmpeg-2025-06-08-git-5fea5e3e11-essentials_build\bin"

# Diretórios
INPUT_DIR = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\SOUNDS- EDIT\PARA TRADUZIR"
OUTPUT_DIR = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\SOUNDS- EDIT\TRADUZIDOS- VOZ HUMANA"

# Inicializa Whisper e Tradutor
whisper_model = whisper.load_model("base")
translator = GoogleTranslator(source="en", target="pt")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

# Lista de speakers disponíveis no modelo
speakers_list = [s.strip() for s in tts.speakers if s.strip()]
print("[INFO] Lista de speakers disponíveis:", speakers_list)

# Função para detectar gênero ou monstro
def detect_gender_or_monster(filename):
    f = filename.lower()
    if "female" in f or "woman" in f:
        return "female"
    elif "male" in f or "man" in f:
        return "male"
    elif "monster" in f or "beast" in f:
        return "monster"
    return "neutral"

# Escolher speaker por gênero
def choose_speaker(gender):
    for s in speakers_list:
        if gender == "female" and "female" in s:
            return s
        elif gender == "male" and "male" in s:
            return s
    return speakers_list[0]  # fallback para o primeiro disponível

def ffmpeg_convert(input_file, output_file, extra_args=None):
    cmd = ["ffmpeg", "-y", "-i", input_file]
    if extra_args:
        cmd += extra_args
    cmd.append(output_file)
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def process_file(src_file, dst_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1) Conversão WAV mono 16kHz
        wav_path = os.path.join(tmpdir, "input.wav")
        ffmpeg_convert(src_file, wav_path, ["-ar", "16000", "-ac", "1", "-vn"])

        # 2) Transcrição
        result = whisper_model.transcribe(wav_path, language="en", task="transcribe", temperature=0.2)
        text_en = result["text"].strip()
        print(f"[INFO] Texto original: {text_en}")

        # 3) Tradução
        text_pt = translator.translate(text_en)
        print(f"[INFO] Tradução: {text_pt}")
        time.sleep(1)

        # 4) Detectar gênero ou monstro
        gender = detect_gender_or_monster(os.path.basename(src_file))
        print(f"[INFO] Detecção: {gender}")

        # 5) Síntese de voz Coqui TTS
        wav_tts_path = os.path.join(tmpdir, "tts.wav")
        if gender != "monster":
            speaker = choose_speaker(gender)
            print(f"[INFO] Usando speaker: {speaker}")
            tts.tts_to_file(text=text_pt, file_path=wav_tts_path, language="pt-br", speaker=speaker)
        else:
            # Se for monstro, gera voz masculina normal e depois aplica efeito
            speaker = choose_speaker("male")
            tts.tts_to_file(text=text_pt, file_path=wav_tts_path, language="pt-br", speaker=speaker)

        # 6) Ajuste final: naturalidade e fluidez
        wav_adj_path = os.path.join(tmpdir, "adjusted.wav")
        if gender == "monster":
            # Efeito de voz monstruosa
            ffmpeg_convert(
                wav_tts_path,
                wav_adj_path,
               [
                    "-af",
                    (
                        "afftdn=nf=-25, "
                        "asetrate=44100*0.2, atempo=1.45, "
                        "bass=g=10, "
                        "aecho=0.8:0.88:1000:0.3, "
                        "aresample=44100"
                    )
                ]
            )
        else:
            # Voz natural: sem asetrate, apenas atempo e equalização
            ffmpeg_convert(
                wav_tts_path,
                wav_adj_path,
               [
                    "-af",
                    (
                        "afftdn=nf=-25, "
                        "acompressor=threshold=-15dB:ratio=2:attack=10:release=50, "
                        "equalizer=f=300:t=q:w=1:g=1.5, "
                        "atempo=1.25, "  # Pequeno ajuste de velocidade (fluidez)
                        "aresample=44100"
                    )
                ]
            )

        # 7) Conversão final para OGG
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        ffmpeg_convert(wav_adj_path, dst_file, ["-c:a", "libopus", "-b:a", "160k"])

        print(f"[✅] Finalizado: {os.path.basename(dst_file)}")


def main():
    print("[INFO] Iniciando conversão...")
    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.lower().endswith((".ogg", ".mp4", ".wav", ".mp3")):
                src = os.path.join(root, file)
                rel = os.path.relpath(root, INPUT_DIR)
                dst = os.path.join(OUTPUT_DIR, rel, os.path.splitext(file)[0] + ".ogg")
                try:
                    process_file(src, dst)
                    time.sleep(1)
                except Exception as e:
                    print(f"[ERRO] {src}: {str(e)}")

if __name__ == "__main__":
    main()
