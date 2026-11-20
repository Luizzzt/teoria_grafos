"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: testes de leitura e gravação do formato grafo.txt.
Histórico: 28/09/2026 - Codex - criação dos testes de persistência.
"""

import tempfile
import unittest
from pathlib import Path

from projeto_tornados.arquivo_grafo import (
    ErroArquivoGrafo,
    carregar_grafo,
    salvar_grafo,
)
from projeto_tornados.grafo import Grafo


class TestArquivoGrafo(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.caminho = Path(self.temporario.name) / "grafo.txt"

    def tearDown(self):
        self.temporario.cleanup()

    def _grafo_basico(self) -> Grafo:
        grafo = Grafo()
        grafo.adicionar_vertice("Cidade A, TX")
        grafo.adicionar_vertice("Cidade B, OK")
        grafo.adicionar_aresta(0, 1, 25)
        return grafo

    def test_salva_no_formato_tipo_2(self):
        salvar_grafo(self._grafo_basico(), self.caminho)

        linhas = self.caminho.read_text(encoding="utf-8").splitlines()

        self.assertEqual("2", linhas[0])
        self.assertEqual("2", linhas[1])
        self.assertEqual('0 "Cidade A, TX"', linhas[2])
        self.assertEqual('1 "Cidade B, OK"', linhas[3])
        self.assertEqual("1", linhas[4])
        self.assertEqual("0 1 25", linhas[5])

    def test_round_trip_preserva_rotulos_pesos_e_quantidades(self):
        original = self._grafo_basico()
        salvar_grafo(original, self.caminho)

        carregado = carregar_grafo(self.caminho)

        self.assertEqual(original.rotulos, carregado.rotulos)
        self.assertEqual(original.adjacencias, carregado.adjacencias)
        self.assertEqual(2, carregado.numero_vertices)
        self.assertEqual(1, carregado.numero_arestas)

    def test_round_trip_preserva_acentos_e_espacos(self):
        grafo = Grafo()
        grafo.adicionar_vertice("São José, MO")
        salvar_grafo(grafo, self.caminho)

        carregado = carregar_grafo(self.caminho)

        self.assertEqual("São José, MO", carregado.rotulos[0])

    def test_rejeita_tipo_diferente_de_2(self):
        self.caminho.write_text('6\n1\n0 "A"\n0\n', encoding="utf-8")

        with self.assertRaisesRegex(ErroArquivoGrafo, "tipo 2"):
            carregar_grafo(self.caminho)

    def test_rejeita_contagens_indices_e_pesos_invalidos(self):
        casos = [
            '2\n2\n0 "A"\n1\n0\n',
            '2\n1\n4 "A"\n0\n',
            '2\n2\n0 "A"\n1 "B"\n1\n0 1 0\n',
            '2\n2\n0 "A"\n1 "B"\n1\n0 3 2\n',
            '2\n1\n0 "A"\n0\nconteudo extra\n',
        ]
        for conteudo in casos:
            with self.subTest(conteudo=conteudo):
                self.caminho.write_text(conteudo, encoding="utf-8")
                with self.assertRaises(ErroArquivoGrafo):
                    carregar_grafo(self.caminho)

    def test_leitura_falha_sem_alterar_grafo_existente(self):
        existente = self._grafo_basico()
        antes = existente.adjacencias
        self.caminho.write_text("arquivo inválido", encoding="utf-8")

        with self.assertRaises(ErroArquivoGrafo):
            carregar_grafo(self.caminho)

        self.assertEqual(antes, existente.adjacencias)
        self.assertEqual(2, existente.numero_vertices)


if __name__ == "__main__":
    unittest.main()
