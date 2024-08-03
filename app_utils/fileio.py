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


class FileHandler:
    def __init__(self, uploaded_file: list[io.BytesIO] | io.BytesIO) -> None:
        if not isinstance(uploaded_file, list):
            uploaded_file = [uploaded_file]

        self._files = uploaded_file
        self.count = len(uploaded_file)
        self.filenames = self.get_filename()

    def student_info(self):
        # use FileReader to return df
        raise NotImplementedError

    def test_results(self):
        # use FileReader to return df
        raise NotImplementedError

    def get_filename(self):
        if self.count < 1:
            return

        return [f.name for f in self._files]

    def separate_file_group(self):
        if not self.filenames:
            return

        groups = {"test_results": [], "student_info": []}
        for f in self.filenames:
            if "assessment" in f.name.lower() or "quiz" in f.name.lower():
                groups["test_results"].append(f.name)
            else:
                groups["student_info"].append(f.name)

        return groups


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
