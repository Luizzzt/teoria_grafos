"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: testes da geração do grafo a partir dos dados oficiais selecionados.
Histórico: 28/09/2026 - Codex - criação dos testes do gerador.
"""

import unittest
from collections import Counter
from pathlib import Path

from projeto_tornados.gerar_grafo import (
    Cidade,
    Tornado,
    calcular_riscos,
    carregar_cidades_csv,
    carregar_tornados_csv,
    distancia_haversine_km,
    gerar_grafo,
)


BASE = Path(__file__).resolve().parents[1]


class TestGerarGrafo(unittest.TestCase):
    def cidade(self, codigo: str, latitude: float, longitude: float) -> Cidade:
        return Cidade(codigo, codigo, "TX", 1000, latitude, longitude)

    def tornado(
        self, codigo: str, escala: str, latitude: float, longitude: float
    ) -> Tornado:
        return Tornado(codigo, 2020, "01-JAN-20", "TEXAS", escala, latitude, longitude)

    def test_haversine_resultado_conhecido(self):
        origem = self.cidade("A", 0.0, 0.0)
        destino = self.cidade("B", 1.0, 0.0)

        self.assertAlmostEqual(111.195, distancia_haversine_km(origem, destino), places=2)

    def test_risco_combina_quantidade_e_intensidade(self):
        cidades = [self.cidade("A", 0.0, 0.0), self.cidade("B", 0.0, 5.0)]
        tornados = [
            self.tornado("1", "EF0", 0.0, 0.0),
            self.tornado("2", "EF2", 0.1, 0.0),
            self.tornado("3", "UNK", 0.0, 0.1),
            self.tornado("4", "EF0", 0.0, 5.0),
        ]

        riscos = calcular_riscos(cidades, tornados, raio_km=100.0)

        self.assertEqual(1.0, riscos["A"])
        self.assertAlmostEqual(0.2, riscos["B"])

    def test_geracao_pequena_remove_lacos_e_duplicatas(self):
        cidades = [
            self.cidade("A", 0.0, 0.0),
            self.cidade("B", 0.0, 1.0),
            self.cidade("C", 1.0, 0.0),
            self.cidade("D", 1.0, 1.0),
        ]

        grafo = gerar_grafo(cidades, [], vizinhos=2)

        pares = set()
        for origem, vizinhos in grafo.adjacencias.items():
            self.assertNotIn(origem, vizinhos)
            for destino, peso in vizinhos.items():
                self.assertEqual(peso, grafo.adjacencias[destino][origem])
                pares.add(tuple(sorted((origem, destino))))
        self.assertEqual(grafo.numero_arestas, len(pares))
        self.assertTrue(grafo.eh_conexo())

    def test_dataset_entregue_tem_80_vertices_200_arestas_e_eh_conexo(self):
        cidades = carregar_cidades_csv(BASE / "dados" / "cidades.csv")
        tornados = carregar_tornados_csv(BASE / "dados" / "tornados.csv")

        grafo = gerar_grafo(cidades, tornados)

        self.assertEqual(80, grafo.numero_vertices)
        self.assertGreaterEqual(grafo.numero_arestas, 200)
        self.assertTrue(grafo.eh_conexo())
        self.assertEqual(
            {estado: 10 for estado in ("AR", "IA", "KS", "MO", "NE", "OK", "SD", "TX")},
            dict(sorted(Counter(cidade.estado for cidade in cidades).items())),
        )
        pares = set()
        for origem, vizinhos in grafo.adjacencias.items():
            for destino, peso in vizinhos.items():
                self.assertIsInstance(peso, int)
                self.assertGreater(peso, 0)
                self.assertEqual(peso, grafo.adjacencias[destino][origem])
                pares.add(tuple(sorted((origem, destino))))
        self.assertEqual(grafo.numero_arestas, len(pares))


if __name__ == "__main__":
    unittest.main()
