# 0003. Atualização diária dos dados via `dpm`

* Status: aceito
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

O conjunto de dados a ser publicado no Portal de Dados Abertos de MG (ver ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)) precisa ser atualizado diariamente, refletindo a fonte de origem (`siafi`, descrita em [`data.toml`](../../data.toml)). O projeto já depende da biblioteca [`dpm`](https://github.com/splor-mg/dpm) (Data Package Manager), que instala/baixa recursos descritos em um `datapackage.json` (padrão [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/)) via `dpm install`.

Esta ADR fixa apenas o *onde/quando/como reagir a falha* da execução diária. As etapas concretas do pipeline (extract → transform → build datapackage → validate → publish, e o step de commit dos artefatos gerados) serão detalhadas em uma ADR específica sobre a definição do workflow do GitHub Actions.

## Decisão

Usar `dpm` como ferramenta de obtenção dos dados de origem, orquestrada por uma rotina agendada para execução diária.

* Mecanismo de agendamento: GitHub Actions (`schedule`/cron), mesmo ambiente já usado no repositório (`.github/workflows/`).
* Horário/fuso: 10h, horário de São Paulo/Brasília (America/Sao_Paulo).
* Tratamento de falha no `dpm install` (task `extract`): se o comando falhar, o processo é encerrado com erro — a própria lib `dpm` já retorna status de erro nesse caso, o que interrompe o workflow do GitHub Actions naturalmente, sem necessidade de lógica adicional no pipeline para isso.
* Notificação de falha: um step do workflow deve criar automaticamente uma Issue no repositório sempre que qualquer etapa do pipeline falhar (não só o `dpm install`).
* Gestão do segredo `GH_TOKEN`: armazenado como GitHub Actions Secret (do repositório ou da organização), nunca versionado em `.env`.
* Artefatos gerados pelo pipeline (`data/`, incluindo `data/fem_execucao.csv` — ADR [0004](0004-script-de-transformacao-scripts-transform.md) —, e `datapackage.json` na raiz — ADR [0005](0005-gerar-datapackage-raiz.md)) devem ser commitados no repositório a cada execução diária; o workflow precisa de um step para isso. A exceção é `datapackages/` (resultado do `dpm install`), que não é commitado — já está listado em `.gitignore`.

Validação de schema da fonte (schema mudar em `dados-siafi-2026`) foi avaliada e descartada como preocupação deste ADR: não há hipótese identificada, no fluxo atual, de a fonte mudar de schema sem que isso seja tratado em outro ponto do processo; se essa necessidade surgir no futuro, deve ser tratada em ADR própria.

## Alternativas consideradas

* Atualização manual sob demanda — descartado, pois o requisito é atualização diária confiável, sem depender de intervenção humana recorrente.
* Implementar download/parsing próprio dos dados de origem, sem `dpm` — descartado, pois `dpm` já é a ferramenta padronizada no ecossistema SPLOR para consumir `datapackage.json`, evitando duplicar lógica já mantida em outro repositório.
* Validar schema da fonte a cada execução, antes de seguir o pipeline — descartado por não haver, no fluxo atual, um cenário identificado em que isso seja necessário; adicionar essa validação agora seria resolver um problema hipotético.

## Consequências

* O projeto fica dependente da disponibilidade e da API do `dpm` e da fonte `dados-siafi-2026`; mudanças nesses repositórios podem quebrar a atualização diária, mas o `dpm install` já falha de forma explícita (o workflow para e uma Issue é criada), evitando publicação de dado desatualizado sem aviso.
* O token de acesso (`GH_TOKEN`) usado pelo `dpm` para instalar o pacote `siafi` passa a ser gerido via GitHub Actions Secrets no ambiente de execução agendada, deixando de depender do `.env` local (que segue útil apenas para desenvolvimento).
* As etapas concretas do pipeline (o que roda entre o `dpm install` e a publicação, e a etapa de commit dos artefatos) ficam para uma ADR específica — este ADR não deve ser tratado como a fonte da verdade sobre a sequência completa do workflow.
