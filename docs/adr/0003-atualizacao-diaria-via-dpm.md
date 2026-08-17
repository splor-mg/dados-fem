# 0003. Atualização diária dos dados via `dpm`

* Status: proposto
* Data: 2026-08-17
* Responsável(is): [A DEFINIR]

## Contexto

O conjunto de dados a ser publicado no Portal de Dados Abertos de MG (ver ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)) precisa ser atualizado diariamente, refletindo a fonte de origem (`siafi`, descrita em [`data.toml`](../../data.toml)). O projeto já depende da biblioteca [`dpm`](https://github.com/splor-mg/dpm) (Data Package Manager), que instala/baixa recursos descritos em um `datapackage.json` (padrão [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/)) via `dpm install`.

Ainda não estão definidos:

* Onde/como a rotina diária será executada (ex.: GitHub Actions agendado via `cron`, outro orquestrador já usado pela equipe).
* Horário de execução e fuso horário de referência.
* Etapas do pipeline após o `dpm install` (transformação/análise em `dados_fem/main.py`, geração do artefato final, publicação no portal).
* Tratamento de falhas: o que acontece se a fonte (`dados-siafi-2026`) não atualizar, estiver indisponível, ou o schema mudar.
* Alertas/notificação em caso de falha na atualização diária.

## Decisão

Usar `dpm` como ferramenta de obtenção dos dados de origem, orquestrada por uma rotina agendada para execução diária, que:

1. Executa `dpm install` para baixar a versão mais recente do(s) datapackage(s) configurado(s) em `data.toml`.
2. Executa a análise/transformação do projeto (`dados_fem`) sobre os dados baixados.
3. Publica/atualiza o dataset no Portal de Dados Abertos de MG (ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)).

Mecanismo de agendamento: `[A DEFINIR]` (ex.: GitHub Actions `schedule`).
Horário/fuso: `[A DEFINIR]`.
Estratégia de tratamento de falhas e alertas: `[A DEFINIR]`.

## Alternativas consideradas

* Atualização manual sob demanda — descartado, pois o requisito é atualização diária confiável, sem depender de intervenção humana recorrente.
* Implementar download/parsing próprio dos dados de origem, sem `dpm` — descartado, pois `dpm` já é a ferramenta padronizada no ecossistema SPLOR para consumir `datapackage.json`, evitando duplicar lógica já mantida em outro repositório.

## Consequências

* O projeto fica dependente da disponibilidade e da API do `dpm` e da fonte `dados-siafi-2026`; mudanças nesses repositórios podem quebrar a atualização diária.
* É necessário monitorar a execução diária e ter um plano de resposta a falhas antes de considerar a publicação como confiável para um consumidor externo.
* O token de acesso (`GH_TOKEN`, hoje em `.env`) usado pelo `dpm` para instalar o pacote `siafi` precisa de uma estratégia de gestão de segredo compatível com o ambiente de execução agendado (ex.: GitHub Actions Secrets), já que `.env` é local.
