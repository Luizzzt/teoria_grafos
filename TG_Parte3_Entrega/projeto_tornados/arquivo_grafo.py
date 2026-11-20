"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: leitura, validação e gravação atômica do arquivo grafo.txt.
Histórico: 28/09/2026 - Codex - implementação inicial da persistência.
"""

import json
import os
import shlex
import tempfile
from pathlib import Path

from .grafo import ErroGrafo, Grafo


class ErroArquivoGrafo(ValueError):
    """Indica que o arquivo não respeita o formato definido no projeto."""


def carregar_grafo(caminho: Path) -> Grafo:
    """Lê e valida completamente um grafo tipo 2 antes de devolvê-lo."""
    caminho = Path(caminho)
    try:
        linhas = [
            linha.strip()
            for linha in caminho.read_text(encoding="utf-8-sig").splitlines()
            if linha.strip()
        ]
    except OSError as erro:
        raise ErroArquivoGrafo(f"Não foi possível ler {caminho}: {erro}") from erro

    posicao = 0

    def proxima(descricao: str) -> str:
        nonlocal posicao
        if posicao >= len(linhas):
            raise ErroArquivoGrafo(f"Arquivo incompleto: faltou {descricao}.")
        valor = linhas[posicao]
        posicao += 1
        return valor

    try:
        tipo = int(proxima("o tipo do grafo"))
        if tipo != 2:
            raise ErroArquivoGrafo("Este projeto aceita somente grafo do tipo 2.")

        quantidade_vertices = _inteiro_nao_negativo(
            proxima("a quantidade de vértices"), "quantidade de vértices"
        )
        grafo = Grafo()
        for esperado in range(quantidade_vertices):
            tokens = shlex.split(proxima(f"o vértice {esperado}"), posix=True)
            if len(tokens) != 2:
                raise ErroArquivoGrafo(
                    f"Vértice {esperado} deve ter índice e rótulo entre aspas."
                )
            indice = int(tokens[0])
            if indice != esperado:
                raise ErroArquivoGrafo(
                    f"Índice de vértice inválido: esperado {esperado}, recebido {indice}."
                )
            grafo.adicionar_vertice(tokens[1])

        quantidade_arestas = _inteiro_nao_negativo(
            proxima("a quantidade de arestas"), "quantidade de arestas"
        )
        for numero in range(quantidade_arestas):
            tokens = proxima(f"a aresta {numero}").split()
            if len(tokens) != 3:
                raise ErroArquivoGrafo(
                    f"Aresta {numero} deve ter origem, destino e peso."
                )
            origem, destino, peso = map(int, tokens)
            grafo.adicionar_aresta(origem, destino, peso)

        if posicao != len(linhas):
            raise ErroArquivoGrafo("Há conteúdo extra após a última aresta.")
        return grafo
    except ErroArquivoGrafo:
        raise
    except (ValueError, ErroGrafo) as erro:
        raise ErroArquivoGrafo(f"Conteúdo inválido em {caminho}: {erro}") from erro


def salvar_grafo(grafo: Grafo, caminho: Path) -> None:
    """Grava o grafo em UTF-8 sem deixar arquivo parcial em caso de erro."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    linhas = ["2", str(grafo.numero_vertices)]
    for indice, rotulo in sorted(grafo.rotulos.items()):
        linhas.append(f"{indice} {json.dumps(rotulo, ensure_ascii=False)}")

    arestas = [
        (origem, destino, peso)
        for origem, vizinhos in sorted(grafo.adjacencias.items())
        for destino, peso in sorted(vizinhos.items())
        if origem < destino
    ]
    linhas.append(str(len(arestas)))
    linhas.extend(f"{origem} {destino} {peso}" for origem, destino, peso in arestas)
    conteudo = "\n".join(linhas) + "\n"

    temporario: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=caminho.parent,
            prefix=f".{caminho.name}.",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            arquivo.write(conteudo)
            temporario = arquivo.name
        os.replace(temporario, caminho)
    except OSError as erro:
        if temporario:
            Path(temporario).unlink(missing_ok=True)
        raise ErroArquivoGrafo(f"Não foi possível gravar {caminho}: {erro}") from erro


def formatar_conteudo_arquivo(caminho: Path) -> str:
    """Devolve o conteúdo textual atual do arquivo para apresentação no menu."""
    try:
        return Path(caminho).read_text(encoding="utf-8-sig")
    except OSError as erro:
        raise ErroArquivoGrafo(f"Não foi possível ler {caminho}: {erro}") from erro


def _inteiro_nao_negativo(valor: str, descricao: str) -> int:
    numero = int(valor)
    if numero < 0:
        raise ErroArquivoGrafo(f"A {descricao} não pode ser negativa.")
    return numero
