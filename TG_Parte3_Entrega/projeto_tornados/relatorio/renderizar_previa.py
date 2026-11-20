"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: renderização de uma prévia PDF de controle a partir do DOCX final.
Histórico: 28/09/2026 - Codex - criação da prévia alternativa para inspeção visual.
"""

from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from PIL import Image as PillowImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

try:
    from relatorio.construir_relatorio import calcular_tamanho_imagem
except ModuleNotFoundError:
    from construir_relatorio import calcular_tamanho_imagem


RAIZ = Path(__file__).resolve().parents[1]
DOCX = RAIZ / "relatorio" / "relatorio_projeto_tornados.docx"
PDF = RAIZ.parent / "work" / "qa_relatorio" / "previa_relatorio.pdf"


def blocos(documento: DocumentType):
    for filho in documento.element.body.iterchildren():
        if isinstance(filho, CT_P):
            yield DocxParagraph(filho, documento)
        elif isinstance(filho, CT_Tbl):
            yield DocxTable(filho, documento)


def estilos_relatorio():
    base = getSampleStyleSheet()
    return {
        "normal": ParagraphStyle(
            "Corpo",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=12,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "Titulo1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "Titulo2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "Titulo3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.black,
            spaceBefore=6,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "centro": ParagraphStyle(
            "Centro", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=12, alignment=TA_CENTER
        ),
        "legenda": ParagraphStyle(
            "Legenda",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=10,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "celula": ParagraphStyle(
            "Celula", parent=base["Normal"], fontName="Helvetica", fontSize=8.3, leading=10, alignment=TA_LEFT
        ),
    }


def cabecalho_rodape(canvas, documento):
    canvas.saveState()
    largura, altura = A4
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(1.9 * cm, altura - 1.25 * cm, "UNIVERSIDADE PRESBITERIANA MACKENZIE — Teoria dos Grafos")
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(largura / 2, 1.35 * cm, f"Página {documento.page}")
    canvas.restoreState()


def imagem_do_paragrafo(paragrafo: DocxParagraph):
    blips = paragrafo._p.xpath(".//a:blip")
    if not blips:
        return None
    rel_id = blips[0].get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
    blob = paragrafo.part.related_parts[rel_id].blob
    largura_px, altura_px = PillowImage.open(BytesIO(blob)).size
    largura_cm, altura_cm = calcular_tamanho_imagem(largura_px, altura_px, 15.5, 17.0)
    largura = largura_cm * cm
    altura = altura_cm * cm
    return Image(BytesIO(blob), width=largura, height=altura)


def paragrafo_pdf(paragrafo: DocxParagraph, estilos):
    estilo = paragrafo.style.name if paragrafo.style else "Normal"
    texto = escape(paragrafo.text).replace("\n", "<br/>")
    if estilo == "Heading 1":
        return Paragraph(texto, estilos["h1"])
    if estilo == "Heading 2":
        return Paragraph(texto, estilos["h2"])
    if estilo == "Heading 3":
        return Paragraph(texto, estilos["h3"])
    if estilo == "Legenda":
        return Paragraph(texto, estilos["legenda"])
    alinhamento = paragrafo.alignment
    escolhido = estilos["centro"] if alinhamento == 1 else estilos["normal"]
    if estilo == "List Bullet" and texto:
        texto = texto if texto.startswith("•") else f"• {texto}"
    return Paragraph(texto or " ", escolhido)


def renderizar() -> Path:
    documento = Document(DOCX)
    estilos = estilos_relatorio()
    historia = []
    for bloco in blocos(documento):
        if isinstance(bloco, DocxParagraph):
            quebras = bloco._p.xpath('.//w:br[@w:type="page"]')
            imagem = imagem_do_paragrafo(bloco)
            if quebras and not bloco.text.strip() and imagem is None:
                historia.append(PageBreak())
                continue
            if imagem is not None:
                historia.extend([Spacer(1, 4), imagem, Spacer(1, 3)])
            if bloco.text.strip():
                historia.append(paragrafo_pdf(bloco, estilos))
        else:
            dados = []
            for linha in bloco.rows:
                dados.append([Paragraph(escape(celula.text), estilos["celula"]) for celula in linha.cells])
            if dados:
                largura_util = 17.2 * cm
                tabela_pdf = Table(dados, colWidths=[largura_util / len(dados[0])] * len(dados[0]), repeatRows=1)
                tabela_pdf.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#808080")),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                historia.extend([tabela_pdf, Spacer(1, 8)])

    PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(PDF),
        pagesize=A4,
        leftMargin=1.9 * cm,
        rightMargin=1.9 * cm,
        topMargin=2.54 * cm,
        bottomMargin=2.54 * cm,
        title="Prévia de controle — relatório do projeto de tornados",
        author="Grupo do projeto de Teoria dos Grafos",
    )
    quadro = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="corpo")
    doc.addPageTemplates([PageTemplate(id="A4", frames=[quadro], onPage=cabecalho_rodape)])
    doc.build(historia)
    return PDF


if __name__ == "__main__":
    print(renderizar())
