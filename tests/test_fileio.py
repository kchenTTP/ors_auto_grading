import io

import pandas as pd
import pytest
from hydra import compose, initialize

from app_utils.fileio import *


def test_FileReader(hydra_cfg):
    filepath = f"{hydra_cfg.path.data}/ORS Excel Assessment (Responses) - Form Responses 1.csv"

    df = pd.read_csv(filepath)

    bytes_buffer = io.BytesIO()
    df.to_csv(bytes_buffer, index=False)
    bytes_buffer.seek(0)

    assert isinstance(bytes_buffer, io.BytesIO)

    file_reader = FileReader(bytes_buffer)

    assert isinstance(file_reader.to_df(), pd.DataFrame)


def test_ExcelWriter(hydra_cfg):
    raise NotImplementedError


def test_ZipWriter(hydra_cfg):
    raise NotImplementedError


def test_hydra(hydra_cfg):
    assert hydra_cfg.path.data == "./data/raw"


@pytest.fixture(scope="session")
def hydra_cfg():
    with initialize(version_base=None, config_path="../conf"):
        cfg = compose(config_name="config")
    return cfg
