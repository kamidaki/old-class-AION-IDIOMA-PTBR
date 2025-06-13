import os
import re
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Comment
from datetime import datetime
from html import unescape

#------------------------------
# CONFIGURAÇÕES GLOBAIS
#------------------------------
DIR_ORIGEM   = r"F:\Servidor Aion\ui"
DIR_DESTINO  = r"F:\Servidor Aion\ui\traduzidos"
FORMATO      = 'utf-16'

PADROES_PROTEGER = [
    r'%\d*\.\d*f', r'%\w+', r'{\d+}', r'\$\w+',
    r'\[\%[^\]]+\]', r'\[[^\]]+\]', r'\\n'
]
SPLIT_REGEX = re.compile('(' + '|'.join(PADROES_PROTEGER) + ')')

async def traduzir_google(session: aiohttp.ClientSession, texto: str)-> str:
    await asyncio.sleep(0.6)
    q   = aiohttp.helpers.quote(texto, safe='')
    url = f"https://translate.google.com/m?sl=auto&tl=pt&q={q}"
    async with session.get(url, headers={'User-Agent':'Mozilla/5.0'}) as resp:
        html = await resp.text()
        m = re.search(r'class="result-container">(.*?)<', html)
        return m.group(1) if m else texto

async def traduzir_segmentos(texto: str, session: aiohttp.ClientSession)-> str:
    parts = SPLIT_REGEX.split(texto)
    for i, p in enumerate(parts):
        if p.strip() and not any(re.fullmatch(pat, p, re.IGNORECASE) for pat in PADROES_PROTEGER):
            parts[i] = await traduzir_google(session, p)
    return ''.join(parts)

async def process_xml(session: aiohttp.ClientSession, raw: str)-> str:
    # só traduz <desc>…
    raw = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', raw)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.fromstring(raw, parser=parser)

    for desc in root.findall('.//desc'):
        if desc.text and desc.text.strip():
            traduzido = await traduzir_segmentos(desc.text, session)
            desc.text = traduzido

    return unescape(ET.tostring(root, encoding='unicode'))

async def process_html_cdata(session: aiohttp.ClientSession, raw: str)-> str:
    pattern = re.compile(
        r'(<Contents\s+cdata="true">\s*<!\[CDATA\[)(.*?)(\]\]>\s*</Contents>)',
        re.DOTALL
    )
    out, last = [], 0
    for m in pattern.finditer(raw):
        out.append(raw[last:m.start()])
        prefix, inner, suffix = m.groups()
        soup = BeautifulSoup(inner, 'html.parser')
        for node in soup.find_all(string=True):
            if isinstance(node, Comment) or node.parent.name in ['script','style']:
                continue
            txt = str(node)
            if txt.strip():
                new = await traduzir_segmentos(txt, session)
                node.replace_with(new)
        out.append(prefix + str(soup) + suffix)
        last = m.end()
    out.append(raw[last:])
    return ''.join(out)

async def process_file(session: aiohttp.ClientSession, path_in: str, path_out: str):
    rel = os.path.relpath(path_in, DIR_ORIGEM)
    print(f"\nIniciando: {rel}")
    inicio = datetime.now()

    raw = open(path_in, encoding=FORMATO).read()
    ext = os.path.splitext(path_in)[1].lower()

    if ext == '.xml':
        result = await process_xml(session, raw)
    else:  # .html
        result = await process_html_cdata(session, raw)

    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    with open(path_out, 'w', encoding=FORMATO) as f:
        f.write(result)

    print(f"✅ Salvo: {rel} (tempo: {datetime.now()-inicio})")

async def main():
    async with aiohttp.ClientSession() as session:
        for raiz, _, arquivos in os.walk(DIR_ORIGEM):
            for arq in sorted(arquivos):
                if not arq.lower().endswith(('.xml','.html')):
                    continue
                in_p  = os.path.join(raiz, arq)
                out_p = os.path.join(DIR_DESTINO, os.path.relpath(in_p, DIR_ORIGEM))
                await process_file(session, in_p, out_p)
    print("\n🎉 Todas as traduções concluídas.")

if __name__ == '__main__':
    asyncio.run(main())
