"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: testes do gerador do relatório acadêmico.
Histórico: 28/09/2026 - Codex - criação do teste de compatibilidade de estilos.
"""

import unittest

from docx import Document

from projeto_tornados.relatorio.construir_relatorio import (
    MODELO,
    calcular_tamanho_imagem,
    configurar_estilos,
    preparar_template,
)


class TestRelatorio(unittest.TestCase):
    def test_configuracao_cria_estilos_de_titulo_ausentes_no_modelo(self):
        documento = Document(MODELO)

        configurar_estilos(documento)

        nomes = {estilo.name for estilo in documento.styles}
        self.assertTrue(
            {"Heading 1", "Heading 2", "Heading 3", "List Bullet"}.issubset(nomes)
        )

    def test_imagem_vertical_respeita_largura_e_altura_maximas(self):
        largura, altura = calcular_tamanho_imagem(1450, 2470, 15.5, 17.0)

        self.assertLessEqual(largura, 15.5)
        self.assertLessEqual(altura, 17.0)
        self.assertAlmostEqual(largura / altura, 1450 / 2470, places=4)

    def test_preparacao_reutiliza_e_preenche_a_tabela_original_do_template(self):
        documento = Document(MODELO)
        tabela_original = documento.tables[0]._tbl

        preparar_template(documento)

        self.assertIs(documento.tables[0]._tbl, tabela_original)
        self.assertEqual(len(documento.tables), 1)
        self.assertEqual(len(documento.tables[0].rows), 4)
        self.assertEqual(len(documento.tables[0].columns), 2)
        self.assertEqual(
            [[celula.text for celula in linha.cells] for linha in documento.tables[0].rows],
            [
                ["Nome do Integrante", "RA"],
                ["Alexandre Toledo Ponton Yerovi", "10426978"],
                ["Luiz Fernando Ferrari Batistela", "10427397"],
                ["", ""],
            ],
        )
        texto = "\n".join(paragrafo.text for paragrafo in documento.paragraphs)
        self.assertIn("Parte 2", texto)
        self.assertNotIn("Parte 1", texto)
        self.assertNotIn("O relatório deve conter", texto)


if __name__ == "__main__":
    unittest.main()
