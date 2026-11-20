# Rotas Estratégicas de Evacuação em Regiões Afetadas por Tornados

Projeto da disciplina Teoria dos Grafos da Universidade Presbiteriana Mackenzie.

## Integrantes

- Alexandre Toledo Ponton Yerovi - RA 10426978
- Luiz Fernando Ferrari Batistela - RA 10427397

## Objetivo

O programa representa 80 cidades de oito estados dos Estados Unidos como um grafo não orientado com peso nas arestas. As conexões são corredores estratégicos aproximados entre cidades próximas. O peso combina distância geográfica e risco histórico de tornados. O protótipo não representa navegação rodoviária rua a rua.

## Execução

Use Python 3.11 ou superior. A partir da pasta que contém `projeto_tornados`, execute:

```powershell
python -m projeto_tornados.main
```

O arquivo `grafo.txt` já está pronto, com 80 vértices e 314 arestas. No menu, use primeiro a opção 1 para carregá-lo.

## Testes

```powershell
python -m unittest discover -s projeto_tornados/testes -v
```

## Regeneração do grafo

Os arquivos `dados/cidades.csv` e `dados/tornados.csv` contêm os subconjuntos oficiais usados na entrega. Não é necessário acesso à internet.

```powershell
python -m projeto_tornados.gerar_grafo
```

## Evidências

As vinte transcrições e imagens em `testes/evidencias` correspondem a duas execuções por opção do menu. Para regenerar as imagens é necessário Pillow:

```powershell
python -m projeto_tornados.testes.executar_evidencias
```

## Estrutura

- `grafo.py`: estrutura, validações e conexidade.
- `arquivo_grafo.py`: leitura e gravação do formato solicitado.
- `main.py`: menu interativo.
- `gerar_grafo.py`: transformação dos dados em grafo.
- `dados/`: bases locais e documentação das fontes.
- `testes/`: testes automatizados e evidências.
- `relatorio/`: relatório editável da Parte 2.

## Fontes

As cidades e populações são do U.S. Census Bureau. Os registros de tornados são da NOAA Storm Events Database. URLs, período, campos e transformações estão documentados em `dados/fontes.md`.
