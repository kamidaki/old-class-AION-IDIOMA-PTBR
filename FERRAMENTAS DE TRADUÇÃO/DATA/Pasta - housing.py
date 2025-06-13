import os
import re
import asyncio
import aiohttp
from datetime import datetime

#------------------------------
# CONFIGURAÇÕES
#------------------------------
DIR_ORIGEM = r"F:\Servidor Aion\housing"
DIR_DESTINO = r"F:\Servidor Aion\housing\traduzidos"
FORMATO = 'utf-16'
FILES = ["lbox_default.xml", "lbox_sample.xml"]

# Patterns a proteger (placeholders, quebras de linha)
PADROES_PROTEGER = [
    r'%\d*\.\d*f',    # formatos %1.2f
    r'%\w+',          # %s, %d, etc
    r'{\d+}',         # {0}, {1}, etc
    r'\$\w+',         # $VAR
    r'\[[^\]]+\]',    # [kvalue:…], [pos:…], etc
    r'\\n'            # quebras de linha literais
]
SPLIT_REGEX = re.compile('(' + '|'.join(PADROES_PROTEGER) + ')')

async def traduzir_google(session: aiohttp.ClientSession, texto: str)-> str:
    """
    Usa o Google Translate (interface mobile) para traduzir um trecho de texto.
    """
    await asyncio.sleep(0.6)
    texto_esc = aiohttp.helpers.quote(texto, safe='')
    url = f"https://translate.google.com/m?sl=auto&tl=pt&q={texto_esc}"
    async with session.get(url, headers={'User-Agent':'Mozilla/5.0'}) as resp:
        html = await resp.text()
        m = re.search(r'class="result-container">(.*?)<', html)
        return m.group(1) if m else texto

async def traduzir_segmentos(session: aiohttp.ClientSession, text: str)-> str:
    """
    Divide 'text' em pedaços, protege placeholders, traduz só o que precisa e recompõe.
    """
    parts = SPLIT_REGEX.split(text)
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        if any(re.fullmatch(pat, part, flags=re.IGNORECASE) for pat in PADROES_PROTEGER):
            continue
        parts[i] = await traduzir_google(session, part)
    return ''.join(parts)

async def traduzir_tag(raw_text: str, tag: str, session: aiohttp.ClientSession)-> str:
    """
    Traduz o conteúdo de CDATA dentro de <tag><![CDATA[...]]></tag>.
    """
    pattern = re.compile(
        rf'(<{tag}><!\[CDATA\[)(.*?)(\]\]></{tag}>)',
        flags=re.DOTALL
    )
    pos = 0
    result = []
    for m in pattern.finditer(raw_text):
        result.append(raw_text[pos:m.start()])
        prefix, conteudo, suffix = m.groups()
        novo = await traduzir_segmentos(session, conteudo)
        result.append(prefix + novo + suffix)
        pos = m.end()
    result.append(raw_text[pos:])
    return ''.join(result)

async def traduzir_script_comments(session: aiohttp.ClientSession, raw_text: str)-> str:
    """
    Traduz apenas os comentários (linhas iniciadas com '--') dentro de <script><![CDATA[...]]></script>.
    Mantém o restante do script intacto.
    """
    pattern = re.compile(
        r'(<script><!\[CDATA\[)(.*?)(\]\]></script>)',
        flags=re.DOTALL
    )
    pos = 0
    result = []
    for m in pattern.finditer(raw_text):
        result.append(raw_text[pos:m.start()])
        prefix, conteudo, suffix = m.groups()
        # processa cada linha do script
        linhas = conteudo.split('\n')
        traduzidas = []
        for linha in linhas:
            if re.match(r'\s*--', linha):
                # separa prefixo de comentário
                pm = re.match(r'^(\s*--\s?)(.*)$', linha)
                pre = pm.group(1)
                texto = pm.group(2)
                traduzido = await traduzir_segmentos(session, texto)
                traduzidas.append(pre + traduzido)
            else:
                traduzidas.append(linha)
        novo_conteudo = '\n'.join(traduzidas)
        result.append(prefix + novo_conteudo + suffix)
        pos = m.end()
    result.append(raw_text[pos:])
    return ''.join(result)

async def process_file(session: aiohttp.ClientSession, filename: str):
    path_in = os.path.join(DIR_ORIGEM, filename)
    path_out = os.path.join(DIR_DESTINO, filename)
    os.makedirs(os.path.dirname(path_out), exist_ok=True)

    raw = open(path_in, encoding=FORMATO).read()

    inicio = datetime.now()
    print(f"Iniciando tradução de {filename}...")

    # traduz <name> e <desc>
    traduzido = await traduzir_tag(raw, "name", session)
    traduzido = await traduzir_tag(traduzido, "desc", session)
    # traduz comentários em <script>
    traduzido = await traduzir_script_comments(session, traduzido)

    with open(path_out, 'w', encoding=FORMATO) as f:
        f.write(traduzido)

    print(f"✅ {filename} traduzido e salvo em {path_out} ({datetime.now()-inicio})")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [process_file(session, fn) for fn in FILES]
        await asyncio.gather(*tasks)
    print("🎉 Todos os arquivos foram traduzidos.")

if __name__ == '__main__':
    asyncio.run(main())
