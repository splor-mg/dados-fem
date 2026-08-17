# 0002. Publicar o conjunto de dados no Portal de Dados Abertos de MG

* Status: proposto (falta confirmar o fluxo de validação/homologação do portal)
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

O objetivo do `dados-fem` é disponibilizar publicamente, como dado aberto, um conjunto de dados tratado a partir de fonte(s) já existente(s) no ecossistema SPLOR (ex.: pacote `siafi` referenciado em [`data.toml`](../../data.toml), com os recursos `execucao` e `credito`). A publicação será feita no [Portal de Dados Abertos do Estado de Minas Gerais](https://dados.mg.gov.br/), plataforma oficial baseada em CKAN, cujo processo de publicação está descrito no [Manual do Portal de Dados Abertos de MG](https://transparencia-mg.github.io/manual-dados-mg/0.1/).

Ainda falta confirmar, junto ao manual/equipe de transparência, o fluxo de validação/homologação exigido pelo portal antes da publicação (`[A DEFINIR]`). Os demais itens obrigatórios do processo de publicação já foram definidos (ver Decisão).

## Decisão

Publicar o conjunto de dados resultante da análise no Portal de Dados Abertos de Minas Gerais (dados.mg.gov.br), como dataset aberto, seguindo o processo de documentação e validação descrito no manual oficial.

* Organização (`owner_org`): `secretaria-de-estado-de-planejamento-e-gestao-seplag` — mesma organização já usada pela fonte `siafi`, mantendo consistência com o dado de origem.
* Formato(s) de publicação: CSV + `datapackage.json` (schema descrito no padrão Frictionless Data Package, já usado no projeto).
* Licença: Creative Commons CC-BY 4.0.
* Nome/slug do dataset no portal: `dados-fem`.
* Fluxo de validação/homologação exigido pelo portal: `[A DEFINIR]`.

## Alternativas consideradas

* Publicar apenas internamente (compartilhamento restrito) — descartado, pois o requisito explícito do projeto é dado **aberto**, no portal oficial do Estado.
* Publicar em outro canal (ex.: repositório GitHub público, como já é feito para `dados-siafi-2026`) — pode ser complementar, mas não substitui a publicação no portal oficial, que é o canal de referência para dados abertos do governo de MG.

## Consequências

* O projeto passa a ter um compromisso de qualidade e estabilidade de schema com um público externo (usuários do portal), não apenas com consumidores internos.
* Mudanças na estrutura dos dados publicados precisam considerar impacto em quem já consome o dataset aberto.
* É necessário validar os metadados exigidos pelo portal antes de cada publicação (ver ADR [0003](0003-atualizacao-diaria-via-dpm.md) para a automação da atualização).
