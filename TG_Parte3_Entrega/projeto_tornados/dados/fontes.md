# Fontes dos dados

## Cidades e população

Os 80 vértices representam as dez cidades incorporadas com maior estimativa populacional de 2025 em cada um dos estados AR, IA, KS, MO, NE, OK, SD e TX.

- U.S. Census Bureau Population Estimates Program, arquivo nacional `sub-est2025.csv`: https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025.csv
- U.S. Census Bureau Gazetteer Files 2025, arquivo nacional de lugares: https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_place_national.zip

As tabelas foram associadas pelo código GEOID formado pelos campos `STATE` e `PLACE`. Foram preservados nome, sigla do estado, população estimada, latitude e longitude. Acesso em 28/09/2026.

## Tornados

Foram usados eventos classificados como `Tornado` nos arquivos anuais de detalhes da NOAA Storm Events Database, de 2015 a 2024. Foram preservados o identificador do evento, o ano, a data, o estado, a escala EF e as coordenadas iniciais disponíveis.

- NOAA National Centers for Environmental Information, diretório de arquivos CSV: https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
- Documentação do formato: https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/Storm-Data-Bulk-csv-Format.pdf

Somente eventos dos oito estados do estudo com coordenadas disponíveis foram mantidos. O subconjunto entregue contém 5.427 registros. Acesso em 28/09/2026.

## Transformação

O risco bruto de uma cidade corresponde à soma das intensidades dos tornados ocorridos em raio de 100 km. Um evento EF0 vale 1, EF1 vale 2 e assim sucessivamente até EF5, que vale 6. Escalas ausentes ou desconhecidas recebem valor 1. Os riscos são normalizados pelo maior valor observado entre as 80 cidades.

Cada cidade é inicialmente ligada às seis cidades mais próximas por distância de Haversine. Duplicidades são removidas e as menores ligações adicionais garantem pelo menos 200 arestas e uma única componente conexa. O peso final é a distância em quilômetros multiplicada por `1 + risco médio normalizado`, arredondada para inteiro positivo.
