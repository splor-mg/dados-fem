# 0001. Adotar Architecture Decision Records

* Status: proposto
* Data: 2026-08-17
* Responsável(is): [A DEFINIR]

## Contexto

O `dados-fem` é um projeto de análise de dados cujo objetivo final é publicar um conjunto de dados abertos no Portal de Dados Abertos de Minas Gerais, com atualização diária automatizada. Ao longo do desenvolvimento serão tomadas decisões (fonte dos dados, forma de tratamento, periodicidade, ferramentas de automação, licenciamento) que precisam ficar registradas para que a equipe — atual e futura — entenda o *porquê* e não apenas o *como*.

## Decisão

Adotar ADRs (*Architecture Decision Records*) na pasta [`docs/adr/`](README.md) para registrar decisões relevantes do projeto, seguindo o [modelo](template.md) definido no índice desta pasta.

## Alternativas consideradas

* Documentar tudo apenas no `README.md` — descartado por misturar contexto histórico com documentação de uso corrente, dificultando a leitura de ambos.
* Não documentar decisões formalmente — descartado por gerar perda de conhecimento em caso de troca de equipe.

## Consequências

* Toda decisão técnica relevante deve gerar (ou atualizar) um ADR antes ou logo após ser implementada.
* Aumenta o esforço de documentação, mas reduz o custo de retomada do projeto por outra pessoa.
