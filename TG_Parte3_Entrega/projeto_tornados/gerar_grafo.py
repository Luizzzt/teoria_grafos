"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: geração determinística do grafo com dados oficiais de cidades e tornados.
Histórico: 28/09/2026 - Codex - implementação do cálculo de risco e das conexões.
"""

import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path

from .arquivo_grafo import salvar_grafo
from .grafo import Grafo


@dataclass(frozen=True)
class Cidade:
    geoid: str
    cidade: str
    estado: str
    populacao: int
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Tornado:
    event_id: str
    ano: int
    data: str
    estado: str
    escala_ef: str
    latitude: float
    longitude: float


def carregar_cidades_csv(caminho: Path) -> list[Cidade]:
    with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
        cidades = [
            Cidade(
                geoid=linha["geoid"],
                cidade=linha["cidade"],
                estado=linha["estado"],
                populacao=int(linha["populacao"]),
                latitude=float(linha["latitude"]),
                longitude=float(linha["longitude"]),
            )
            for linha in csv.DictReader(arquivo)
        ]
    if not cidades:
        raise ValueError("O arquivo de cidades está vazio.")
    return cidades


def carregar_tornados_csv(caminho: Path) -> list[Tornado]:
    with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
        return [
            Tornado(
                event_id=linha["event_id"],
                ano=int(linha["ano"]),
                data=linha["data"],
                estado=linha["estado"],
                escala_ef=linha["escala_ef"],
                latitude=float(linha["latitude"]),
                longitude=float(linha["longitude"]),
            )
            for linha in csv.DictReader(arquivo)
        ]


def distancia_haversine_km(a: Cidade, b: Cidade) -> float:
    return _distancia_coordenadas(a.latitude, a.longitude, b.latitude, b.longitude)


def calcular_riscos(
    cidades: list[Cidade], tornados: list[Tornado], raio_km: float = 100.0
) -> dict[str, float]:
    if raio_km <= 0:
        raise ValueError("O raio de análise deve ser positivo.")
    pontuacoes = {cidade.geoid: 0 for cidade in cidades}
    for cidade in cidades:
        for tornado in tornados:
            distancia = _distancia_coordenadas(
                cidade.latitude,
                cidade.longitude,
                tornado.latitude,
                tornado.longitude,
            )
            if distancia <= raio_km:
                pontuacoes[cidade.geoid] += _pontuacao_escala(tornado.escala_ef)
    maior = max(pontuacoes.values(), default=0)
    if maior == 0:
        return {codigo: 0.0 for codigo in pontuacoes}
    return {codigo: valor / maior for codigo, valor in pontuacoes.items()}


def gerar_grafo(
    cidades: list[Cidade], tornados: list[Tornado], vizinhos: int = 6
) -> Grafo:
    if not cidades:
        raise ValueError("É necessária ao menos uma cidade.")
    if vizinhos < 1:
        raise ValueError("A quantidade de vizinhos deve ser positiva.")
    if len({cidade.geoid for cidade in cidades}) != len(cidades):
        raise ValueError("Há identificadores de cidades repetidos.")

    grafo = Grafo()
    for cidade in cidades:
        grafo.adicionar_vertice(f"{cidade.cidade}, {cidade.estado}")

    riscos = calcular_riscos(cidades, tornados)
    distancias = sorted(
        (
            distancia_haversine_km(cidades[origem], cidades[destino]),
            origem,
            destino,
        )
        for origem in range(len(cidades))
        for destino in range(origem + 1, len(cidades))
    )

    pares: set[tuple[int, int]] = set()
    for origem in range(len(cidades)):
        proximas = sorted(
            (
                (distancia_haversine_km(cidades[origem], cidades[destino]), destino)
                for destino in range(len(cidades))
                if destino != origem
            ),
            key=lambda item: (item[0], item[1]),
        )[: min(vizinhos, len(cidades) - 1)]
        for _distancia, destino in proximas:
            pares.add(tuple(sorted((origem, destino))))

    _conectar_componentes(pares, distancias, len(cidades))
    alvo = min(200, len(cidades) * (len(cidades) - 1) // 2)
    for _distancia, origem, destino in distancias:
        if len(pares) >= alvo:
            break
        pares.add((origem, destino))

    distancias_por_par = {
        (origem, destino): distancia for distancia, origem, destino in distancias
    }
    for origem, destino in sorted(pares):
        risco_medio = (
            riscos[cidades[origem].geoid] + riscos[cidades[destino].geoid]
        ) / 2
        peso = max(1, round(distancias_por_par[(origem, destino)] * (1 + risco_medio)))
        grafo.adicionar_aresta(origem, destino, peso)
    return grafo


def main() -> None:
    base = Path(__file__).resolve().parent
    cidades = carregar_cidades_csv(base / "dados" / "cidades.csv")
    tornados = carregar_tornados_csv(base / "dados" / "tornados.csv")
    grafo = gerar_grafo(cidades, tornados)
    salvar_grafo(grafo, base / "grafo.txt")
    situacao = "grafo conexo" if grafo.eh_conexo() else "grafo desconexo"
    print(
        f"Arquivo gerado: {grafo.numero_vertices} vértices, "
        f"{grafo.numero_arestas} arestas, {situacao}."
    )


def _distancia_coordenadas(
    latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float
) -> float:
    raio_terra_km = 6371.0088
    lat_a = math.radians(latitude_a)
    lat_b = math.radians(latitude_b)
    delta_lat = math.radians(latitude_b - latitude_a)
    delta_lon = math.radians(longitude_b - longitude_a)
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    )
    return raio_terra_km * 2 * math.asin(math.sqrt(haversine))


def _pontuacao_escala(escala: str) -> int:
    correspondencia = re.search(r"(?:EF|F)([0-5])", escala.upper())
    return int(correspondencia.group(1)) + 1 if correspondencia else 1


def _conectar_componentes(
    pares: set[tuple[int, int]],
    distancias: list[tuple[float, int, int]],
    quantidade_vertices: int,
) -> None:
    while True:
        componentes = _componentes_dos_pares(pares, quantidade_vertices)
        if len(componentes) <= 1:
            return
        componente_por_vertice = {
            vertice: indice
            for indice, componente in enumerate(componentes)
            for vertice in componente
        }
        for _distancia, origem, destino in distancias:
            if componente_por_vertice[origem] != componente_por_vertice[destino]:
                pares.add((origem, destino))
                break


def _componentes_dos_pares(
    pares: set[tuple[int, int]], quantidade_vertices: int
) -> list[set[int]]:
    vizinhos = {indice: set() for indice in range(quantidade_vertices)}
    for origem, destino in pares:
        vizinhos[origem].add(destino)
        vizinhos[destino].add(origem)
    restantes = set(vizinhos)
    componentes: list[set[int]] = []
    while restantes:
        inicio = min(restantes)
        componente = {inicio}
        pilha = [inicio]
        restantes.remove(inicio)
        while pilha:
            atual = pilha.pop()
            for vizinho in sorted(vizinhos[atual]):
                if vizinho in restantes:
                    restantes.remove(vizinho)
                    componente.add(vizinho)
                    pilha.append(vizinho)
        componentes.append(componente)
    return componentes


if __name__ == "__main__":
    main()

