# Architecture Decision Records (ADR)

Esta pasta reúne os **ADRs** (*Architecture Decision Records*) do projeto `dados-fem`: registros curtos que documentam decisões arquiteturais/técnicas relevantes, o contexto em que foram tomadas e as consequências esperadas.

## Por que usar ADR aqui

O projeto tem como objetivo publicar um conjunto de dados abertos no [Portal de Dados Abertos de Minas Gerais](https://dados.mg.gov.br/), com atualização diária automatizada via [`dpm`](https://github.com/splor-mg/dpm). Decisões como formato de publicação, periodicidade, ferramentas de automação e responsabilidades precisam ficar registradas para consulta futura — tanto pela equipe atual quanto por quem vier a dar manutenção no projeto.

## Convenção adotada

* Um arquivo por decisão, nomeado `NNNN-titulo-curto-em-kebab-case.md`, com `NNNN` sequencial e sem reaproveitar números.
* Use o [modelo](template.md) como ponto de partida.
* Status possíveis: `proposto`, `aceito`, `substituído (ver ADR-000X)`, `rejeitado`, `obsoleto`.
* ADRs não são editados retroativamente para mudar a decisão — se a decisão muda, cria-se um novo ADR que substitui o anterior (atualizando o `Status` do antigo para apontar para o novo).

## Índice

| ADR | Título | Status |
|---|---|---|
| [0001](0001-adotar-adr.md) | Adotar Architecture Decision Records | aceito |
| [0002](0002-publicacao-portal-dados-abertos-mg.md) | Publicar o conjunto de dados no Portal de Dados Abertos de MG | proposto (falta fluxo de validação do portal) |
| [0003](0003-atualizacao-diaria-via-dpm.md) | Atualização diária dos dados via `dpm` | proposto (falta detalhar etapas do pipeline) |
| [0004](0004-script-de-transformacao-scripts-transform.md) | Script de transformação em `scripts/transform.py` | aceito |

> Rascunho iniciado em 2026-08-17. Decisões centrais já resolvidas em 2026-08-17; pontos remanescentes seguem marcados com `[A DEFINIR]` em cada ADR até serem confirmados junto ao manual do portal e à implementação do pipeline.
