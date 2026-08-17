"""Rascunho do pipeline de transformação do dataset a publicar.

Fluxo (ver docs/adr/0003-atualizacao-diaria-via-dpm.md):
    1. `dpm install` já baixou os recursos do pacote `siafi` em
       datapackages/siafi/data/ (execucao.csv.gz, receita.csv.gz).
    2. Este script lê esses recursos, aplica a análise/transformação
       do projeto e grava o resultado em `data/`.
    3. O conteúdo de `data/` é o que será publicado no Portal de
       Dados Abertos de MG (ver docs/adr/0002).

TODO: as regras de análise/transformação ainda não foram definidas —
por ora o script só lê e repassa os dados (passthrough), como ponto
de partida para revisão.
"""

from pathlib import Path

import pandas as pd
from frictionless import Package

DATAPACKAGE_PATH = Path('datapackages/siafi/datapackage.json')
OUTPUT_DIR = Path('data')

RESOURCES = ['execucao', 'receita']


def load_resource(name: str) -> pd.DataFrame:
    package = Package(DATAPACKAGE_PATH)
    resource = package.get_resource(name)
    return resource.to_pandas()


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: aplicar aqui as regras da análise (filtros, agregações,
    # cálculo de colunas derivadas, etc.) antes de publicar.
    return df


def save_resource(df: pd.DataFrame, name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f'{name}.csv'
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    for name in RESOURCES:
        df = load_resource(name)
        df = transform(df)
        output_path = save_resource(df, name)
        print(f'{name}: {len(df)} linhas -> {output_path}')


if __name__ == '__main__':
    main()
