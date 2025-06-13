import os
import re
import xml.etree.ElementTree as ET
import asyncio
import aiohttp
import time
from datetime import datetime
from html import unescape

#------------------------------
# CONFIGURAÇÕES GLOBAIS
#------------------------------
DIR_ORIGEM = r"F:\Servidor Aion\housing"
DIR_DESTINO_BASE = r"F:\Servidor Aion\housing\traduzidos"
FORMATO = 'utf-16'
# Patterns a proteger (placeholders, quebras de linha)
PADROES_PROTEGER = [r'%\d*\.\d*f', r'%\w+', r'{\d+}', r'\$\w+', r'\[%[^\]]+\]', r'\\n']
# Regex para split em partes de texto (mantém \n e placeholders)
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
    r'\bhttps://oldclassaion.com/doacao/\b': 'https://aionclassicbrasil.com/oldclass/doacao/',
    r'\bSoldier, Rank\b': 'Soldado, Posto',
    r'\bPandaemonium\b': 'Pandaemonium',
    r'\bStrike Resist\b': 'Resistência ao ataque',
    r'\bSanctum\b': 'Santuário Elyos',
    r'\bIshalgen\b': 'Ishalgen',
    r'\bDeputy\b': 'Segundo Mestre de Guilda',
    r'\bLevel\b': 'Nível',
    r'\bhttps://oldclassaion.com/loja/\b': 'https://aionclassicbrasil.com/oldclass/loja/',
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
    r'\bhttps://oldclassaion.com/loja/;Aion Shop\b': 'https://aionclassicbrasil.com/oldclass/loja/;Loja Old Class',
    r'\bEltnen\b': 'Eltnen',
    r'\bTheobomos\b': 'Theobomos',
    r'\bVerteron\b': 'Verteron',
}

async def traduzir(session: aiohttp.ClientSession, texto: str)-> str:
    await asyncio.sleep(0.6)
    texto_esc = aiohttp.helpers.quote(texto, safe='')
    url = f"https://translate.google.com/m?sl=auto&tl=pt&q={texto_esc}"
    async with session.get(url, headers={'User-Agent':'Mozilla/5.0'}) as resp:
        html = await resp.text()
        m = re.search(r'class="result-container">(.*?)<', html)
        return m.group(1) if m else texto

async def process_file(session: aiohttp.ClientSession, caminho_in: str, caminho_out: str):
    rel = os.path.relpath(caminho_in, DIR_ORIGEM)
    print(f"\n=== Iniciando tradução do arquivo: {rel} ===")
    inicio = datetime.now()

    # prepara diretório de saída e log
    out_dir = os.path.dirname(caminho_out)
    os.makedirs(out_dir, exist_ok=True)
    log_file = os.path.splitext(caminho_out)[0] + '.log'
    processed = set()
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding=FORMATO) as f:
            processed = {line.strip() for line in f if line.strip()}

    # carrega e parseia XML
    raw = open(caminho_in, encoding=FORMATO).read()
    raw = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', raw)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.fromstring(raw, parser=parser)

    # coleta segmentos a traduzir
    entries = []
    for idx, elem in enumerate(root.findall('.//string')):
        body = elem.find('body')
        if body is None or not body.text:
            continue
        parts = SPLIT_REGEX.split(body.text)
        needs = [(i, part) for i, part in enumerate(parts)
                 if part.strip() and not any(re.fullmatch(p, part, flags=re.IGNORECASE) for p in PADROES_PROTEGER)]
        entries.append({'body': body, 'parts': parts, 'needs': needs})

    total = sum(len(e ['needs']) for e in entries)
    count = len(processed)
    print(f"Total de segmentos a traduzir: {total}")

    # traduz e registra
    for entry_idx, entry in enumerate(entries):
        for part_idx, text in entry['needs']:
            key = f"{entry_idx}:{part_idx}"
            if key in processed:
                continue
            while True:
                try:
                    trad = await traduzir(session, text)
                    entry['parts'][part_idx] = trad
                    with open(log_file, 'a', encoding=FORMATO) as lf:
                        lf.write(key + '\n')
                    processed.add(key)
                    count += 1
                    print(f"[{count}/{total}] Traduzido segmento {key}")
                    break
                except Exception as e:
                    print(f"❌ Erro ao traduzir {key}: {e}. Retry em 10s...")
                    await asyncio.sleep(10)

    # aplica traduções e substituições estritas
    for entry in entries:
        texto_trad = ''.join(entry['parts'])
        for pat, repl in STRICT_MAP.items():
            texto_trad = re.sub(pat, repl, texto_trad)
        entry['body'].text = texto_trad

    # salva XML
    with open(caminho_out, 'w', encoding=FORMATO) as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(unescape(ET.tostring(root, encoding='unicode')))

    print(f"✅ Arquivo salvo: {caminho_out} ({datetime.now()- inicio})")

async def main():
    start = datetime.now()
    async with aiohttp.ClientSession() as session:
        for raiz, _, files in os.walk(DIR_ORIGEM):
            for file in sorted(files):
                if not file.lower().endswith('.xml'):
                    continue
                caminho_in = os.path.join(raiz, file)
                rel = os.path.relpath(caminho_in, DIR_ORIGEM)
                caminho_out = os.path.join(DIR_DESTINO_BASE, rel)
                await process_file(session, caminho_in, caminho_out)
    print(f"\n🎉 Todas as traduções concluídas em {datetime.now()- start}")

if __name__ == '__main__':
    asyncio.run(main())
