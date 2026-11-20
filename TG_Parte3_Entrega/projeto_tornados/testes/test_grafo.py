"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: testes da estrutura de grafo não orientado e ponderado.
Histórico: 28/09/2026 - Codex - criação dos testes da classe Grafo.
"""

import unittest

from projeto_tornados.grafo import ErroGrafo, Grafo


class TestGrafo(unittest.TestCase):
    def test_adiciona_vertices_e_aresta_nao_orientada(self):
        grafo = Grafo()
        a = grafo.adicionar_vertice("A")
        b = grafo.adicionar_vertice("B")

        grafo.adicionar_aresta(a, b, 7)

        self.assertEqual(2, grafo.numero_vertices)
        self.assertEqual(1, grafo.numero_arestas)
        self.assertEqual(7, grafo.adjacencias[a][b])
        self.assertEqual(7, grafo.adjacencias[b][a])

    def test_rejeita_rotulo_repetido_e_aresta_invalida(self):
        grafo = Grafo()
        a = grafo.adicionar_vertice("A")
        b = grafo.adicionar_vertice("B")
        grafo.adicionar_aresta(a, b, 3)

        with self.assertRaises(ErroGrafo):
            grafo.adicionar_vertice(" A ")
        with self.assertRaises(ErroGrafo):
            grafo.adicionar_aresta(a, a, 1)
        with self.assertRaises(ErroGrafo):
            grafo.adicionar_aresta(a, b, 9)
        with self.assertRaises(ErroGrafo):
            grafo.adicionar_aresta(a, 99, 2)
        with self.assertRaises(ErroGrafo):
            grafo.adicionar_aresta(a, b, 0)

    def test_remove_vertice_reindexa_rotulos_e_arestas(self):
        grafo = Grafo()
        for rotulo in ("A", "B", "C", "D"):
            grafo.adicionar_vertice(rotulo)
        grafo.adicionar_aresta(0, 1, 1)
        grafo.adicionar_aresta(0, 2, 2)
        grafo.adicionar_aresta(2, 3, 3)

        mapeamento = grafo.remover_vertice(1)

        self.assertEqual({0: 0, 2: 1, 3: 2}, mapeamento)
        self.assertEqual({0: "A", 1: "C", 2: "D"}, grafo.rotulos)
        self.assertEqual({1: 2}, grafo.adjacencias[0])
        self.assertEqual({0: 2, 2: 3}, grafo.adjacencias[1])
        self.assertEqual({1: 3}, grafo.adjacencias[2])

    def test_remove_aresta_nos_dois_sentidos(self):
        grafo = Grafo()
        grafo.adicionar_vertice("A")
        grafo.adicionar_vertice("B")
        grafo.adicionar_aresta(0, 1, 5)

        grafo.remover_aresta(0, 1)

        self.assertNotIn(1, grafo.adjacencias[0])
        self.assertNotIn(0, grafo.adjacencias[1])
        self.assertEqual(0, grafo.numero_arestas)

    def test_componentes_conexas_em_ordem_deterministica(self):
        grafo = Grafo()
        for rotulo in ("A", "B", "C", "D", "E"):
            grafo.adicionar_vertice(rotulo)
        grafo.adicionar_aresta(0, 1, 1)
        grafo.adicionar_aresta(2, 3, 1)

        self.assertEqual([[0, 1], [2, 3], [4]], grafo.componentes_conexas())
        self.assertFalse(grafo.eh_conexo())

    def test_formata_lista_de_adjacencia(self):
        grafo = Grafo()
        grafo.adicionar_vertice("Cidade A, TX")
        grafo.adicionar_vertice("Cidade B, OK")
        grafo.adicionar_aresta(0, 1, 42)

        texto = grafo.formatar_lista_adjacencia()

        self.assertEqual(
            '0 - Cidade A, TX: 1 (Cidade B, OK, peso 42)\n'
            '1 - Cidade B, OK: 0 (Cidade A, TX, peso 42)',
            texto,
        )


if __name__ == "__main__":
    unittest.main()
