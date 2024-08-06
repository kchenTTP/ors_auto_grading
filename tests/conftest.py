import io
import os
import random

import pandas as pd
import pytest
from hydra import compose, initialize
from omegaconf import DictConfig

from app_utils.fileio import ExcelWrapper


@pytest.fixture(scope="session")
def hydra_cfg() -> DictConfig:
    with initialize(version_base=None, config_path="../conf"):
        cfg = compose(config_name="config")

    assert cfg.path.data == "./data/raw"

    return cfg


@pytest.fixture(scope="session")
def random_csv_file(hydra_cfg) -> str | bytes:
    csv_files = [f for f in os.listdir(hydra_cfg.path.data) if f.endswith(".csv")]
    if csv_files:
        return os.path.join(hydra_cfg.path.data, random.choice(csv_files))
    else:
        raise FileNotFoundError(f"No CSV files found in: {hydra_cfg.path.data}")


@pytest.fixture(scope="session")
def sample_files() -> list[io.BytesIO]:
    file1 = io.BytesIO(b"name,age\nAlice,25\nBob,30")
    file1.name = "student_info.csv"

    file2 = io.BytesIO(b"name,score\nAlice,95\nBob,88")
    file2.name = "assessment_results.csv"

    return [file1, file2]


@pytest.fixture(scope="session")
def sample_csv_buffer(random_csv_file) -> io.BytesIO:
    df = pd.read_csv(random_csv_file)
    bytes_buffer = io.BytesIO()
    df.to_csv(bytes_buffer, index=False)
    bytes_buffer.seek(0)

    assert isinstance(bytes_buffer, io.BytesIO)

    return bytes_buffer


@pytest.fixture(scope="session")
def sample_dataframe(random_csv_file) -> pd.DataFrame:
    df = pd.read_csv(random_csv_file, index_col=False)

    assert not df.empty

    return df


@pytest.fixture(scope="session")
def sample_excel_wrappers(hydra_cfg) -> list[ExcelWrapper]:
    filename_list: list[str] = hydra_cfg.test.excel_wrapper_names
    data_list: list[str] = hydra_cfg.test.excel_wrapper_data

    ew_list = []

    for f, d in zip(filename_list, data_list):
        ew_list.append(ExcelWrapper(f, io.BytesIO(d.encode())))

    return ew_list
