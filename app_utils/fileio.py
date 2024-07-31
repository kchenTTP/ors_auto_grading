"""
file reader: read csv file or xlsx file and convert it to pandas df
file writer: take pandas df and create xlsx file and zip files
"""

import io
import zipfile
from dataclasses import dataclass

import pandas as pd
import streamlit as st


@dataclass
class ExcelWrapper:
    filename: str
    data: io.BytesIO


class FileReader:
    def __init__(self, file: io.BytesIO) -> None:
        self._file = file

    # @st.cache_data(hash_funcs={"__main__.FileReader": lambda x: hash(x._file.getvalue())})
    def to_df(self) -> pd.DataFrame:
        return pd.read_csv(self._file)


class ExcelWriter:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def to_xlsx(self, filename: str) -> ExcelWrapper:
        excel_buffer = io.BytesIO()
        writer = pd.ExcelWriter(excel_buffer, "xlsxwriter")
        self.df.to_excel(writer, sheet_name="attempts", index=False)
        writer.close()

        return ExcelWrapper(filename=filename, data=excel_buffer)


class ZipWriter:
    def __init__(self, file_list: list[ExcelWrapper]) -> None:
        self.files = file_list

    def zip(self) -> io.BytesIO:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f in self.files:
                zip_file.writestr(f.filename, f.data.getvalue())

        return zip_buffer
