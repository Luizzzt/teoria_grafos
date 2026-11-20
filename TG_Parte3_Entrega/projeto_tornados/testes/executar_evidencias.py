"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: executa cenários reais do menu e gera transcrições e capturas PNG.
Histórico: 28/09/2026 - Codex - criação das evidências automatizadas; 29/09/2026 - Codex - moldura realista de console.
"""

import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from projeto_tornados.arquivo_grafo import salvar_grafo
from projeto_tornados.grafo import Grafo
from projeto_tornados.main import executar_menu


BASE = Path(__file__).resolve().parent
DESTINO = BASE / "evidencias"
CAMINHO_CONSOLE = r"C:\Users\Alexandre\Documents\ProjetoTornados"


CENARIOS = {
    1: [(["1", "10"], True), (["1", "10"], False)],
    2: [(["1", "2", "10"], True), (["2", "10"], False)],
    3: [(["3", "Cidade Experimental, TX", "10"], False), (["3", "", "10"], False)],
    4: [
        (["3", "A", "3", "B", "4", "0", "1", "15", "10"], False),
        (["3", "A", "3", "B", "4", "0", "1", "0", "10"], False),
    ],
    5: [
        (["3", "A", "3", "B", "4", "0", "1", "5", "5", "1", "s", "10"], False),
        (["3", "A", "5", "0", "n", "10"], False),
    ],
    6: [
        (["3", "A", "3", "B", "4", "0", "1", "5", "6", "0", "1", "s", "10"], False),
        (["3", "A", "3", "B", "6", "0", "1", "s", "10"], False),
    ],
    7: [(["7", "10"], True), (["7", "10"], False)],
    8: [(["1", "8", "10"], True), (["8", "10"], False)],
    9: [(["1", "9", "10"], True), (["3", "A", "3", "B", "9", "10"], False)],
    10: [(["10"], False), (["99", "10"], False)],
}


def executar_cenario(
    nome: str,
    entradas: list[str],
    diretorio: Path,
    criar_grafo_base: bool = True,
) -> Path:
    diretorio.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporario:
        caminho_grafo = Path(temporario) / "grafo.txt"
        if criar_grafo_base:
            _salvar_grafo_pequeno(caminho_grafo)
        iterador = iter(entradas)
        saidas: list[str] = []

        def entrada_registrada() -> str:
            valor = next(iterador)
            saidas.append(f"> {valor}")
            return valor

        executar_menu(caminho_grafo, entrada_registrada, saidas.append)
        texto = "\n".join(saidas) + "\n"

    caminho_txt = diretorio / f"{nome}.txt"
    caminho_png = diretorio / f"{nome}.png"
    caminho_txt.write_text(texto, encoding="utf-8")
    _renderizar_transcricao(texto, caminho_png)
    return caminho_txt


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for opcao, cenarios in CENARIOS.items():
        for numero, (entradas, criar_base) in enumerate(cenarios, 1):
            executar_cenario(
                f"opcao_{opcao:02d}_teste_{numero:02d}",
                entradas,
                DESTINO,
                criar_base,
            )
    print("Evidências geradas: 20 transcrições e 20 imagens PNG.")


def _salvar_grafo_pequeno(caminho: Path) -> None:
    grafo = Grafo()
    for rotulo in ("Oklahoma City, OK", "Tulsa, OK", "Wichita, KS"):
        grafo.adicionar_vertice(rotulo)
    grafo.adicionar_aresta(0, 1, 170)
    grafo.adicionar_aresta(1, 2, 285)
    salvar_grafo(grafo, caminho)


def _renderizar_transcricao(texto: str, caminho: Path) -> None:
    try:
        fonte = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
        fonte_titulo = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17)
        fonte_icone = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 13)
    except OSError:
        fonte = ImageFont.load_default()
        fonte_titulo = fonte
        fonte_icone = fonte

    linhas_brutas = texto.rstrip().splitlines()
    linhas_com_entrada: list[str] = []
    for linha in linhas_brutas:
        if linha.startswith("> ") and linhas_com_entrada:
            anterior = linhas_com_entrada[-1]
            if anterior.rstrip().endswith((":", "]:")):
                linhas_com_entrada[-1] = f"{anterior} {linha[2:]}"
                continue
        linhas_com_entrada.append(linha)

    linhas: list[str] = [
        f"{CAMINHO_CONSOLE}>python -m projeto_tornados.main",
        "",
    ]
    for linha in linhas_com_entrada:
        linhas.extend(textwrap.wrap(linha, width=116, replace_whitespace=False) or [""])
    linhas.extend(
        [
            "",
            f"{CAMINHO_CONSOLE}>█",
        ]
    )

    maximo_visivel = 34
    houve_rolagem = len(linhas) > maximo_visivel
    linhas_visiveis = linhas[-maximo_visivel:] if houve_rolagem else linhas

    altura_linha = 25
    largura = 1500
    altura_barra = 50
    altura = max(520, altura_barra + 48 + altura_linha * len(linhas_visiveis))
    imagem = Image.new("RGB", (largura, altura), "#0C0C0C")
    desenho = ImageDraw.Draw(imagem)

    # Moldura e barra de título inspiradas no Prompt de Comando do Windows 11.
    desenho.rectangle((0, 0, largura - 1, altura - 1), outline="#666666", width=1)
    desenho.rectangle((1, 1, largura - 2, altura_barra), fill="#202020")
    desenho.rectangle((18, 15, 39, 35), fill="#0C0C0C", outline="#8A8A8A")
    desenho.text((21, 16), ">_", font=fonte_icone, fill="#F2F2F2")
    desenho.text(
        (52, 14),
        "Prompt de Comando - python -m projeto_tornados.main",
        font=fonte_titulo,
        fill="#F2F2F2",
    )

    # Controles da janela; o botão fechar aparece em estado de foco, como em uma captura real.
    desenho.rectangle((1338, 1, 1391, altura_barra), fill="#202020")
    desenho.line((1357, 26, 1372, 26), fill="#F2F2F2", width=2)
    desenho.rectangle((1392, 1, 1445, altura_barra), fill="#202020")
    desenho.rectangle((1410, 17, 1426, 32), outline="#F2F2F2", width=2)
    desenho.rectangle((1446, 1, 1498, altura_barra), fill="#C42B1C")
    desenho.line((1464, 17, 1480, 33), fill="#FFFFFF", width=2)
    desenho.line((1480, 17, 1464, 33), fill="#FFFFFF", width=2)

    # Área útil e barra de rolagem vertical.
    desenho.rectangle((1, altura_barra + 1, largura - 2, altura - 2), fill="#0C0C0C")
    desenho.rectangle((1482, altura_barra + 1, 1498, altura - 2), fill="#1F1F1F")
    tamanho_thumb = max(90, int((altura - altura_barra) * min(1.0, maximo_visivel / max(1, len(linhas)))))
    topo_thumb = altura_barra + 14
    if houve_rolagem:
        topo_thumb = altura - tamanho_thumb - 18
    desenho.rectangle((1485, topo_thumb, 1495, topo_thumb + tamanho_thumb), fill="#606060")

    y = altura_barra + 18
    for linha in linhas_visiveis:
        desenho.text((20, y), linha, font=fonte, fill="#CCCCCC")
        y += altura_linha
    imagem.save(caminho, format="PNG", optimize=True, dpi=(96, 96))


if __name__ == "__main__":
    main()

