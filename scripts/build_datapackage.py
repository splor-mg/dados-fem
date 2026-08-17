"""Gera o datapackage.json (raiz do repo) descrevendo os dados publicados.

Fluxo (ver docs/adr/0005-gerar-datapackage-raiz.md):
    1. `frictionless describe` infere a estrutura dos arquivos em
       `data/*.csv` (hoje só `data/fem_execucao.csv`, gerado por
       `scripts/transform.py`).
    2. Para cada campo inferido cujo nome já exista em algum campo de
       `datapackages/*/datapackage.json` (os pacotes de origem
       baixados pelo `dpm`), o descritor desse campo é usado na
       íntegra, no lugar do inferido — assim reaproveitamos
       title/description/constraints já documentados na fonte.
    3. O resultado é gravado em `datapackage.json`, na raiz do repo.
"""

import json
from pathlib import Path

from frictionless import describe

DATA_GLOB = 'data/*.csv'
DATAPACKAGES_GLOB = 'datapackages/*/datapackage.json'
OUTPUT_PATH = Path('datapackage.json')

PACKAGE_NAME = 'dados_fem'
PACKAGE_TITLE = 'Dados FEM'  # TODO: confirmar título definitivo do dataset
OWNER_ORG = 'secretaria-de-estado-de-planejamento-e-gestao-seplag'
LICENSES = [
    {
        'name': 'CC-BY-4.0',
        'title': 'Creative Commons Attribution 4.0',
        'path': 'https://creativecommons.org/licenses/by/4.0/',
    }
]


def load_known_fields() -> dict[str, dict]:
    known_fields: dict[str, dict] = {}
    for path in sorted(Path().glob(DATAPACKAGES_GLOB)):
        descriptor = json.loads(path.read_text(encoding='utf-8'))
        for resource in descriptor.get('resources', []):
            for field in resource.get('schema', {}).get('fields', []):
                known_fields[field['name']] = field
    return known_fields


def build_package() -> dict:
    package = describe(DATA_GLOB, type='package')
    descriptor = package.to_dict()

    known_fields = load_known_fields()
    for resource in descriptor['resources']:
        fields = resource['schema']['fields']
        resource['schema']['fields'] = [
            known_fields.get(field['name'], field) for field in fields
        ]

    descriptor['name'] = PACKAGE_NAME
    descriptor['title'] = PACKAGE_TITLE
    descriptor['owner_org'] = OWNER_ORG
    descriptor['licenses'] = LICENSES
    return descriptor


def save(descriptor: dict) -> Path:
    content = json.dumps(descriptor, indent=2, ensure_ascii=False) + '\n'
    OUTPUT_PATH.write_text(content, encoding='utf-8')
    return OUTPUT_PATH


def main() -> None:
    descriptor = build_package()
    output_path = save(descriptor)
    print(f'datapackage.json gerado em {output_path}')


if __name__ == '__main__':
    main()
