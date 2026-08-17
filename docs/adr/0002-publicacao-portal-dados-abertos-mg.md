# 0002. Publicar o conjunto de dados no Portal de Dados Abertos de MG

* Status: proposto
* Data: 2026-08-17
* Responsável(is): [A DEFINIR]

## Contexto

O objetivo do `dados-fem` é disponibilizar publicamente, como dado aberto, um conjunto de dados tratado a partir de fonte(s) já existente(s) no ecossistema SPLOR (ex.: pacote `siafi` referenciado em [`data.toml`](../../data.toml), com os recursos `execucao` e `receita`). A publicação será feita no [Portal de Dados Abertos do Estado de Minas Gerais](https://dados.mg.gov.br/), plataforma oficial baseada em CKAN, cujo processo de publicação está descrito no [Manual do Portal de Dados Abertos de MG](https://transparencia-mg.github.io/manual-dados-mg/0.1/).

Ainda faltam definir, junto ao manual/equipe de transparência, itens obrigatórios do processo de publicação:

* Formatos de arquivo aceitos e formato(s) escolhido(s) para este conjunto (ex.: CSV).
* Organização (`owner_org`) responsável pelo dataset no portal.
* Licença de uso dos dados.
* Nome, título e descrição do conjunto de dados como aparecerão no portal.
* Fluxo de validação/homologação exigido pelo portal antes da publicação.

## Decisão

Publicar o conjunto de dados resultante da análise no Portal de Dados Abertos de Minas Gerais (dados.mg.gov.br), como dataset aberto, seguindo o processo de documentação e validação descrito no manual oficial.

* Organização (`owner_org`): `[A DEFINIR]` (a fonte `siafi` usada como insumo já referencia `secretaria-de-estado-de-planejamento-e-gestao-seplag` — confirmar se esta é também a organização do dataset publicado).
* Formato(s) de publicação: `[A DEFINIR]`
* Licença: `[A DEFINIR]`
* Nome/slug do dataset no portal: `[A DEFINIR]`

## Alternativas consideradas

* Publicar apenas internamente (compartilhamento restrito) — descartado, pois o requisito explícito do projeto é dado **aberto**, no portal oficial do Estado.
* Publicar em outro canal (ex.: repositório GitHub público, como já é feito para `dados-siafi-2026`) — pode ser complementar, mas não substitui a publicação no portal oficial, que é o canal de referência para dados abertos do governo de MG.

## Consequências

* O projeto passa a ter um compromisso de qualidade e estabilidade de schema com um público externo (usuários do portal), não apenas com consumidores internos.
* Mudanças na estrutura dos dados publicados precisam considerar impacto em quem já consome o dataset aberto.
* É necessário validar os metadados exigidos pelo portal antes de cada publicação (ver ADR [0003](0003-atualizacao-diaria-via-dpm.md) para a automação da atualização).
