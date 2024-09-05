import io
import zipfile

import pandas as pd

from app_utils.fileio import (
    ExcelWrapper,
    ExcelWriter,
    FileHandler,
    FileReader,
    ZipWriter,
)


def test_file_reader(sample_csv_buffer) -> None:
    file_reader = FileReader(sample_csv_buffer)
    buff_df = file_reader.to_df()

    assert isinstance(buff_df, pd.DataFrame)
    assert not buff_df.empty


# FIXME: sometimes fail test
def test_excel_writer_to_xlsx(sample_dataframe, hydra_cfg) -> None:
    result = ExcelWriter(df=sample_dataframe).to_xlsx(filename=hydra_cfg.test.excel_filename)
    filename = hydra_cfg.test.excel_filename

    assert isinstance(result, ExcelWrapper)
    assert result.filename == filename
    assert isinstance(result.data, io.BytesIO)

    df_read = pd.read_excel(result.data, index_col=False)
    pd.testing.assert_frame_equal(df_read, sample_dataframe, check_dtype=False)


def test_zip_writer(sample_excel_wrappers, hydra_cfg):
    result = ZipWriter(sample_excel_wrappers).zip()

    assert isinstance(result, io.BytesIO)

    with zipfile.ZipFile(result) as zip_file:
        assert zip_file.namelist() == hydra_cfg.test.excel_wrapper_names

        # check file content
        for excel_wrapper in sample_excel_wrappers:
            with zip_file.open(excel_wrapper.filename) as f:
                assert f.read() == excel_wrapper.data.getvalue()


def test_file_handler(sample_files) -> None:
    handler = FileHandler(sample_files)

    assert handler.count == 2
    assert handler.filenames == ["student_info.csv", "assessment_results.csv"]

    groups = handler.separate_file_group()
    assert groups is not None
    assert "student_info" in groups
    assert "test_results" in groups
    assert len(groups["student_info"]) == 1
    assert len(groups["test_results"]) == 1
    assert isinstance(groups["student_info"][0], io.BytesIO)
    assert isinstance(groups["test_results"][0], io.BytesIO)
    assert groups["student_info"][0].name == "student_info.csv"
    assert groups["test_results"][0].name == "assessment_results.csv"

    student_info = handler.student_info()
    assert student_info is not None
    assert len(student_info) == 1
    assert isinstance(student_info[0], pd.DataFrame)
    assert student_info[0].to_dict("records") == [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]

    test_results = handler.test_results()
    assert test_results is not None
    assert len(test_results) == 1
    assert isinstance(test_results[0], pd.DataFrame)
    assert test_results[0].to_dict("records") == [
        {"name": "Alice", "score": 95},
        {"name": "Bob", "score": 88},
    ]


def test_file_handler_single_file() -> None:
    file = io.BytesIO(b"name,age\nCharlie,35")
    file.name = "single_student.csv"

    handler = FileHandler(file)

    assert handler.count == 1
    assert handler.filenames == ["single_student.csv"]

    groups = handler.separate_file_group()
    assert groups is not None
    assert len(groups["student_info"]) == 1
    assert len(groups["test_results"]) == 0
    assert groups["student_info"][0].name == "single_student.csv"


def test_file_handler_empty() -> None:
    handler = FileHandler([])

    assert handler.count == 0
    assert handler.filenames is None
    assert handler.separate_file_group() is None
    assert handler.student_info() is None
    assert handler.test_results() is None
