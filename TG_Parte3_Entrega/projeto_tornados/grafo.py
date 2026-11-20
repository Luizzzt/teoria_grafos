"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: estrutura de grafo não orientado com pesos nas arestas.
Histórico: 28/09/2026 - Codex - implementação inicial da classe Grafo.
         19/11/2026 - Codex - adição de Dijkstra, grau dos vértices, verificação euleriana,
                               verificação hamiltoniana (Ore/Dirac) e coloração gulosa.
"""

from collections import deque
import heapq


class ErroGrafo(ValueError):
    """Indica uma operação incompatível com a estrutura do grafo."""


class Grafo:
    """Grafo não orientado, rotulado e ponderado por lista de adjacência."""

    def __init__(self) -> None:
        self._rotulos: dict[int, str] = {}
        self._adjacencias: dict[int, dict[int, int]] = {}

    @property
    def rotulos(self) -> dict[int, str]:
        return {indice: rotulo for indice, rotulo in self._rotulos.items()}

    @property
    def adjacencias(self) -> dict[int, dict[int, int]]:
        return {
            origem: {destino: peso for destino, peso in vizinhos.items()}
            for origem, vizinhos in self._adjacencias.items()
        }

    @property
    def numero_vertices(self) -> int:
        return len(self._rotulos)

    @property
    def numero_arestas(self) -> int:
        return sum(len(vizinhos) for vizinhos in self._adjacencias.values()) // 2

    def adicionar_vertice(self, rotulo: str) -> int:
        rotulo_normalizado = rotulo.strip()
        if not rotulo_normalizado:
            raise ErroGrafo("O rótulo do vértice não pode estar vazio.")
        if rotulo_normalizado.casefold() in {
            existente.casefold() for existente in self._rotulos.values()
        }:
            raise ErroGrafo("Já existe um vértice com esse rótulo.")
        indice = len(self._rotulos)
        self._rotulos[indice] = rotulo_normalizado
        self._adjacencias[indice] = {}
        return indice

    def adicionar_aresta(self, origem: int, destino: int, peso: int) -> None:
        self._validar_vertice(origem)
        self._validar_vertice(destino)
        if origem == destino:
            raise ErroGrafo("Laços não são permitidos neste projeto.")
        if not isinstance(peso, int) or isinstance(peso, bool) or peso <= 0:
            raise ErroGrafo("O peso deve ser um número inteiro positivo.")
        if destino in self._adjacencias[origem]:
            raise ErroGrafo("A aresta informada já existe.")
        self._adjacencias[origem][destino] = peso
        self._adjacencias[destino][origem] = peso

    def remover_vertice(self, vertice: int) -> dict[int, int]:
        self._validar_vertice(vertice)
        indices_antigos = [indice for indice in self._rotulos if indice != vertice]
        mapeamento = {antigo: novo for novo, antigo in enumerate(indices_antigos)}

        novos_rotulos = {
            mapeamento[antigo]: self._rotulos[antigo] for antigo in indices_antigos
        }
        novas_adjacencias = {novo: {} for novo in novos_rotulos}
        for origem_antiga in indices_antigos:
            for destino_antigo, peso in self._adjacencias[origem_antiga].items():
                if destino_antigo == vertice or origem_antiga > destino_antigo:
                    continue
                origem_nova = mapeamento[origem_antiga]
                destino_novo = mapeamento[destino_antigo]
                novas_adjacencias[origem_nova][destino_novo] = peso
                novas_adjacencias[destino_novo][origem_nova] = peso

        self._rotulos = novos_rotulos
        self._adjacencias = novas_adjacencias
        return mapeamento

    def remover_aresta(self, origem: int, destino: int) -> None:
        self._validar_vertice(origem)
        self._validar_vertice(destino)
        if destino not in self._adjacencias[origem]:
            raise ErroGrafo("A aresta informada não existe.")
        del self._adjacencias[origem][destino]
        del self._adjacencias[destino][origem]

    def componentes_conexas(self) -> list[list[int]]:
        visitados: set[int] = set()
        componentes: list[list[int]] = []
        for inicio in sorted(self._rotulos):
            if inicio in visitados:
                continue
            fila = deque([inicio])
            visitados.add(inicio)
            componente: list[int] = []
            while fila:
                atual = fila.popleft()
                componente.append(atual)
                for vizinho in sorted(self._adjacencias[atual]):
                    if vizinho not in visitados:
                        visitados.add(vizinho)
                        fila.append(vizinho)
            componentes.append(sorted(componente))
        return componentes

    def eh_conexo(self) -> bool:
        return self.numero_vertices > 0 and len(self.componentes_conexas()) == 1

    def formatar_lista_adjacencia(self) -> str:
        linhas: list[str] = []
        for origem in sorted(self._rotulos):
            vizinhos = [
                f"{destino} ({self._rotulos[destino]}, peso {peso})"
                for destino, peso in sorted(self._adjacencias[origem].items())
            ]
            linhas.append(
                f"{origem} - {self._rotulos[origem]}: " + ", ".join(vizinhos)
            )
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Técnica 1 (solução): Dijkstra — menor caminho entre dois vértices
    # ------------------------------------------------------------------

    def dijkstra(self, origem: int) -> tuple[dict[int, int], dict[int, int | None]]:
        """Aplica Dijkstra a partir de *origem* e devolve (distâncias, predecessores).

        distâncias[v]  — custo mínimo de *origem* até *v* (ou -1 se inalcançável).
        predecessores[v] — vértice anterior no caminho mínimo (None para *origem*).
        """
        self._validar_vertice(origem)
        INF = float("inf")
        dist: dict[int, float] = {v: INF for v in self._rotulos}
        pred: dict[int, int | None] = {v: None for v in self._rotulos}
        dist[origem] = 0
        heap: list[tuple[float, int]] = [(0, origem)]

        while heap:
            custo_atual, u = heapq.heappop(heap)
            if custo_atual > dist[u]:
                continue
            for vizinho, peso in self._adjacencias[u].items():
                novo_custo = dist[u] + peso
                if novo_custo < dist[vizinho]:
                    dist[vizinho] = novo_custo
                    pred[vizinho] = u
                    heapq.heappush(heap, (novo_custo, vizinho))

        distancias_int = {
            v: (int(d) if d != INF else -1) for v, d in dist.items()
        }
        return distancias_int, pred

    def reconstruir_caminho(
        self, predecessores: dict[int, int | None], destino: int
    ) -> list[int]:
        """Reconstrói o caminho mínimo até *destino* a partir dos predecessores."""
        self._validar_vertice(destino)
        caminho: list[int] = []
        atual: int | None = destino
        while atual is not None:
            caminho.append(atual)
            atual = predecessores[atual]
        caminho.reverse()
        return caminho

    # ------------------------------------------------------------------
    # Técnica 2: Grau dos vértices
    # ------------------------------------------------------------------

    def graus_vertices(self) -> dict[int, int]:
        """Devolve um dicionário {vértice: grau}."""
        return {v: len(vizinhos) for v, vizinhos in self._adjacencias.items()}

    # ------------------------------------------------------------------
    # Técnica 3: Verificação euleriana
    # ------------------------------------------------------------------

    def verificar_euleriano(self) -> str:
        """Verifica se o grafo admite circuito ou trilha euleriana.

        Critérios (grafo não orientado):
        - Circuito euleriano: grafo conexo e todos os vértices têm grau par.
        - Trilha euleriana:   grafo conexo e exatamente dois vértices têm grau ímpar.
        """
        if self.numero_vertices == 0:
            return "O grafo está vazio."
        if not self.eh_conexo():
            return "O grafo não é conexo — não existe percurso euleriano."

        graus = self.graus_vertices()
        impares = [v for v, g in graus.items() if g % 2 != 0]

        if len(impares) == 0:
            return "O grafo possui CIRCUITO euleriano (todos os vértices têm grau par)."
        if len(impares) == 2:
            v1, v2 = impares
            return (
                f"O grafo possui TRILHA euleriana entre os vértices {v1} "
                f"({self._rotulos[v1]}) e {v2} ({self._rotulos[v2]}) — "
                "exatamente dois vértices têm grau ímpar."
            )
        return (
            f"O grafo NÃO é euleriano ({len(impares)} vértices com grau ímpar; "
            "são necessários 0 ou 2)."
        )

    # ------------------------------------------------------------------
    # Técnica 4: Verificação hamiltoniana (condições suficientes)
    # ------------------------------------------------------------------

    def verificar_hamiltoniano(self) -> str:
        """Verifica condições suficientes para hamiltonicidade.

        Aplica:
        - Teorema de Dirac (1952): se n ≥ 3 e grau_mínimo ≥ n/2 → Hamiltoniano.
        - Teorema de Ore   (1960): se para todo par não adjacente u, v:
              grau(u) + grau(v) ≥ n → Hamiltoniano.
        Caso nenhum teorema se aplique, informa que não é possível garantir.
        """
        n = self.numero_vertices
        if n == 0:
            return "O grafo está vazio."
        if not self.eh_conexo():
            return "O grafo não é conexo — não admite ciclo hamiltoniano."

        graus = self.graus_vertices()

        # Teorema de Dirac
        if n >= 3 and min(graus.values()) >= n / 2:
            return (
                f"O grafo ADMITE ciclo hamiltoniano pelo Teorema de Dirac "
                f"(n={n}, grau mínimo={min(graus.values())} ≥ n/2={n/2:.1f})."
            )

        # Teorema de Ore
        ore_satisfeito = True
        for u in self._rotulos:
            for v in self._rotulos:
                if u >= v:
                    continue
                if v not in self._adjacencias[u]:  # não adjacentes
                    if graus[u] + graus[v] < n:
                        ore_satisfeito = False
                        break
            if not ore_satisfeito:
                break

        if ore_satisfeito:
            return (
                f"O grafo ADMITE ciclo hamiltoniano pelo Teorema de Ore "
                f"(para todo par não adjacente u, v: grau(u)+grau(v) ≥ n={n})."
            )

        return (
            "Nenhum teorema suficiente (Dirac/Ore) garante hamiltonicidade. "
            "Não é possível afirmar com certeza se o grafo admite ciclo hamiltoniano."
        )

    # ------------------------------------------------------------------
    # Técnica 5: Coloração gulosa
    # ------------------------------------------------------------------

    def coloracao_gulosa(self) -> dict[int, int]:
        """Aplica coloração gulosa e devolve {vértice: cor (inteiro ≥ 0)}.

        A cor é o menor inteiro não utilizado pelos vizinhos já coloridos.
        A ordem de coloração segue os vértices em ordem decrescente de grau
        (heurística de saturação simplificada).
        """
        graus = self.graus_vertices()
        ordem = sorted(self._rotulos, key=lambda v: graus[v], reverse=True)
        cores: dict[int, int] = {}
        for v in ordem:
            cores_vizinhos = {cores[viz] for viz in self._adjacencias[v] if viz in cores}
            cor = 0
            while cor in cores_vizinhos:
                cor += 1
            cores[v] = cor
        return cores

    # ------------------------------------------------------------------
    # Utilitário interno
    # ------------------------------------------------------------------

    def _validar_vertice(self, vertice: int) -> None:
        if not isinstance(vertice, int) or isinstance(vertice, bool):
            raise ErroGrafo("O identificador do vértice deve ser inteiro.")
        if vertice not in self._rotulos:
            raise ErroGrafo(f"Vértice {vertice} inexistente.")
