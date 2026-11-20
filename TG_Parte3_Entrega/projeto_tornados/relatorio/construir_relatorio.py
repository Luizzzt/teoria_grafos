"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: geração do relatório acadêmico em DOCX a partir do modelo fornecido.
Histórico: 28/09/2026 - Codex - criação do gerador do relatório completo da Parte 2.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image as PillowImage


RAIZ = Path(__file__).resolve().parents[1]
MODELO = Path(r"C:\Users\Alexandre\Downloads\projetoTG_parte2_templateRelatorio.docx")
SAIDA = RAIZ / "relatorio" / "relatorio_projeto_tornados.docx"
EVIDENCIAS = RAIZ / "testes" / "evidencias"


def calcular_tamanho_imagem(
    largura_px: int, altura_px: int, largura_max_cm: float, altura_max_cm: float
) -> tuple[float, float]:
    escala = min(largura_max_cm / largura_px, altura_max_cm / altura_px)
    return largura_px * escala, altura_px * escala


def limpar_corpo(documento: Document) -> None:
    corpo = documento._element.body
    for elemento in list(corpo):
        if elemento.tag != qn("w:sectPr"):
            corpo.remove(elemento)


def _substituir_texto_preservando_runs(paragrafo, antigo: str, novo: str) -> None:
    for run in paragrafo.runs:
        if antigo in run.text:
            run.text = run.text.replace(antigo, novo)


def _preencher_celula_existente(celula, texto: str) -> None:
    paragrafo = celula.paragraphs[0]
    if paragrafo.runs:
        paragrafo.runs[0].text = texto
        for run in paragrafo.runs[1:]:
            run.text = ""
    elif texto:
        paragrafo.add_run(texto)


def preparar_template(documento: Document) -> None:
    """Preserva a abertura e a tabela originais, preenchendo apenas seus campos."""
    for paragrafo in documento.paragraphs:
        if "Parte 1" in paragrafo.text:
            _substituir_texto_preservando_runs(paragrafo, "Parte 1", "Parte 2")

    tabela_integrantes = documento.tables[0]
    valores = [
        ["Nome do Integrante", "RA"],
        ["Alexandre Toledo Ponton Yerovi", "10426978"],
        ["Luiz Fernando Ferrari Batistela", "10427397"],
        ["", ""],
    ]
    for linha, conteudo in zip(tabela_integrantes.rows, valores):
        for celula, texto in zip(linha.cells, conteudo):
            _preencher_celula_existente(celula, texto)

    marcador_relatorio = next(
        paragrafo for paragrafo in documento.paragraphs if paragrafo.text.strip() == "Relatório"
    )
    corpo = documento._element.body
    encontrou_marcador = False
    for elemento in list(corpo):
        if elemento is marcador_relatorio._p:
            encontrou_marcador = True
            continue
        if encontrou_marcador and elemento.tag != qn("w:sectPr"):
            corpo.remove(elemento)


def definir_fonte(run, tamanho: float = 11, negrito: bool = False) -> None:
    run.font.name = "Arial"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    run.font.size = Pt(tamanho)
    run.font.bold = negrito
    run.font.color.rgb = RGBColor(0, 0, 0)


def configurar_estilos(documento: Document) -> None:
    estilos = documento.styles
    normal = estilos["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    normal.font.size = Pt(11)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)

    nomes_existentes = {estilo.name for estilo in estilos}
    for nivel, (nome, tamanho, espaco) in enumerate(
        (("Heading 1", 15, 12), ("Heading 2", 13, 9), ("Heading 3", 11, 6)), start=1
    ):
        if nome in nomes_existentes:
            estilo = estilos[nome]
        else:
            estilo = estilos.add_style(nome, WD_STYLE_TYPE.PARAGRAPH)
            estilo.base_style = normal
            p_pr = estilo.element.get_or_add_pPr()
            nivel_xml = OxmlElement("w:outlineLvl")
            nivel_xml.set(qn("w:val"), str(nivel - 1))
            p_pr.append(nivel_xml)
        estilo.font.name = "Arial"
        estilo._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        estilo.font.size = Pt(tamanho)
        estilo.font.bold = True
        estilo.font.color.rgb = RGBColor(0, 0, 0)
        estilo.paragraph_format.space_before = Pt(espaco)
        estilo.paragraph_format.space_after = Pt(6)
        estilo.paragraph_format.keep_with_next = True

    if "Legenda" not in [s.name for s in estilos]:
        legenda = estilos.add_style("Legenda", WD_STYLE_TYPE.PARAGRAPH)
    else:
        legenda = estilos["Legenda"]
    legenda.font.name = "Arial"
    legenda._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    legenda.font.size = Pt(9)
    legenda.font.italic = True
    legenda.font.color.rgb = RGBColor(0, 0, 0)
    legenda.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    legenda.paragraph_format.space_after = Pt(8)

    if "List Bullet" not in {s.name for s in estilos}:
        lista = estilos.add_style("List Bullet", WD_STYLE_TYPE.PARAGRAPH)
        lista.base_style = normal
        lista.font.name = "Arial"
        lista._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        lista.font.size = Pt(11)


def adicionar_campo(paragrafo, instrucao: str, texto_padrao: str = "") -> None:
    run = paragrafo.add_run()
    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    codigo = OxmlElement("w:instrText")
    codigo.set(qn("xml:space"), "preserve")
    codigo.text = instrucao
    separador = OxmlElement("w:fldChar")
    separador.set(qn("w:fldCharType"), "separate")
    run._r.extend([inicio, codigo, separador])
    if texto_padrao:
        texto = paragrafo.add_run(texto_padrao)
        definir_fonte(texto, 10)
    fim_run = paragrafo.add_run()
    fim = OxmlElement("w:fldChar")
    fim.set(qn("w:fldCharType"), "end")
    fim_run._r.append(fim)


def adicionar_numero_pagina(documento: Document) -> None:
    for secao in documento.sections:
        rodape = secao.footer
        p = rodape.paragraphs[0] if rodape.paragraphs else rodape.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Página ")
        definir_fonte(run, 9)
        adicionar_campo(p, "PAGE", "1")


def adicionar_paragrafo(documento: Document, texto: str, *, centralizado: bool = False, negrito: bool = False):
    p = documento.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centralizado else WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(texto)
    definir_fonte(r, 11, negrito)
    return p


def adicionar_titulo(documento: Document, texto: str, nivel: int = 1):
    p = documento.add_heading(texto, level=nivel)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def sombrear_celula(celula, cor: str) -> None:
    tc_pr = celula._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), cor)


def tabela(documento: Document, cabecalhos: list[str], linhas: list[list[str]], larguras: list[float] | None = None):
    tab = documento.add_table(rows=1, cols=len(cabecalhos))
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab.style = "Table Grid"
    for i, cabecalho in enumerate(cabecalhos):
        celula = tab.rows[0].cells[i]
        sombrear_celula(celula, "D9E2F3")
        celula.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = celula.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(cabecalho)
        definir_fonte(r, 9, True)
    for valores in linhas:
        celulas = tab.add_row().cells
        for i, valor in enumerate(valores):
            celulas[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = celulas[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(valor))
            definir_fonte(r, 9)
    if larguras:
        for linha in tab.rows:
            for i, largura in enumerate(larguras):
                linha.cells[i].width = Cm(largura)
    documento.add_paragraph()
    return tab


def adicionar_lista(documento: Document, itens: list[str]) -> None:
    for item in itens:
        p = documento.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.3)
        r = p.add_run(f"• {item}")
        definir_fonte(r, 11)


def adicionar_capa(documento: Document) -> None:
    for _ in range(5):
        documento.add_paragraph()
    p = documento.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ANÁLISE DE ROTAS DE RISCO E EVACUAÇÃO EM REGIÕES AFETADAS POR TORNADOS NOS EUA COM GRAFOS")
    definir_fonte(r, 16, True)
    p.paragraph_format.space_after = Pt(20)

    p = documento.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Relatório do Projeto — Parte 2")
    definir_fonte(r, 14, True)
    p.paragraph_format.space_after = Pt(18)

    adicionar_paragrafo(documento, "Disciplina: Teoria dos Grafos", centralizado=True)
    adicionar_paragrafo(documento, "Professor: Prof. Dr. Ivan Carlos Alcântara de Oliveira", centralizado=True)
    adicionar_paragrafo(documento, "Curso: Ciência da Computação", centralizado=True)
    adicionar_paragrafo(documento, "Turma: 6º G", centralizado=True)

    for _ in range(7):
        documento.add_paragraph()
    adicionar_paragrafo(documento, "São Paulo", centralizado=True)
    adicionar_paragrafo(documento, "2026", centralizado=True)
    documento.add_page_break()


def adicionar_sumario(documento: Document) -> None:
    adicionar_titulo(documento, "Sumário", 1)
    itens = [
        "1 Título",
        "2 Integrantes",
        "3 Resumo",
        "4 Introdução",
        "5 Fundamentação teórica",
        "6 Metodologia",
        "7 Resultados parciais",
        "8 Organização do repositório",
        "9 Limitações e próximos passos",
        "10 Conclusão",
        "Referências",
    ]
    for item in itens:
        p = documento.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8)
        r = p.add_run(item)
        definir_fonte(r, 11)
    documento.add_page_break()


def inserir_evidencias(documento: Document) -> None:
    imagens = sorted(EVIDENCIAS.glob("*.png"))
    grupos: dict[int, list[Path]] = {i: [] for i in range(1, 11)}
    for imagem in imagens:
        achado = re.search(r"(?:opcao|opcao_|opcao-)?0?(10|[1-9])", imagem.stem, re.IGNORECASE)
        if achado:
            grupos[int(achado.group(1))].append(imagem)

    nomes = {
        1: "Ler dados do grafo",
        2: "Gravar dados do grafo",
        3: "Inserir vértice",
        4: "Inserir aresta",
        5: "Remover vértice",
        6: "Remover aresta",
        7: "Mostrar conteúdo do arquivo",
        8: "Mostrar grafo",
        9: "Verificar conexidade",
        10: "Encerrar o programa",
    }
    for numero in range(1, 11):
        documento.add_page_break()
        adicionar_titulo(documento, f"Evidências da opção {numero} — {nomes[numero]}", 2)
        encontrados = grupos[numero]
        if len(encontrados) != 2:
            adicionar_paragrafo(documento, f"Foram localizadas {len(encontrados)} evidências para esta opção.")
        for indice, imagem in enumerate(encontrados, start=1):
            p = documento.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            with PillowImage.open(imagem) as arquivo_imagem:
                largura_cm, altura_cm = calcular_tamanho_imagem(
                    arquivo_imagem.width, arquivo_imagem.height, 15.5, 17.0
                )
            p.add_run().add_picture(str(imagem), width=Cm(largura_cm), height=Cm(altura_cm))
            legenda = documento.add_paragraph(style="Legenda")
            legenda.add_run(
                f"Figura {numero}.{indice} — Evidência {indice} da opção {numero}: {nomes[numero]}."
            )


def construir() -> Path:
    documento = Document(MODELO)
    preparar_template(documento)
    configurar_estilos(documento)

    for secao in documento.sections:
        secao.page_width = Cm(21)
        secao.page_height = Cm(29.7)
        secao.top_margin = Cm(2.54)
        secao.right_margin = Cm(1.9)
        secao.bottom_margin = Cm(2.54)
        secao.left_margin = Cm(1.9)

    adicionar_numero_pagina(documento)
    documento.add_page_break()
    adicionar_sumario(documento)

    adicionar_titulo(documento, "1 Título", 1)
    adicionar_paragrafo(
        documento,
        "Análise de Rotas de Risco e Evacuação em Regiões Afetadas por Tornados nos EUA com Grafos.",
    )

    adicionar_titulo(documento, "3 Resumo", 1)
    adicionar_paragrafo(
        documento,
        "Este projeto modela relações espaciais entre cidades de áreas historicamente expostas a tornados nos "
        "Estados Unidos por meio de um grafo não direcionado e ponderado. O conjunto produzido contém 80 "
        "vértices, correspondentes a cidades de oito estados, e 314 arestas, que representam proximidade "
        "geográfica entre pares de cidades. O peso inteiro de cada aresta combina a distância geodésica e um "
        "índice de risco relativo calculado a partir de 5.427 registros de tornados ocorridos entre 2015 e 2024. "
        "A solução foi implementada em Python, com persistência em arquivo texto do tipo 2, operações de edição, "
        "exibição e verificação de conexidade. O grafo final é conexo, possui quantidade superior ao mínimo de "
        "200 arestas e é acompanhado por 31 testes automatizados e vinte evidências de execução. A modelagem "
        "fornece uma base reprodutível para, em etapa posterior, estudar rotas de menor custo entre cidades.",
    )
    p = documento.add_paragraph()
    r = p.add_run("Palavras-chave: ")
    definir_fonte(r, 11, True)
    r = p.add_run("teoria dos grafos; tornados; risco; distância geográfica; conexidade.")
    definir_fonte(r, 11)

    adicionar_titulo(documento, "4 Introdução", 1)
    adicionar_paragrafo(
        documento,
        "Eventos meteorológicos severos afetam cidades conectadas por infraestrutura, fluxos populacionais e "
        "relações espaciais. A representação por grafos permite transformar esse contexto em uma estrutura "
        "computacional composta por vértices, arestas e pesos. Neste trabalho, cada vértice representa uma "
        "cidade e cada aresta representa uma relação de proximidade com outra cidade selecionada. O peso atribuído "
        "à aresta expressa um custo que cresce com a distância e com o risco relativo de tornados nas extremidades.",
    )
    adicionar_paragrafo(
        documento,
        "A Parte 2 materializa a proposta da primeira etapa em um programa de console capaz de ler, gravar e "
        "alterar o grafo. Além da implementação das operações obrigatórias, o projeto inclui a construção "
        "documentada do conjunto de dados, testes automatizados e evidências visuais para todas as opções do menu.",
    )

    adicionar_titulo(documento, "4.1 Contextualização", 2)
    adicionar_paragrafo(
        documento,
        "A base de eventos utiliza registros públicos do Storm Events Database da National Oceanic and "
        "Atmospheric Administration (NOAA) [1]. As cidades, suas coordenadas e suas populações foram selecionadas "
        "a partir das estimativas populacionais e dos arquivos Gazetteer do United States Census Bureau [2–4]. "
        "Foram considerados Texas, Oklahoma, Kansas, Nebraska, Dakota do Sul, Missouri, Iowa e Arkansas, com dez "
        "cidades por estado. Esse recorte produz variedade geográfica suficiente para estudar vizinhança e "
        "conectividade sem tornar o arquivo de entrada excessivamente grande.",
    )

    adicionar_titulo(documento, "4.2 Justificativa", 2)
    adicionar_paragrafo(
        documento,
        "O tema integra dados reais, modelagem matemática e desenvolvimento de software. A escolha de um grafo "
        "ponderado permite representar simultaneamente proximidade e exposição relativa. O projeto também "
        "favorece a aplicação de conceitos centrais da disciplina, como grau, caminho, componente conexa, matriz "
        "de adjacência e lista de adjacência. Socialmente, a proposta dialoga com os Objetivos de Desenvolvimento "
        "Sustentável 11 e 13, relacionados a cidades resilientes e ação climática [5].",
    )

    adicionar_titulo(documento, "4.3 Objetivo", 2)
    adicionar_paragrafo(
        documento,
        "Desenvolver uma representação em grafo de cidades expostas a tornados e um programa em Python que "
        "permita carregar, persistir, consultar e modificar essa estrutura, verificando sua conexidade e "
        "preparando-a para análises posteriores de caminhos de menor custo.",
    )
    adicionar_lista(
        documento,
        [
            "Construir um grafo não direcionado, ponderado e conexo com pelo menos 50 vértices e 200 arestas.",
            "Empregar dados públicos de cidades e ocorrências de tornados.",
            "Implementar as operações previstas no menu do enunciado.",
            "Garantir persistência compatível com o arquivo texto do tipo 2.",
            "Validar o comportamento por testes automatizados e duas evidências por opção do menu.",
        ],
    )

    adicionar_titulo(documento, "5 Fundamentação teórica", 1)
    adicionar_paragrafo(
        documento,
        "Um grafo G = (V, E) é formado por um conjunto V de vértices e um conjunto E de arestas. Como as relações "
        "de proximidade deste projeto são simétricas, utiliza-se um grafo não direcionado: a aresta {u, v} pode "
        "ser percorrida nos dois sentidos. O grafo é simples, pois não contém laços nem arestas paralelas. Cada "
        "aresta recebe um peso inteiro positivo, transformando a estrutura em um grafo ponderado.",
    )
    adicionar_paragrafo(
        documento,
        "A implementação armazena os rótulos dos vértices em uma lista e as arestas em um dicionário cuja chave é "
        "o par ordenado canônico (menor índice, maior índice). Essa decisão elimina duplicidades. Para verificar "
        "a conexidade, o programa realiza uma busca em largura a partir de um vértice e compara a quantidade de "
        "vértices alcançados com |V|. Se todos forem visitados, há uma única componente conexa.",
    )
    adicionar_paragrafo(
        documento,
        "A distância entre coordenadas é calculada pela fórmula de Haversine. Para duas posições com latitudes φ₁ "
        "e φ₂ e diferença de longitude Δλ, calcula-se a = sen²(Δφ/2) + cos(φ₁)cos(φ₂)sen²(Δλ/2) e d = 2R·arcsen(√a), "
        "com R = 6.371 km. O custo final da aresta é obtido pela distância multiplicada por um fator de risco médio "
        "das duas cidades e arredondado para um inteiro positivo.",
    )

    adicionar_titulo(documento, "5.1 Trabalhos e soluções relacionados", 2)
    adicionar_paragrafo(
        documento,
        "O Storm Events Database [1] oferece consulta e arquivos de eventos meteorológicos, mas não organiza as "
        "ocorrências como uma rede de cidades. Os arquivos do Census Bureau [2–4] fornecem população e coordenadas, "
        "porém também não expressam relações de vizinhança. A contribuição deste projeto é integrar as duas fontes "
        "em um grafo reproduzível, adequado às operações e aos algoritmos estudados na disciplina. Ferramentas "
        "genéricas de visualização de grafos auxiliam a inspeção estrutural, mas não substituem a metodologia de "
        "seleção e ponderação adotada aqui.",
    )

    adicionar_titulo(documento, "6 Metodologia", 1)
    adicionar_paragrafo(
        documento,
        "A execução foi dividida em cinco etapas: obtenção dos dados oficiais; seleção das cidades; cálculo do risco "
        "relativo; construção e validação do grafo; e implementação do programa de console com testes e evidências. "
        "O arquivo `gerar_grafo.py` automatiza a etapa de modelagem, de modo que o resultado possa ser reproduzido.",
    )
    tabela(
        documento,
        ["Etapa", "Procedimento", "Produto"],
        [
            ["1", "Coleta e normalização das fontes públicas", "cidades.csv e tornados.csv"],
            ["2", "Escolha das dez cidades mais populosas de cada estado", "80 vértices"],
            ["3", "Contagem de tornados em raio de 100 km", "índice de risco relativo"],
            ["4", "Ligação aos seis vizinhos geográficos mais próximos", "314 arestas"],
            ["5", "Testes e execuções roteirizadas", "31 testes e 20 evidências"],
        ],
        [1.5, 9.0, 5.5],
    )

    adicionar_titulo(documento, "6.1 Coleta de dados", 2)
    adicionar_paragrafo(
        documento,
        "O arquivo de tornados reúne 5.427 registros de 2015 a 2024. Para cada ocorrência são mantidos ano, estado, "
        "latitude, longitude e intensidade quando disponível. O arquivo de cidades contém estado, nome, população, "
        "latitude e longitude. As URLs exatas, a data de acesso e as regras de transformação estão registradas em "
        "`dados/fontes.md`, permitindo auditoria da procedência.",
    )
    tabela(
        documento,
        ["Arquivo", "Linhas de dados", "Campos principais", "Origem"],
        [
            ["cidades.csv", "80", "estado, cidade, população, latitude, longitude", "U.S. Census Bureau"],
            ["tornados.csv", "5.427", "ano, estado, latitude, longitude, intensidade", "NOAA/NCEI"],
        ],
        [3.0, 2.5, 7.0, 3.5],
    )

    adicionar_titulo(documento, "6.2 Modelagem do problema como grafo", 2)
    adicionar_paragrafo(
        documento,
        "Cada cidade recebe um índice inteiro e um rótulo no formato `Cidade, UF`. Para cada cidade são selecionados "
        "os seis vizinhos com menor distância geodésica. Como o grafo é não direcionado, uniões repetidas são "
        "eliminadas. Após a construção, um procedimento de componentes conexas confirma que todos os vértices estão "
        "alcançáveis. O arquivo final segue o tipo 2: primeira linha com o tipo do grafo, segunda com a quantidade "
        "de vértices, rótulos nas linhas seguintes e, ao final, quantidade e lista de arestas com pesos.",
    )
    tabela(
        documento,
        ["Característica", "Valor final"],
        [
            ["Tipo", "2 — não direcionado e ponderado"],
            ["Vértices", "80"],
            ["Arestas", "314"],
            ["Estados", "8"],
            ["Componentes conexas", "1"],
            ["Peso", "inteiro positivo baseado em distância e risco"],
        ],
        [7.0, 9.0],
    )

    adicionar_titulo(documento, "6.3 Implementação", 2)
    adicionar_paragrafo(
        documento,
        "A classe `Grafo` concentra as invariantes da estrutura, valida índices e pesos, impede laços e duplicidades "
        "e recalcula os índices das arestas quando um vértice é removido. O módulo `arquivo_grafo.py` realiza a "
        "leitura estrita e a gravação atômica. O programa `main.py` apresenta o menu em português e converte erros "
        "de entrada em mensagens compreensíveis, sem encerrar inesperadamente a sessão.",
    )
    tabela(
        documento,
        ["Opção", "Operação", "Resultado esperado"],
        [
            ["1", "Ler grafo", "Carrega e valida arquivo tipo 2"],
            ["2", "Gravar grafo", "Persiste o estado atual"],
            ["3", "Inserir vértice", "Inclui novo rótulo"],
            ["4", "Inserir aresta", "Inclui ligação ponderada"],
            ["5", "Remover vértice", "Remove e reindexa arestas"],
            ["6", "Remover aresta", "Exclui ligação existente"],
            ["7", "Mostrar arquivo", "Exibe o conteúdo textual"],
            ["8", "Mostrar grafo", "Lista vértices e arestas"],
            ["9", "Verificar conexidade", "Informa componentes"],
            ["10", "Encerrar", "Finaliza de forma controlada"],
        ],
        [2.0, 5.5, 8.5],
    )

    adicionar_titulo(documento, "7 Resultados parciais", 1)
    adicionar_paragrafo(
        documento,
        "O programa atende às operações solicitadas e o grafo produzido supera os limites de 50 vértices e 200 "
        "arestas. A execução da suíte automatizada resultou em 31 testes aprovados. Os testes abrangem criação e "
        "alteração do grafo, validações, persistência, tratamento de arquivos inválidos, opções do menu, cálculo "
        "geográfico, construção do conjunto e conectividade.",
    )
    tabela(
        documento,
        ["Indicador", "Resultado", "Situação"],
        [
            ["Vértices", "80 (mínimo: 50)", "Atendido"],
            ["Arestas", "314 (mínimo: 200)", "Atendido"],
            ["Conexidade", "1 componente", "Atendido"],
            ["Testes automatizados", "31 aprovados", "Atendido"],
            ["Evidências", "20 imagens", "Atendido"],
            ["Opções do menu", "10 implementadas", "Atendido"],
        ],
        [6.0, 5.0, 5.0],
    )
    adicionar_paragrafo(
        documento,
        "A análise dos resultados indica que a estratégia dos seis vizinhos mais próximos produz densidade "
        "suficiente para a atividade e mantém o grafo conectado. Os pesos não devem ser interpretados como uma "
        "previsão meteorológica; eles constituem um custo relativo para fins acadêmicos. A etapa futura poderá "
        "aplicar Dijkstra e comparar rotas com diferentes formulações de custo.",
    )

    adicionar_titulo(documento, "7.1 Evidências de execução", 2)
    adicionar_paragrafo(
        documento,
        "As páginas seguintes apresentam duas execuções documentadas para cada opção. Os arquivos de texto "
        "correspondentes permanecem na pasta `testes/evidencias`, permitindo conferir integralmente as entradas e "
        "saídas além das capturas inseridas neste relatório.",
    )
    inserir_evidencias(documento)

    documento.add_page_break()
    adicionar_titulo(documento, "8 Organização do repositório", 1)
    adicionar_paragrafo(
        documento,
        "O projeto foi organizado para separar código-fonte, dados, testes, evidências e documentação. Todos os "
        "arquivos Python possuem cabeçalho com identificação do projeto, síntese do conteúdo e histórico de "
        "alterações. O `README.md` contém instruções de execução e testes.",
    )
    tabela(
        documento,
        ["Caminho", "Finalidade"],
        [
            ["main.py", "Programa principal e menu"],
            ["grafo.py", "Estrutura e operações do grafo"],
            ["arquivo_grafo.py", "Leitura e gravação no formato tipo 2"],
            ["gerar_grafo.py", "Geração reprodutível do conjunto"],
            ["grafo.txt", "Grafo final com 80 vértices e 314 arestas"],
            ["dados/", "Fontes tratadas e metodologia"],
            ["testes/", "Testes automatizados e evidências"],
            ["relatorio/", "Gerador e relatório da Parte 2"],
        ],
        [6.0, 10.0],
    )

    adicionar_titulo(documento, "8.1 Endereço público do GitHub", 2)
    p = documento.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run("[PREENCHER ANTES DA ENTREGA: URL PÚBLICA DO REPOSITÓRIO]")
    definir_fonte(r, 11, True)
    r.font.highlight_color = 7
    adicionar_paragrafo(
        documento,
        "O endereço não foi inventado neste relatório. Após a publicação, confirme que o repositório está público "
        "e contém o relatório, os arquivos-fonte, `grafo.txt`, os dados e as evidências.",
    )

    adicionar_titulo(documento, "9 Limitações e próximos passos", 1)
    adicionar_lista(
        documento,
        [
            "O índice representa risco relativo histórico e não substitui avaliação meteorológica operacional.",
            "O recorte utiliza dez cidades por estado; cidades menores não aparecem no grafo.",
            "A relação por vizinhos próximos simplifica fatores reais de mobilidade e infraestrutura.",
            "A próxima etapa pode implementar caminho mínimo e comparar cenários de ponderação.",
        ],
    )

    adicionar_titulo(documento, "10 Conclusão", 1)
    adicionar_paragrafo(
        documento,
        "A Parte 2 atingiu o objetivo de transformar a proposta sobre tornados em uma solução executável e "
        "verificável. A integração de dados oficiais resultou em um grafo não direcionado, ponderado e conexo com "
        "80 cidades e 314 relações. O programa oferece as dez opções previstas, a persistência respeita o formato "
        "tipo 2 e a qualidade foi verificada por testes automatizados e evidências de execução. Assim, o projeto "
        "dispõe de uma base consistente para análises futuras de caminhos e custos em grafos.",
    )

    adicionar_titulo(documento, "Referências", 1)
    referencias = [
        "[1] NATIONAL OCEANIC AND ATMOSPHERIC ADMINISTRATION. Storm Events Database. Disponível em: https://www.ncei.noaa.gov/access/storm-events-database/. Acesso em: 28 set. 2026.",
        "[2] UNITED STATES CENSUS BUREAU. City and Town Population Totals: 2020–2025. Disponível em: https://www.census.gov/programs-surveys/popest/data/tables.html. Acesso em: 28 set. 2026.",
        "[3] UNITED STATES CENSUS BUREAU. Annual Estimates of the Resident Population for Incorporated Places: 2020–2025. Disponível em: https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025.csv. Acesso em: 28 set. 2026.",
        "[4] UNITED STATES CENSUS BUREAU. 2025 Gazetteer Files. Disponível em: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html. Acesso em: 28 set. 2026.",
        "[5] ORGANIZAÇÃO DAS NAÇÕES UNIDAS. Sustainable Development Goals: Goals 11 and 13. Disponível em: https://sdgs.un.org/goals. Acesso em: 28 set. 2026.",
    ]
    for ref in referencias:
        p = documento.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(-0.75)
        p.paragraph_format.left_indent = Cm(0.75)
        r = p.add_run(ref)
        definir_fonte(r, 10)

    propriedades = documento.core_properties
    propriedades.title = "Análise de Rotas de Risco e Evacuação em Regiões Afetadas por Tornados nos EUA com Grafos — Parte 2"
    propriedades.subject = "Relatório do projeto de Teoria dos Grafos"
    propriedades.author = "Grupo do projeto de Teoria dos Grafos"
    propriedades.keywords = "grafos, tornados, Python, conexidade, risco"
    propriedades.comments = "Relatório produzido em português a partir do modelo institucional fornecido."

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    documento.save(SAIDA)
    return SAIDA


if __name__ == "__main__":
    print(construir())
