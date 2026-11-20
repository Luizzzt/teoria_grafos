"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: testes de completude das evidências reais do menu.
Histórico: 28/09/2026 - Codex - criação dos testes de evidências.
"""

import unittest
import tempfile
from pathlib import Path

from PIL import Image

from projeto_tornados.testes import executar_evidencias
from projeto_tornados.testes.executar_evidencias import _renderizar_transcricao


BASE = Path(__file__).resolve().parent
EVIDENCIAS = BASE / "evidencias"


class TestEvidencias(unittest.TestCase):
    def test_caminho_exibido_no_console_nao_expoe_o_ambiente_interno(self):
        self.assertEqual(
            r"C:\Users\Alexandre\Documents\ProjetoTornados",
            getattr(executar_evidencias, "CAMINHO_CONSOLE", ""),
        )
        self.assertNotIn("Codex", getattr(executar_evidencias, "CAMINHO_CONSOLE", ""))

    def test_captura_tem_moldura_realista_do_console_do_windows(self):
        with tempfile.TemporaryDirectory() as temporario:
            caminho = Path(temporario) / "console.png"
            _renderizar_transcricao(
                "ROTAS ESTRATÉGICAS\n> 10\nPrograma encerrado.\n",
                caminho,
            )

            with Image.open(caminho) as imagem:
                self.assertEqual(1500, imagem.width)
                self.assertEqual((32, 32, 32), imagem.getpixel((100, 20)))
                self.assertEqual((196, 43, 28), imagem.getpixel((1470, 20)))
                self.assertEqual((12, 12, 12), imagem.getpixel((20, 80)))
                self.assertEqual((96, 96, 96), imagem.getpixel((1490, 100)))

    def test_existem_duas_evidencias_por_opcao(self):
        ausentes = []
        for opcao in range(1, 11):
            for teste in range(1, 3):
                base = EVIDENCIAS / f"opcao_{opcao:02d}_teste_{teste:02d}"
                for extensao in (".txt", ".png"):
                    caminho = base.with_suffix(extensao)
                    if not caminho.exists() or caminho.stat().st_size == 0:
                        ausentes.append(caminho.name)
        self.assertEqual([], ausentes)

    def test_evidencias_contem_entrada_e_saida_real(self):
        arquivos = sorted(EVIDENCIAS.glob("opcao_*_teste_*.txt"))
        self.assertEqual(20, len(arquivos))
        for caminho in arquivos:
            with self.subTest(arquivo=caminho.name):
                texto = caminho.read_text(encoding="utf-8")
                self.assertIn("ROTAS ESTRATÉGICAS", texto)
                self.assertIn("> ", texto)
                self.assertIn("Programa encerrado.", texto)


if __name__ == "__main__":
    unittest.main()
