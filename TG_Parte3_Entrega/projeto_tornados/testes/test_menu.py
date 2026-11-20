"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: testes de integração das dez opções do menu interativo.
Histórico: 28/09/2026 - Codex - criação dos testes do menu.
"""

import tempfile
import unittest
from pathlib import Path

from projeto_tornados.arquivo_grafo import salvar_grafo
from projeto_tornados.grafo import Grafo
from projeto_tornados.main import executar_menu


class TestMenu(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.caminho = Path(self.temporario.name) / "grafo.txt"

    def tearDown(self):
        self.temporario.cleanup()

    def executar(self, entradas: list[str]) -> str:
        iterador = iter(entradas)
        saidas: list[str] = []
        executar_menu(self.caminho, lambda: next(iterador), saidas.append)
        return "\n".join(saidas)

    def salvar_basico(self, conectado: bool = True) -> None:
        grafo = Grafo()
        grafo.adicionar_vertice("Cidade A, TX")
        grafo.adicionar_vertice("Cidade B, OK")
        if conectado:
            grafo.adicionar_aresta(0, 1, 25)
        salvar_grafo(grafo, self.caminho)

    def test_menu_exibe_titulo_e_dez_opcoes(self):
        texto = self.executar(["10"])

        self.assertIn("ROTAS ESTRATÉGICAS", texto)
        for numero in range(1, 11):
            self.assertIn(f"{numero}.", texto)

    def test_menu_le_e_grava_arquivo(self):
        self.salvar_basico()

        texto = self.executar(["1", "2", "10"])

        self.assertIn("Grafo carregado", texto)
        self.assertIn("Grafo gravado", texto)
        self.assertIn('0 "Cidade A, TX"', self.caminho.read_text(encoding="utf-8"))

    def test_menu_insere_e_remove_vertice(self):
        texto = self.executar(["3", "Cidade A, TX", "3", "Cidade B, OK", "5", "1", "s", "8", "10"])

        self.assertIn("Vértice 0 inserido", texto)
        self.assertIn("Vértice 1 inserido", texto)
        self.assertIn("Vértice removido", texto)
        self.assertIn("0 - Cidade A, TX", texto)
        self.assertNotIn("1 - Cidade B, OK:", texto)

    def test_menu_insere_e_remove_aresta(self):
        texto = self.executar([
            "3", "A", "3", "B", "4", "0", "1", "12",
            "6", "0", "1", "s", "8", "10",
        ])

        self.assertIn("Aresta inserida", texto)
        self.assertIn("Aresta removida", texto)
        self.assertIn("0 - A:", texto)

    def test_menu_mostra_arquivo_e_lista(self):
        self.salvar_basico()

        texto = self.executar(["1", "7", "8", "10"])

        self.assertIn("CONTEÚDO DE grafo.txt", texto)
        self.assertIn('0 "Cidade A, TX"', texto)
        self.assertIn("Cidade B, OK, peso 25", texto)

    def test_menu_mostra_conexidade_e_inaplicabilidade_do_reduzido(self):
        self.salvar_basico(conectado=False)

        texto = self.executar(["1", "9", "10"])

        self.assertIn("desconexo", texto.lower())
        self.assertIn("Componente 1", texto)
        self.assertIn("Componente 2", texto)
        self.assertIn("grafo reduzido não se aplica", texto.lower())

    def test_menu_recupera_de_entrada_invalida(self):
        texto = self.executar(["opção inválida", "3", "", "10"])

        self.assertIn("Opção inválida", texto)
        self.assertIn("não pode estar vazio", texto)
        self.assertIn("Programa encerrado", texto)

    def test_menu_encerra_normalmente(self):
        texto = self.executar(["10"])

        self.assertTrue(texto.rstrip().endswith("Programa encerrado."))


if __name__ == "__main__":
    unittest.main()
