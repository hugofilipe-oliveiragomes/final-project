import pandas as pd
import re
import fitz

def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        full_text += page.get_text()
    pdf_document.close()
    return full_text

def extrair_info_completa_refinada(texto):
    indices_diploma = [m.start() for m in re.finditer("Diploma", texto)]
    if len(indices_diploma) < 2:
        raise ValueError("A palavra 'Diploma' não apareceu duas vezes.")

    texto_apos_segundo_diploma = texto[indices_diploma[1]:]

    padrao_geral = re.compile(
        r"(Livro\s+([IVXLCDM]+)|Título\s+([IVXLCDM]+)|Capítulo\s+([IVXLCDM]+)|Seção\s+(\d+)|Artigo\s+(\d+\.?[A-Z]?))\.?([^:]*?):?\s*(.*?)\n",
        re.DOTALL
    )

    dados = {
        "Livro": [], "Número do Livro": [],
        "Título": [], "Número do Título": [],
        "Capítulo": [], "Número do Capítulo": [],
        "Seção": [], "Número da Seção": [],
        "Número do Artigo": [],
        "Título do Artigo": [],
        "Conteúdo do Artigo": []
    }

    current_book = current_title = current_chapter = current_section = "Não especificado"
    current_num_book = current_num_title = current_num_chapter = current_num_section = "Não especificado"

    for match in padrao_geral.finditer(texto_apos_segundo_diploma):
        kind, num_livro, num_titulo, num_capitulo, num_secao, num_artigo, title, content = match.groups()

        content = content.strip().replace("\n", " ")

        if "Livro" in kind:
            current_book, current_num_book = content, num_livro
        elif "Título" in kind:
            current_title, current_num_title = content, num_titulo
        elif "Capítulo" in kind:
            current_chapter, current_num_chapter = content, num_capitulo
        elif "Seção" in kind:
            current_section, current_num_section = content, num_secao
        
        if "Artigo" in kind:
            dados["Número do Artigo"].append(num_artigo)
            dados["Título do Artigo"].append(title.strip())
            dados["Conteúdo do Artigo"].append(content)
            dados["Livro"].append(current_book)
            dados["Número do Livro"].append(current_num_book)
            dados["Título"].append(current_title)
            dados["Número do Título"].append(current_num_title)
            dados["Capítulo"].append(current_chapter)
            dados["Número do Capítulo"].append(current_num_chapter)
            dados["Seção"].append(current_section)
            dados["Número da Seção"].append(current_num_section)

    df = pd.DataFrame(dados)
    return df

def extrair_artigos_apos_segundo_diploma(texto):
    indices_diploma = [m.start() for m in re.finditer("Diploma", texto)]
    if len(indices_diploma) < 2:
        raise ValueError("A palavra 'Diploma' não apareceu duas vezes.")
    
    texto_apos_segundo_diploma = texto[indices_diploma[1]:]
    
    padrao_artigos = re.compile(r"Artigo\s+(\d+\.º(?:-[A-Za-z]+)?)(.*?)(?=\nArtigo\s+\d+\.º|\Z)", re.DOTALL)
    
    matches = padrao_artigos.finditer(texto_apos_segundo_diploma)
    
    artigos = [{'Número do Artigo': match.group(1), 'Conteúdo do Artigo': match.group(2).strip()}
               for match in matches]
   
    return artigos
def processar_dataframe(df):
    df['Tipo de Artigo'] = ['Diploma' if i <= 22 else 'Código Civil' for i in df.index]

    # Substituindo 'Não especificado' por 'Sem informação' em 'Livro', 'Título' e 'Capítulo'
    df.loc[:22, 'Livro'] = df.loc[:23, 'Livro'].replace('Não especificado', 'Sem informação')
    df.loc[:22, 'Título'] = df.loc[:23, 'Título'].replace('Não especificado', 'Sem informação')
    df.loc[:22, 'Capítulo'] = df.loc[:23, 'Capítulo'].replace('Não especificado', 'Sem informação')
    
    return df
    
def extrair_titulo_e_limpar_conteudo(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Não é um DataFrame.")

    if 'Título do Artigo' not in df.columns:
        df['Título do Artigo'] = None
    
    for i, row in df.iterrows():
        conteudo = str(row['Conteúdo do Artigo'])
        
        titulo_entre_parenteses = re.search(r'\((.*?)\)', conteudo)
        if titulo_entre_parenteses:
            titulo = titulo_entre_parenteses.group(1)
            conteudo_limpo = re.sub(re.escape(titulo_entre_parenteses.group(0)), '', conteudo).strip()
        else:
            titulo, _, restante = conteudo.partition('\n')
            conteudo_limpo = restante.strip()

        df.at[i, 'Título do Artigo'] = titulo.strip()
        df.at[i, 'Conteúdo do Artigo'] = conteudo_limpo

    return df
    
def ajustar_titulos_conteudos(texto):
    padrao_artigo = re.compile(r"Artigo\s+(\d+\.?[A-Z]?º?)\s*-\s*(.*?)\n(\d+)", re.DOTALL)
    artigos = []
    for num_artigo, titulo, conteudo_inicial in padrao_artigo.findall(texto):
        if re.match(r"Norma\s", titulo):
            titulo_limpo = titulo
        else:
            titulo_limpo = None
            conteudo_inicial = f"{titulo}\n{conteudo_inicial}"

        artigos.append({
            "Número do Artigo": num_artigo.strip(),
            "Título do Artigo": titulo_limpo.strip() if titulo_limpo else "Não Especificado",
            "Conteúdo do Artigo": conteudo_inicial.strip()
        })
    
    return artigos

def identificar_secao(numeros_artigos):
    secao_atual = 1
    for i, num_artigo in enumerate(numeros_artigos):
        if num_artigo == '1':
            secao_atual += 1
        numeros_artigos[i] = (secao_atual, num_artigo)
        
    return numeros_artigos