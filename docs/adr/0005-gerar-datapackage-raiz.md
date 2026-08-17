# 0005. Gerar `datapackage.json` na raiz descrevendo o dataset publicado

* Status: aceito
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

O dataset a publicar (`data/fem_execucao.csv`, gerado por `scripts/transform.py` — ver ADR [0004](0004-script-de-transformacao-scripts-transform.md)) precisa de um descritor [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/) na raiz do repositório, documentando seu schema para a publicação no Portal de Dados Abertos de MG (ADR [0002](0002-publicacao-portal-dados-abertos-mg.md), que já define formato CSV + `datapackage.json`).

O projeto já usa esse padrão nos pacotes de origem baixados pelo `dpm` (`datapackages/*/datapackage.json`, hoje só `datapackages/siafi/datapackage.json`), cujos campos já têm `title`, `description` e `constraints` bem documentados — informação que não deve ser reescrita à mão nem perdida ao gerar o novo descritor.

O `frictionless` (já dependência do projeto) oferece [`describe`](https://framework.frictionlessdata.io/docs/console/describe.html), que infere a estrutura de arquivos de dados (schema, tipos) sem precisar de metadado prévio — mas a inferência de tipo é genérica (ex.: campos de código como `ano`, `uo_cod`, `acao_cod`, `fonte_cod` são inferidos como `integer`, quando na verdade são `string` com padrão/`constraints` definidos na fonte).

## Decisão

Criar `scripts/build_datapackage.py`, responsável por gerar `datapackage.json` na raiz do repositório:

1. Rodar `frictionless.describe('data/*.csv', type='package')` para inferir a estrutura de todos os arquivos em `data/` (hoje só `fem_execucao.csv`).
2. Carregar todos os campos (`schema.fields`) de todos os recursos de todos os `datapackages/*/datapackage.json` existentes, indexados por nome de campo.
3. Para cada campo inferido no passo 1 cujo nome coincida com um campo carregado no passo 2, substituir o descritor inferido pelo descritor de origem **na íntegra** (mesmo dict — `title`, `description`, `type`, `constraints` etc.), em vez de só copiar `type`/`title` isoladamente. Campos sem correspondência mantêm o resultado da inferência do `frictionless`.
4. Preencher metadados do pacote (`name`, `title`, `owner_org`, `licenses`) com os valores já definidos na ADR 0002. Os nomes propostos em `scripts/build_datapackage.py` (`PACKAGE_NAME = 'dados_fem'`, `PACKAGE_TITLE = 'Dados FEM'`) foram revisados e aprovados.
5. Gravar o resultado em `datapackage.json`, na raiz do repositório.

Em caso de dois `datapackages/*/datapackage.json` diferentes declararem o mesmo nome de campo com descritores diferentes, o último lido (ordem alfabética dos caminhos, via `Path.glob` ordenado) prevalece — hoje isso não ocorre (os campos compartilhados entre `credito` e `execucao` em `datapackages/siafi` são idênticos), mas fica registrado aqui como comportamento atual, a revisar se surgir conflito real.

## Alternativas consideradas

* Escrever o `datapackage.json` da raiz manualmente — descartado por duplicar informação já mantida nos pacotes de origem e ficar desatualizado a cada mudança de schema na fonte.
* Copiar o `datapackage.json` de `datapackages/siafi/` inteiro e editar — descartado porque descreve os recursos de origem (`credito`, `execucao`), não o dataset transformado (`fem_execucao`, com chaves agregadas e campos de ambos os recursos lado a lado).
* Fazer merge campo a campo copiando só `title`/`description` (preservando o `type` inferido) — descartado porque o pedido explícito foi reaproveitar o descritor de origem **na íntegra**, o que também recupera `constraints` (ex.: `pattern`, `required`) que a inferência genérica do `frictionless` não produz sozinha.

## Consequências

* O schema do dataset publicado fica consistente com a documentação já existente na fonte, sem retrabalho manual, e se atualiza automaticamente se a fonte mudar `title`/`description`/`constraints` de um campo já conhecido.
* Campos que só existem no dataset transformado (nenhum deles hoje, mas pode ocorrer no futuro) continuam sendo apenas inferidos pelo `frictionless`, sem `title`/`description` — ficam mais pobres de documentação até serem tratados manualmente.
* Este script passa a ser mais uma etapa do pipeline diário (ADR [0003](0003-atualizacao-diaria-via-dpm.md)), rodando depois de `scripts/transform.py`, antes da validação (task `validate`, ver ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)) e da publicação no portal. Também remove `TODO` de `scripts/build_datapackage.py` referente ao título provisório.
