import io
import zipfile

import pandas as pd

from app_utils.fileio import ExcelWrapper, ExcelWriter, FileReader, ZipWriter


def test_FileReader(sample_csv_buffer) -> None:
    file_reader = FileReader(sample_csv_buffer)
    buff_df = file_reader.to_df()

    assert isinstance(buff_df, pd.DataFrame)
    assert not buff_df.empty


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
