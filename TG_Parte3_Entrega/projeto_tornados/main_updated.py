"""
Integrantes: Alexandre Toledo Ponton Yerovi - RA 10426978; Luiz Fernando Ferrari Batistela - RA 10427397.
Resumo: menu interativo para manutenção e análise do grafo de cidades.
Histórico: 28/09/2026 - Codex - implementação das dez opções obrigatórias.
         19/11/2026 - Codex - adição das opções 11-15: Dijkstra, grau dos vértices,
                               verificação euleriana, verificação hamiltoniana e coloração gulosa.
"""

from collections.abc import Callable
from pathlib import Path

from .arquivo_grafo import (
    ErroArquivoGrafo,
    carregar_grafo,
    formatar_conteudo_arquivo,
    salvar_grafo,
)
from .grafo import ErroGrafo, Grafo


TITULO = "ROTAS ESTRATÉGICAS DE EVACUAÇÃO EM REGIÕES AFETADAS POR TORNADOS"
OPCOES = (
    "1. Ler dados do arquivo grafo.txt",
    "2. Gravar dados no arquivo grafo.txt",
    "3. Inserir vértice",
    "4. Inserir aresta",
    "5. Remover vértice",
    "6. Remover aresta",
    "7. Mostrar conteúdo do arquivo",
    "8. Mostrar grafo como lista de adjacência",
    "9. Apresentar conexidade e grafo reduzido",
    "10. Encontrar menor caminho (Dijkstra)",
    "11. Analisar grau dos vértices",
    "12. Verificar se é grafo euleriano",
    "13. Verificar se admite ciclo hamiltoniano",
    "14. Coloração do grafo (número cromático)",
    "15. Encerrar a aplicação",
)


def executar_menu(
    caminho_padrao: Path,
    entrada: Callable[[], str] = input,
    saida: Callable[[str], None] = print,
) -> None:
    """Executa o menu até que a opção de encerramento seja selecionada."""
    grafo = Grafo()
    caminho_padrao = Path(caminho_padrao)

    while True:
        _mostrar_menu(saida)
        opcao = _perguntar("Escolha uma opção:", entrada, saida).strip()
        try:
            if opcao == "1":
                grafo = carregar_grafo(caminho_padrao)
                saida(
                    f"Grafo carregado: {grafo.numero_vertices} vértices e "
                    f"{grafo.numero_arestas} arestas."
                )
            elif opcao == "2":
                salvar_grafo(grafo, caminho_padrao)
                saida(f"Grafo gravado em {caminho_padrao.name}.")
            elif opcao == "3":
                rotulo = _perguntar("Rótulo do novo vértice:", entrada, saida)
                indice = grafo.adicionar_vertice(rotulo)
                saida(f"Vértice {indice} inserido com sucesso.")
            elif opcao == "4":
                origem = _ler_inteiro("Vértice de origem:", entrada, saida)
                destino = _ler_inteiro("Vértice de destino:", entrada, saida)
                peso = _ler_inteiro("Peso inteiro positivo:", entrada, saida)
                grafo.adicionar_aresta(origem, destino, peso)
                saida("Aresta inserida com sucesso.")
            elif opcao == "5":
                vertice = _ler_inteiro("Vértice a remover:", entrada, saida)
                if _confirmar(entrada, saida):
                    grafo.remover_vertice(vertice)
                    saida("Vértice removido e índices atualizados.")
                else:
                    saida("Remoção cancelada.")
            elif opcao == "6":
                origem = _ler_inteiro("Vértice de origem:", entrada, saida)
                destino = _ler_inteiro("Vértice de destino:", entrada, saida)
                if _confirmar(entrada, saida):
                    grafo.remover_aresta(origem, destino)
                    saida("Aresta removida com sucesso.")
                else:
                    saida("Remoção cancelada.")
            elif opcao == "7":
                saida(f"CONTEÚDO DE {caminho_padrao.name}")
                saida(formatar_conteudo_arquivo(caminho_padrao).rstrip())
            elif opcao == "8":
                saida("LISTA DE ADJACÊNCIA")
                saida(grafo.formatar_lista_adjacencia() or "Grafo vazio.")
            elif opcao == "9":
                _mostrar_conexidade(grafo, saida)
            elif opcao == "10":
                _executar_dijkstra(grafo, entrada, saida)
            elif opcao == "11":
                _mostrar_graus(grafo, saida)
            elif opcao == "12":
                saida(grafo.verificar_euleriano())
            elif opcao == "13":
                saida(grafo.verificar_hamiltoniano())
            elif opcao == "14":
                _mostrar_coloracao(grafo, saida)
            elif opcao == "15":
                saida("Programa encerrado.")
                return
            else:
                saida("Opção inválida. Digite um número de 1 a 15.")
        except (ErroGrafo, ErroArquivoGrafo, ValueError) as erro:
            saida(f"Erro: {erro}")


def main() -> None:
    executar_menu(Path(__file__).with_name("grafo.txt"))


def _mostrar_menu(saida: Callable[[str], None]) -> None:
    saida("")
    saida(TITULO)
    saida("=" * len(TITULO))
    for opcao in OPCOES:
        saida(opcao)


def _perguntar(
    mensagem: str, entrada: Callable[[], str], saida: Callable[[str], None]
) -> str:
    saida(mensagem)
    return entrada()


def _ler_inteiro(
    mensagem: str, entrada: Callable[[], str], saida: Callable[[str], None]
) -> int:
    valor = _perguntar(mensagem, entrada, saida).strip()
    try:
        return int(valor)
    except ValueError as erro:
        raise ValueError(f"'{valor}' não é um número inteiro.") from erro


def _confirmar(
    entrada: Callable[[], str], saida: Callable[[str], None]
) -> bool:
    resposta = _perguntar("Confirma a remoção? (s/n):", entrada, saida)
    return resposta.strip().casefold() in {"s", "sim"}


def _mostrar_conexidade(grafo: Grafo, saida: Callable[[str], None]) -> None:
    componentes = grafo.componentes_conexas()
    if grafo.eh_conexo():
        saida("O grafo é conexo.")
    else:
        saida(f"O grafo é desconexo e possui {len(componentes)} componentes.")
    for numero, componente in enumerate(componentes, 1):
        itens = ", ".join(
            f"{indice} ({grafo.rotulos[indice]})" for indice in componente
        )
        saida(f"Componente {numero}: {itens}")
    saida("O grafo reduzido não se aplica ao tipo 2, que é não orientado.")


def _executar_dijkstra(
    grafo: Grafo,
    entrada: Callable[[], str],
    saida: Callable[[str], None],
) -> None:
    """Calcula e exibe o menor caminho entre dois vértices via Dijkstra."""
    saida(f"Vértices disponíveis: 0 a {grafo.numero_vertices - 1}")
    origem = _ler_inteiro("Vértice de origem:", entrada, saida)
    destino = _ler_inteiro("Vértice de destino:", entrada, saida)

    distancias, predecessores = grafo.dijkstra(origem)

    if distancias[destino] == -1:
        saida(
            f"Não existe caminho entre {origem} ({grafo.rotulos[origem]}) "
            f"e {destino} ({grafo.rotulos[destino]})."
        )
        return

    caminho = grafo.reconstruir_caminho(predecessores, destino)
    rotulos_caminho = " → ".join(
        f"{v} ({grafo.rotulos[v]})" for v in caminho
    )
    saida(f"Menor caminho de {origem} até {destino}:")
    saida(f"  Rota: {rotulos_caminho}")
    saida(f"  Custo total: {distancias[destino]}")


def _mostrar_graus(grafo: Grafo, saida: Callable[[str], None]) -> None:
    """Exibe o grau de cada vértice com estatísticas."""
    if grafo.numero_vertices == 0:
        saida("Grafo vazio.")
        return
    graus = grafo.graus_vertices()
    saida("GRAU DOS VÉRTICES")
    saida("-" * 40)
    for v in sorted(graus):
        saida(f"  {v:3d} - {grafo.rotulos[v]}: grau {graus[v]}")
    saida("-" * 40)
    saida(f"  Grau mínimo : {min(graus.values())}")
    saida(f"  Grau máximo : {max(graus.values())}")
    total = sum(graus.values())
    saida(f"  Soma total  : {total}  (= 2 × {total // 2} arestas)")


def _mostrar_coloracao(grafo: Grafo, saida: Callable[[str], None]) -> None:
    """Exibe a coloração gulosa do grafo e o número cromático encontrado."""
    if grafo.numero_vertices == 0:
        saida("Grafo vazio.")
        return
    cores = grafo.coloracao_gulosa()
    numero_cromatico = max(cores.values()) + 1
    saida("COLORAÇÃO DO GRAFO (algoritmo guloso)")
    saida("-" * 40)
    # Agrupar vértices por cor
    grupos: dict[int, list[int]] = {}
    for v, cor in cores.items():
        grupos.setdefault(cor, []).append(v)
    for cor in sorted(grupos):
        vertices = ", ".join(
            f"{v} ({grafo.rotulos[v]})" for v in sorted(grupos[cor])
        )
        saida(f"  Cor {cor}: {vertices}")
    saida("-" * 40)
    saida(f"  Número cromático (guloso): {numero_cromatico} cor(es)")
    saida(
        "  Obs.: coloração gulosa pode não ser ótima; "
        "o número cromático real pode ser menor."
    )


if __name__ == "__main__":
    main()
