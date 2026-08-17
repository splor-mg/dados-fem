"""Pipeline de transformação do dataset a publicar.

Fluxo (ver docs/adr/0003-atualizacao-diaria-via-dpm.md):
    1. `dpm install` já baixou os recursos do pacote `siafi` em
       datapackages/siafi/data/ (execucao.csv.gz, credito.csv.gz).
    2. Este script lê esses recursos via `frictionless`, filtra
       fonte_cod == '71', agrega (soma) os campos de valor por
       chave (ano, uo_cod, acao_cod, fonte_cod) em cada recurso e
       faz um LEFT JOIN nessa chave, com `credito` como base.
    3. O resultado é gravado em `data/fem.csv`, que é o que será
       publicado no Portal de Dados Abertos de MG (ver docs/adr/0002).
"""

from functools import reduce
from pathlib import Path

import pandas as pd
from frictionless import Package

DATAPACKAGE_PATH = Path('datapackages/siafi/datapackage.json')
OUTPUT_DIR = Path('data')

KEY_FIELDS = ['ano', 'uo_cod', 'acao_cod', 'fonte_cod']
FONTE_COD_FILTRO = '71'


def load_resources() -> list[pd.DataFrame]:
    package = Package(DATAPACKAGE_PATH)
    return [resource.to_pandas() for resource in package.resources]


def filter_fonte(df: pd.DataFrame) -> pd.DataFrame:
    return df[df['fonte_cod'] == FONTE_COD_FILTRO]


def aggregate_by_key(df: pd.DataFrame) -> pd.DataFrame:
    value_fields = [c for c in df.columns if c.startswith('vlr_')]
    return df.groupby(KEY_FIELDS, as_index=False)[value_fields].sum()


def transform(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    dfs = [aggregate_by_key(filter_fonte(df)) for df in dfs]
    return reduce(
        lambda left, right: left.merge(right, on=KEY_FIELDS, how='left'),
        dfs,
    )


def save(df: pd.DataFrame) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'fem_execucao.csv'
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    dfs = load_resources()
    df = transform(dfs)
    output_path = save(df)
    print(f'{len(df)} linhas -> {output_path}')


if __name__ == '__main__':
    main()


