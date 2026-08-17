# 0003. Atualização diária dos dados via `dpm`

* Status: proposto (falta detalhar as etapas de transformação/publicação do pipeline)
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

O conjunto de dados a ser publicado no Portal de Dados Abertos de MG (ver ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)) precisa ser atualizado diariamente, refletindo a fonte de origem (`siafi`, descrita em [`data.toml`](../../data.toml)). O projeto já depende da biblioteca [`dpm`](https://github.com/splor-mg/dpm) (Data Package Manager), que instala/baixa recursos descritos em um `datapackage.json` (padrão [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/)) via `dpm install`.

Ainda falta detalhar:

* As etapas concretas do pipeline após o `dpm install` (transformação/análise em `dados_fem/main.py`, geração do artefato final a publicar) — `[A DEFINIR]`.
* O que acontece especificamente se a fonte (`dados-siafi-2026`) não atualizar ou o schema mudar (validação de schema antes de publicar) — `[A DEFINIR]`.

Os demais itens (onde a rotina roda, horário, tratamento de falha, gestão do segredo) já foram definidos (ver Decisão).

## Decisão

Usar `dpm` como ferramenta de obtenção dos dados de origem, orquestrada por uma rotina agendada para execução diária, que:

1. Executa `dpm install` para baixar a versão mais recente do(s) datapackage(s) configurado(s) em `data.toml`.
2. Executa a análise/transformação do projeto (`dados_fem`) sobre os dados baixados.
3. Publica/atualiza o dataset no Portal de Dados Abertos de MG (ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)).

* Mecanismo de agendamento: GitHub Actions (`schedule`/cron), mesmo ambiente já usado no repositório (`.github/workflows/`).
* Horário/fuso: 10h, horário de São Paulo/Brasília (America/Sao_Paulo).
* Estratégia de tratamento de falhas: se qualquer etapa do pipeline falhar, o job falha e não publica dado parcial/incorreto; a equipe é notificada automaticamente (ex.: GitHub Actions enviando e-mail/mensagem em caso de falha do workflow).
* Gestão do segredo `GH_TOKEN`: armazenado como GitHub Actions Secret (do repositório ou da organização), nunca versionado em `.env`.

## Alternativas consideradas

* Atualização manual sob demanda — descartado, pois o requisito é atualização diária confiável, sem depender de intervenção humana recorrente.
* Implementar download/parsing próprio dos dados de origem, sem `dpm` — descartado, pois `dpm` já é a ferramenta padronizada no ecossistema SPLOR para consumir `datapackage.json`, evitando duplicar lógica já mantida em outro repositório.

## Consequências

* O projeto fica dependente da disponibilidade e da API do `dpm` e da fonte `dados-siafi-2026`; mudanças nesses repositórios podem quebrar a atualização diária.
* É necessário monitorar a execução diária e ter um plano de resposta a falhas antes de considerar a publicação como confiável para um consumidor externo.
* O token de acesso (`GH_TOKEN`) usado pelo `dpm` para instalar o pacote `siafi` passa a ser gerido via GitHub Actions Secrets no ambiente de execução agendada, deixando de depender do `.env` local (que segue útil apenas para desenvolvimento).
