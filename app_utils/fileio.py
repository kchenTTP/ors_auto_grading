"""
file reader: read csv file or xlsx file and convert it to pandas df
file writer: take pandas df and create xlsx file and zip files
"""

import io


class file_reader:
    def __init__(self, file: io.BytesIO) -> None:
        raise NotImplementedError


class file_writer:
    def __init__(self, file: io.BytesIO) -> None:
        raise NotImplementedError
