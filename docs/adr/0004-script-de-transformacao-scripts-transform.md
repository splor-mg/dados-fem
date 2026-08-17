# 0004. Script de transformação em `scripts/transform.py`

* Status: proposto (regras de transformação ainda não definidas)
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

O pacote de código do projeto foi reorganizado de `dados_fem/` para `scripts/` (ver `pyproject.toml`, `tests/test_main.py`). As etapas 1 e 3 do pipeline diário já estão definidas no ADR [0003](0003-atualizacao-diaria-via-dpm.md) (`dpm install` e publicação no portal); faltava um lugar concreto para a etapa 2 — a análise/transformação dos dados baixados pelo `dpm` antes da publicação.

Os recursos de origem (`execucao`, `receita`) ficam em `datapackages/siafi/data/*.csv.gz` após o `dpm install`, descritos por `datapackages/siafi/datapackage.json`. O projeto já tem `pandas` e `frictionless[pandas]` como dependências.

## Decisão

Criar `scripts/transform.py` como o script responsável pela etapa de transformação do pipeline: lê os recursos baixados pelo `dpm`, aplica a análise/transformação do projeto e grava o resultado em `data/`, pronto para a etapa de publicação.

Leitura dos recursos: carregar via `frictionless.Package(datapackages/siafi/datapackage.json).get_resource(name).to_pandas()`, e não via `pd.read_csv` direto no `.csv.gz`. O `datapackage.json` já declara o schema de cada campo (tipo, `constraints`, `pattern`); usar o `frictionless` para instanciar o resource faz a inferência/casting de tipos respeitar esse schema, em vez de depender da inferência genérica do pandas — que erraria tipos em colunas como códigos numéricos com zero à esquerda (ex.: `mes_cod`, `uo_cod`), tratados como `string` no schema.

Neste primeiro rascunho o restante do script faz apenas *passthrough* dos dados (lê, carrega via `frictionless` e regrava sem alterar o conteúdo), como esqueleto do pipeline — as regras reais de análise/transformação (filtros, agregações, colunas derivadas) ficam marcadas como `TODO` no próprio arquivo e ainda precisam ser definidas.

## Alternativas consideradas

* Colocar a lógica de transformação dentro do `scripts/main.py` — descartado por já existir como stub do template; manter a transformação em módulo próprio (`transform.py`) deixa o pipeline mais legível por etapa.
* Fazer a transformação em notebook — descartado por dificultar a execução automatizada diária (ADR 0003).
* Ler os recursos com `pd.read_csv` direto no arquivo `.csv.gz` — descartado por ignorar o schema declarado no `datapackage.json`, deixando a inferência de tipos a cargo do pandas.

## Consequências

* O pipeline diário passa a ter uma etapa intermediária explícita e testável, separada do download (`dpm`) e da publicação (portal).
* Enquanto as regras de transformação não forem definidas, o dataset gerado em `data/` é equivalente ao dado bruto de origem (apenas com tipos corrigidos pelo schema) — não deve ser publicado como está.
* `data/` passa a ser o diretório de saída candidato à publicação; falta decidir se ele é versionado no repositório ou tratado como artefato de build (gerado a cada execução, sem commit). Hoje o `transform.py` grava CSV sem compressão — o arquivo `execucao.csv` já sai com ~114 MB (contra 18 MB do `.csv.gz` de origem); falta decidir se a saída deve ser comprimida antes de publicar.
