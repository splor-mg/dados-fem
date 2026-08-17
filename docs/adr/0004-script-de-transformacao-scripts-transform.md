# 0004. Script de transformação em `scripts/transform.py`

* Status: aceito
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

O pacote de código do projeto foi reorganizado de `dados_fem/` para `scripts/` (ver `pyproject.toml`, `tests/test_main.py`). As etapas 1 e 3 do pipeline diário já estão definidas no ADR [0003](0003-atualizacao-diaria-via-dpm.md) (`dpm install` e publicação no portal); faltava um lugar concreto para a etapa 2 — a análise/transformação dos dados baixados pelo `dpm` antes da publicação.

Os recursos de origem ficam em `datapackages/siafi/data/*.csv.gz` após o `dpm install`, descritos por `datapackages/siafi/datapackage.json`. Em `data.toml`, o recurso `receita` foi substituído por `credito` (a base correta para esta análise); os recursos atuais do pacote `siafi` são `execucao` e `credito`. O projeto já tem `pandas` e `frictionless[pandas]` como dependências.

## Decisão

Criar `scripts/transform.py` como o script responsável pela etapa de transformação do pipeline: lê os recursos baixados pelo `dpm`, aplica a análise/transformação do projeto e grava o resultado em `data/fem_execucao.csv`, pronto para a etapa de publicação.

Leitura dos recursos: carregar via `frictionless.Package(datapackages/siafi/datapackage.json)`, iterando `package.resources` e convertendo cada um com `resource.to_pandas()`, em vez de `pd.read_csv` direto no `.csv.gz`. O `datapackage.json` já declara o schema de cada campo (tipo, `constraints`, `pattern`); usar o `frictionless` para instanciar o resource faz a inferência/casting de tipos respeitar esse schema, em vez de depender da inferência genérica do pandas — que erraria tipos em colunas como códigos numéricos com zero à esquerda (ex.: `uo_cod`), tratados como `string` no schema.

Regras de transformação (`transform()`):

1. Filtrar cada recurso por `fonte_cod == '71'`.
2. Agregar cada recurso já filtrado por `ano`, `uo_cod`, `acao_cod`, `fonte_cod`, somando (`SUM`) os campos de valor (prefixo `vlr_`) daquele recurso — necessário porque, nessa granularidade de chave, cada recurso tem múltiplas linhas por chave (ex.: `execucao` tem 13.812 linhas para 46 chaves únicas depois do filtro); sem agregar antes, um `JOIN` geraria produto cartesiano e infrutificaria os valores.
3. Fazer um `LEFT JOIN` (`pd.merge(..., on=KEY_FIELDS, how='left')`) encadeado entre os recursos já agregados, usando `credito` como tabela base — todas as combinações de chave de `credito` são mantidas, com os campos de `execucao` (`vlr_empenhado`, `vlr_liquidado`, `vlr_liquidado_retido`, `vlr_pago_orcamentario`, `vlr_pago_financeiro`) preenchidos quando existir a mesma chave, e `NaN` quando não existir (crédito ainda sem execução correspondente).
4. Gravar o resultado em `data/fem_execucao.csv`.

## Alternativas consideradas

* Colocar a lógica de transformação dentro do `scripts/main.py` — descartado por já existir como stub do template; manter a transformação em módulo próprio (`transform.py`) deixa o pipeline mais legível por etapa.
* Fazer a transformação em notebook — descartado por dificultar a execução automatizada diária (ADR 0003).
* Ler os recursos com `pd.read_csv` direto no arquivo `.csv.gz` — descartado por ignorar o schema declarado no `datapackage.json`, deixando a inferência de tipos a cargo do pandas.
* Unir os recursos com `pd.concat` (uma linha por linha de origem, empilhadas) — primeira versão implementada, descartada por não corresponder ao resultado desejado: gerava uma linha por chave *por recurso* (union), em vez de uma linha por chave com os valores de ambos os recursos lado a lado (join).
* `INNER JOIN` ou `FULL OUTER JOIN` em vez de `LEFT JOIN` com `credito` como base — descartados porque o requisito é manter toda combinação de chave de `credito` (crédito orçamentário concedido), mesmo quando ainda não há execução correspondente; um `INNER JOIN` descartaria essas linhas. `FULL OUTER JOIN` não se justifica pela regra orçamentária: não existe execução sem crédito prévio (essa consistência já é garantida em outras bases fora deste pipeline), então não há combinação de `execucao` sem `credito` correspondente a preservar.
* `JOIN`/agregação na granularidade original (sem `GROUP BY` antes) — descartado por gerar produto cartesiano entre as múltiplas linhas de mesma chave em cada recurso.

## Consequências

* O pipeline diário passa a ter uma etapa intermediária explícita e testável, separada do download (`dpm`) e da publicação (portal).
* O dataset final (`data/fem_execucao.csv`) fica restrito a `fonte_cod == '71'`, agregado por `ano`/`uo_cod`/`acao_cod`/`fonte_cod` — perde a granularidade original (por empenho, por processo de compra etc.); qualquer análise que precise dessa granularidade não pode usar este dataset como está.
* `data/` passa a ser o diretório de saída candidato à publicação e será versionado no repositório (ver ADR [0003](0003-atualizacao-diaria-via-dpm.md)); falta decidir se a saída deve ser comprimida antes de publicar.
