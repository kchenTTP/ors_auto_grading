import io
import zipfile
from typing import Literal


class FileWrapper:
    def __init__(
        self, file: io.BytesIO, for_export: bool = False, filename: str | None = None
    ) -> None:
        self.data = file
        if not for_export:
            if filename:
                filename = None
                print("File already have a file name, parameter: filename set to None")
            self.__filename = file.name
            self.type = self._check_file_type()
        else:
            assert (
                filename is not None
            ), "Parameter filename cannot be None when parameter for_export is set to True. Please provide a filename."

            self.__filename = filename
            self.type = "export"

    def __repr__(self) -> str:
        return self.__filename

    @property
    def file(self) -> io.BytesIO:
        return self.data

    @property
    def filename(self) -> str:
        return self.__filename

    # @st.cache_data(hash_funcs={"__main__.FileUtils": lambda x: hash(x.file.getvalue())})
    # def to_dataframe_utils(self):
    #     return DataFrameUtils(pd.read_csv(self.data))

    def _check_file_type(
        self,
    ) -> Literal["word"] | Literal["excel"] | Literal["ppt"] | Literal["info"]:
        f_lowered = self.__filename.lower()

        if "word" in f_lowered:
            return "word"
        if "excel" in f_lowered:
            return "excel"
        if "powerpoint" in f_lowered or "ppt" in f_lowered:
            return "ppt"
        return "info"


def create_zip_file(file_list: list[FileWrapper]) -> io.BytesIO:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in file_list:
            zip_file.writestr(file.filename, file.data.getvalue())

    return zip_buffer
