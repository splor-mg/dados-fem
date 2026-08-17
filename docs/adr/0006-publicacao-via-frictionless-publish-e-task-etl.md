# 0006. Publicação via `frictionless publish` (CKAN) e task `etl` unificada

* Status: proposto — há um risco técnico bloqueante (duplicação de recursos) e vários pontos `[A DEFINIR]` a resolver antes de implementar
* Data: 2026-08-17
* Responsável(is): Gabriel Dornas

## Contexto

Faltava definir, dentro do pipeline diário (ADR [0003](0003-atualizacao-diaria-via-dpm.md)), como a etapa de publicação (ADR [0002](0002-publicacao-portal-dados-abertos-mg.md)) seria executada, e criar uma task `etl` que unifique `extract` (`dpm install`), `transform` (`scripts/transform.py`), `build_datapackage` (`scripts/build_datapackage.py`), `validate` (`frictionless validate`) e a nova task `publish`.

O Portal de Dados Abertos de MG (dados.mg.gov.br) é baseado em **CKAN**. O `frictionless` (5.19.0, já dependência do projeto) tem um comando/API `publish` (https://framework.frictionlessdata.io/docs/console/publish.html) com suporte a portais. Como a documentação pública não detalha o comportamento em atualizações repetidas, o código-fonte instalado (`frictionless==5.19.0`) foi lido diretamente para entender o funcionamento real, em vez de assumir pela documentação:

* `frictionless/console/commands/publish.py` — implementação do comando CLI `frictionless publish`.
* `frictionless/portals/ckan/adapter.py` — `CkanAdapter`, que faz o trabalho de fato (`write_package`, `write_resource`).
* `frictionless/portals/ckan/control.py` — `CkanControl`, as opções configuráveis (`baseurl`, `dataset`, `apikey`, `organization_name`, `allow_update`, ...).
* `frictionless/portals/ckan/plugin.py` — como uma URL como `https://dados.mg.gov.br/dataset/dados-fem` é interpretada (`baseurl` + `dataset`, o slug do dataset no CKAN).

### O que o código mostra

**1. Só CKAN é suportado.** `console_publish` levanta exceção para qualquer outro `target`: *"Currently only CKAN publishing is supported"*. Isso é favorável, já que o portal de MG é CKAN.

**2. O comando CLI (`frictionless publish` via terminal) não é utilizável em automação sem modificação:**
* O `apikey` só pode ser informado via prompt interativo (`Prompt.ask("Please enter API Key")`) — não existe flag `--apikey` nem leitura de variável de ambiente na CLI. Só funcionaria em CI se o valor fosse passado via stdin (`echo "$CKAN_API_KEY" | frictionless publish ...`), o que é frágil e não documentado como uso suportado.
* A CLI **não tem opção para `organization_name`** (a organização CKAN dona do dataset). Sem isso, `write_package` monta `package_data["owner_org"] = self.control.organization_name`, que ficaria `None` — a publicação provavelmente falharia ou cairia em organização errada/padrão do CKAN.
* A CLI monta o pacote a partir de `source` (arquivos) + `--title`, e **não lê o `datapackage.json`** que já geramos com `name`, `owner_org` e `licenses` (ADR [0005](0005-gerar-datapackage-raiz.md)) — essa informação se perderia.

Por esses três motivos, a CLI (`frictionless publish` rodada diretamente no terminal/Action) não atende ao nosso caso de uso.

**3. A API Python (`Package.publish(target, control=CkanControl(...))`) não tem essas limitações** — é o mesmo mecanismo por baixo (`CkanAdapter.write_package`), mas com controle total dos parâmetros via código, incluindo `apikey='env:NOME_DA_VAR'` (a própria `CkanControl` já sabe ler de variável de ambiente quando o valor começa com `env:`) e `organization_name` explícito.

**4. Atualização diária — funciona parcialmente, com uma lacuna importante:**
* No nível do **pacote** (metadados do dataset), `CkanControl(allow_update=True)` faz `write_package` chamar o endpoint `package_update` em vez de `package_create` — ou seja, atualizar metadados de um dataset já existente é suportado.
* No nível dos **recursos** (os arquivos de dado em si), porém, `write_package` sempre chama `self.write_resource(dataset_id, resource)` para cada recurso, e `write_resource` **sempre** faz um POST em `resource_create` — não existe chamada a `resource_update`/`resource_patch`, nem checagem se um recurso com aquele nome já existe. **Isso significa que, se rodarmos `publish()` todo dia com `allow_update=True`, o dataset ganha um recurso novo (`fem_execucao.csv`) duplicado a cada execução, em vez de o arquivo existente ser substituído.**

Esse último ponto é o critério que você definiu como bloqueante ("se ele não for capaz de atualizar diariamente não poderemos utilizá-lo") — **no estado em que o `frictionless publish` está na v5.19.0, ele não substitui o recurso de dado em uma atualização, só duplica.** É preciso uma mitigação (ver Decisão) para o `publish` ser viável no pipeline diário.

**5. Primeira execução vs. execuções seguintes.** `package_create` falha se o dataset já existir (nome duplicado no CKAN); `package_update` falha se o dataset ainda não existir. Ou seja, a criação inicial do dataset e as atualizações diárias não podem usar a mesma chamada sem alguma lógica de "existe ou não existe".

**6. Nome do dataset.** O slug do dataset é resolvido a partir da URL alvo (`.../dataset/<slug>`) só quando o pacote **não** tem `name`; como nosso `datapackage.json` já define `name = "dados_fem"` (com underscore — ADR 0005), é esse valor que prevalece na publicação, **não** o slug `dados-fem` (com hífen) decidido na ADR 0002. Os dois precisam ficar consistentes.

## Decisão

* Publicar via **API Python do `frictionless`** (`Package.from_descriptor('datapackage.json').publish(target, control=CkanControl(...))`), dentro de um script `scripts/publish.py`, e **não** via CLI (`frictionless publish` direto no terminal) — pelas limitações de `apikey` e `organization_name` descritas acima.
* A `CkanControl` deve receber, no mínimo: `baseurl`/`target` do portal, `organization_name` (ADR 0002: `secretaria-de-estado-de-planejamento-e-gestao-seplag`), `apikey='env:CKAN_API_KEY'` (lido do ambiente, nunca hardcoded) e `allow_update=True` a partir da segunda execução.
* Criar a task `publish` em `pyproject.toml` chamando esse script: `publish = { cmd = 'python scripts/publish.py', help = 'Publish datapackage.json to the CKAN portal.' }`.
* Criar a task `etl` unificando as etapas existentes, seguindo o mesmo padrão já usado em `pre_test = { cmd = 'task lint' }`: `etl = { cmd = 'task extract && task transform && task build_datapackage && task validate && task publish', help = 'Runs the full ETL pipeline.' }` — encadeada com `&&`, então qualquer etapa que falhe interrompe a cadeia (consistente com a estratégia de falha da ADR 0003).

### Pontos que ficam `[A DEFINIR]` antes de implementar

Este ADR não avança para `aceito` enquanto os itens abaixo não forem decididos — o pedido explícito foi não escrever código de publicação sem isso resolvido:

1. **Duplicação de recursos (bloqueante).** Como evitar que `fem_execucao.csv` seja duplicado a cada `publish()` diário? Opções a avaliar (nenhuma decidida ainda):
   * (a) Antes de publicar, remover o(s) recurso(s) existentes do dataset via chamada direta à API do CKAN (`resource_delete`), fora do `frictionless`, e então publicar "do zero" — o `package_update` cuida dos metadados, e os recursos entram limpos.
   * (b) Não usar `Package.publish()` para os recursos; usar a API do CKAN diretamente (`resource_patch`/`resource_update`) para o(s) recurso(s) já existentes, e usar `frictionless` só para o metadado do pacote.
   * (c) Outra estratégia, a definir.
2. **Bootstrap da primeira publicação.** O primeiro `publish()` precisa ser `package_create` (dataset não existe); os seguintes, `package_update`. Decidir se isso é: uma execução manual única de setup, um `try/except` no script que tenta `package_update` e cai para `package_create` se o dataset não existir, ou outra abordagem.
3. **Nome do dataset.** Alinhar `PACKAGE_NAME` em `scripts/build_datapackage.py` (hoje `dados_fem`) com o slug decidido na ADR 0002 (`dados-fem`), ou decidir explicitamente que são identificadores diferentes (nome interno do pacote vs. slug no portal) e ajustar o script de publicação para usar o slug correto independente do `name` do descritor.
4. **Credenciais.** Confirmar como obter um API key/token do CKAN de dados.mg.gov.br vinculado à organização `secretaria-de-estado-de-planejamento-e-gestao-seplag`, e armazená-lo como GitHub Actions Secret (`CKAN_API_KEY`), seguindo o mesmo padrão do `GH_TOKEN` (ADR 0003).
5. **URL/target do portal.** Confirmar a URL exata a ser usada como `target` (ex.: `https://dados.mg.gov.br/dataset/dados-fem`) junto à equipe de transparência.
6. **Mapeamento de metadados não validado em produção.** O mapeamento interno `frictionless_ckan_mapper` (licenças, formato de recurso etc.) não foi testado contra o CKAN real de dados.mg.gov.br nesta pesquisa — só o código-fonte do `frictionless` foi inspecionado. Recomenda-se um teste manual/dry-run contra um dataset de teste antes de confiar nisso no pipeline diário.

## Alternativas consideradas

* Rodar `frictionless publish` como CLI direto no step do GitHub Actions — descartado: não dá para informar `apikey` nem `organization_name` sem prompt interativo ou gambiarra de stdin, e perde os metadados já documentados em `datapackage.json`.
* Implementar a publicação inteiramente via chamadas HTTP diretas à API do CKAN, sem usar `frictionless` — não descartado, mas não escolhido como decisão principal ainda; é a alternativa natural para os itens 1(b) acima, caso o `frictionless` não seja suficiente para atualizar recursos sem duplicar.
* Publicar recriando o dataset inteiro a cada execução (deletar dataset + criar de novo) — descartado por ser mais destrutivo que necessário (perde histórico/URL estável do dataset no portal a cada recriação, dependendo de como o CKAN trata isso) frente à alternativa de só limpar os recursos.

## Consequências

* A task `publish` depende de um script Python (`scripts/publish.py`), não de uma chamada CLI simples — mais uma peça de código no projeto para manter e testar, além dos scripts já existentes.
* Enquanto o ponto 1 (duplicação de recursos) não for resolvido, a task `publish`/`etl` **não deve ser plugada no agendamento diário real** — rodar assim geraria um dataset publicado com dezenas/centenas de cópias do mesmo arquivo ao longo do tempo.
* A task `etl` fica dependente de todas as tasks anteriores já existirem e funcionarem (`extract`, `transform`, `build_datapackage`, `validate`) — qualquer mudança de nome/comportamento nelas afeta o `etl` também.
