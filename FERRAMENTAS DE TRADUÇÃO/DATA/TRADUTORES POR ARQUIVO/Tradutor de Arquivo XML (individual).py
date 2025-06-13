import os
import re
import xml.etree.ElementTree as ET
import asyncio
import aiohttp
import time
from datetime import datetime
from html import unescape
from aiohttp import ClientTimeout
from aiohttp.helpers import quote

# CONFIG
DIR_ORIGEM = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\DATA_PAK\ULTIMO OLD CLASS FUNCIONAL\strings\PARA TRADUZIR"
FILE_TO_TRANSLATE = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\DATA_PAK\ULTIMO OLD CLASS FUNCIONAL\strings\PARA TRADUZIR\client_strings_item3.xml"
DIR_DESTINO_BASE = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT- CLIENT FILES\DATA_PAK\EDIT _TRANSLATE_PTBR\strings\TESTE"
FORMATO = 'utf-16'
PADROES_PROTEGER = [r'%\d*\.\d*f', r'%\w+', r'{\d+}', r'\$\w+', r'\[%[^\]]+\]', r'\\n']
SPLIT_REGEX = re.compile(r'(\\n|\[%[^\]]+\])')
# Mapeamento absoluto de termos
STRICT_MAP = {
    r'\bDagger\b': 'Adaga',
    r'\bLivro de Feitiço\b': 'Livro Mágico',
    r'\bSpellbook\b': 'Livro Mágico',
    r'\bAetherTech\b': 'Tecnologia Éter',
    r'\bAether\b': 'Éter',
    r'\bVIP\b': 'ULTIMATE',
    r'\bAION Shop\b': 'Loja Old Class',
    r'\bRank\b': 'Posto',
    r'\bShop AION\b': 'Loja Old Class',
    r'\bWeb Shop\b': 'Loja Old Class',
    r'\bCrucible\b': 'Crisol',
    r'\bCaracteres\b': 'Personagens',
    r'\bCaracter\b': 'Personagem',
    r'\bcharacter\b': 'Personagem',
    r'\bcharacters\b': 'Personagens',
    r'\bGuilda\b': 'Guilda',
    r'\bLegion\b': 'Guilda',
    r'\bpack\b': 'Pacote',
    r'\bGeneral da Brigada\b': 'Mestre de Guilda',
    r'\bStringTable_MSG.xls\b': 'StringTable_MSG.xls',
    r'\bQuickBar\b': 'Barra de Acesso Rápido',
    r'https://oldclassaion\.com/doacao/': 'https://aionclassicbrasil.com/oldclass/doacao/',
    r'\bSoldier, Rank\b': 'Soldado, Posto',
    r'\bPandaemonium\b': 'Pandaemonium',
    r'\bStrike Resist\b': 'Resistência ao ataque',
    r'\bSanctum\b': 'Santuário Elyos',
    r'\bIshalgen\b': 'Ishalgen',
    r'\bDeputy\b': 'Segundo Mestre de Guilda',
    r'\bLevel\b': 'Nível',
    r'https://oldclassaion\.com/loja/': 'https://aionclassicbrasil.com/oldclass/loja/',
    r'\bDark Star\b': 'Estrela Negra',
    r'\bCadinho\b': 'Crisol',
    r'\bEmpyrean\b': 'Empíreo',
    r'\bAbyss Gate\b': 'Portão do Abismo',
    r'\bToken\b': 'Ficha',
    r'\bTokens\b': 'Fichas',
    r'\bGryphu\b': 'Grifo',
    r'\bGryphus\b': 'Grifos',
    r'\ba Tear\b': 'Uma Máquina de Tecelagem',
    r'\buma Tear\b': 'Uma Máquina de Tecelagem',
    r'\bthis Tear\b': 'essa Máquina de Tecelagem',
    r'\bSiel Greatsword\b': 'Espada Grande de Siel',
    r'\bGreatsword\b': 'Espada Grande',
    r'\bHeiron\b': 'Heiron',
    r'https://oldclassaion\.com/loja/;Aion Shop': 'https://aionclassicbrasil.com/oldclass/loja/;Loja Old Class',
    r'\bEltnen\b': 'Eltnen',
    r'\bTheobomos\b': 'Theobomos',
    r'\bVerteron\b': 'Verteron',
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'}

async def traduzir(session, texto, cache):
    if texto in cache:
        return cache[texto]

    url = f"https://translate.google.com/m?sl=auto&tl=pt&q={quote(texto, safe='')}"
    for _ in range(3):
        try:
            async with session.get(url, headers=HEADERS, timeout=ClientTimeout(total=10)) as resp:
                html = await resp.text()
                m = re.search(r'class="result-container">(.*?)<', html)
                trad = m.group(1) if m else texto
                cache[texto] = trad
                return trad  # 👈 só usa a variável trad
        except Exception as e:
            await asyncio.sleep(3)
    print(f"❌ Falha ao traduzir: {texto[:30]}...")
    return texto


async def traduzir_concorrente(session, tasks, semaforo):
    """
    Controla concorrência de traduções.
    """
    async with semaforo:
        idx, text, entry, part_idx, log_file, cache = tasks  # 👈 agora 6 valores
        trad = await traduzir(session, text, cache)
        entry['parts'][part_idx] = trad
        with open(log_file, 'a', encoding=FORMATO) as lf:
            lf.write(f"{idx}:{part_idx}\n")
        print(f"✔️ Traduzido [{idx}:{part_idx}]")
        return

async def process_file(session, caminho_in, caminho_out):
    cache = {}  # Cache em memória para esta execução
    rel = os.path.relpath(caminho_in, DIR_ORIGEM)
    print(f"\n=== Iniciando: {rel} ===")
    inicio = datetime.now()
    out_dir = os.path.dirname(caminho_out)
    os.makedirs(out_dir, exist_ok=True)
    log_file = os.path.splitext(caminho_out)[0] + '.log'
    processed = set()
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding=FORMATO) as f:
            processed = {line.strip() for line in f if line.strip()}

    raw = open(caminho_in, encoding=FORMATO).read()
    raw = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', raw)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.fromstring(raw, parser=parser)

    entries = []
    tasks = []
    for idx, elem in enumerate(root.findall('.//string')):
        body = elem.find('body')
        if body is None or not body.text:
            continue
        parts = SPLIT_REGEX.split(body.text)
        needs = [(i, part) for i, part in enumerate(parts)
                 if part.strip() and not any(re.fullmatch(p, part, flags=re.IGNORECASE) for p in PADROES_PROTEGER)]
        entries.append({'body': body, 'parts': parts, 'needs': needs})

    total = sum(len(e ['needs']) for e in entries)
    print(f"Total a traduzir: {total}")

    semaforo = asyncio.Semaphore(10)  # até 10 traduções em paralelo
    for entry_idx, entry in enumerate(entries):
        for part_idx, text in entry['needs']:
            key = f"{entry_idx}:{part_idx}"
            if key not in processed:
                tasks.append((entry_idx, text, entry, part_idx, log_file, cache))

    # Cria tarefas concorrentes
    await asyncio.gather(*(traduzir_concorrente(session, t, semaforo) for t in tasks))

    # Aplicar substituições estritas
    for entry in entries:
        texto_trad = ''.join(entry['parts'])
        for pat, repl in STRICT_MAP.items():
            texto_trad = re.sub(pat, repl, texto_trad)
        entry['body'].text = texto_trad

    # Salvar XML final
    with open(caminho_out, 'w', encoding=FORMATO) as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(unescape(ET.tostring(root, encoding='unicode')))
    print(f"✅ Salvo: {caminho_out} ({datetime.now()- inicio})")

async def main():
    caminho_in = FILE_TO_TRANSLATE
    caminho_out = os.path.join(DIR_DESTINO_BASE, os.path.relpath(caminho_in, DIR_ORIGEM))
    async with aiohttp.ClientSession() as session:
        await process_file(session, caminho_in, caminho_out)
    print("\n🎉 Tradução concluída!")

if __name__ == '__main__':
    asyncio.run(main())
