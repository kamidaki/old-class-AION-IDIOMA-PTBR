import os
import shutil

# Caminhos
PASTA_NEW = r"F:\OBS - VIDEOS\MP3\ATAQUES\ogg"
PASTA_SYSTEM = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT - CLIENT FILES\SOUNDS - EDIT\TRADUZIDOS - PASTAS ISOLADAS\system"
PASTA_FINAL = r"F:\OBS - VIDEOS\MP3\ATAQUES\ogg\FINAL"

# Cria a pasta FINAL se não existir
os.makedirs(PASTA_FINAL, exist_ok=True)

# Processa apenas arquivos que começam com New_ e terminam com .ogg
for file in os.listdir(PASTA_NEW):
    if file.lower().startswith("new_") and file.lower().endswith(".ogg"):
        base_name = file[4:-4]  # remove "New_" e ".ogg"
        new_path = os.path.join(PASTA_NEW, file)

        # Procura todos os arquivos no system que comecem com o mesmo nome base
        for system_file in os.listdir(PASTA_SYSTEM):
            if system_file.lower().startswith(base_name.lower()) and system_file.lower().endswith(".ogg"):
                # Caminho do novo arquivo a ser salvo
                final_path = os.path.join(PASTA_FINAL, system_file)
                # Copia o áudio do NEW com o nome do arquivo de produção
                shutil.copyfile(new_path, final_path)
                print(f"[OK] Copiado: {file} → {system_file}")

print("\nConcluído.")
