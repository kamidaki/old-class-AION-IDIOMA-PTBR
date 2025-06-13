import os
import zipfile

# Pastas base
base_organizacao = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT - CLIENT FILES\SOUNDS - EDIT\TRADUZIDOS - VOZ SUAVE 02\npc\ORGANIZAÇÃO"
base_para_traduzir = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT - CLIENT FILES\SOUNDS - EDIT\TRADUZIDOS - VOZ SUAVE 02\Z - CONVERTIDOS FINAL\npc"
saida_zip = base_para_traduzir  # Mesmo local para salvar os .zip

# Processa cada pasta npc 1 a npc 6
for i in range(1, 7):
    nome_pasta = f"npc {i}"
    pasta_origem = os.path.join(base_organizacao, nome_pasta)
    nome_zip = f"sound_npc_{i}.zip"
    caminho_zip = os.path.join(saida_zip, nome_zip)

    arquivos_para_zipar = []

    # Verifica se a pasta existe
    if not os.path.isdir(pasta_origem):
        print(f"[AVISO] Pasta não encontrada: {pasta_origem}")
        continue

    # Lista os arquivos na pasta npc i
    for nome_arquivo in os.listdir(pasta_origem):
        caminho_arquivo = os.path.join(base_para_traduzir, nome_arquivo)
        if os.path.isfile(caminho_arquivo):
            arquivos_para_zipar.append(caminho_arquivo)
        else:
            print(f"[ERRO] Arquivo não encontrado em PARA TRADUZIR: {nome_arquivo}")

    # Cria o ZIP com os arquivos encontrados
    if arquivos_para_zipar:
        with zipfile.ZipFile(caminho_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file_path in arquivos_para_zipar:
                arcname = os.path.basename(file_path)  # Nome dentro do zip
                zipf.write(file_path, arcname)
                print(f"[OK] Adicionado ao {nome_zip}: {arcname}")
        print(f"[✓] ZIP criado: {caminho_zip}\n")
    else:
        print(f"[X] Nenhum arquivo válido para zipar em {nome_pasta}\n")

print("Processo concluído.")
