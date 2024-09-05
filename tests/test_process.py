import pandas as pd

from app_utils.process import get_section_number, process_multiple_email


def test_get_section_number() -> None:
    d = {"name": [0, 1, 2, 3, 4, 5], "Section": pd.Series([3, 3, 3, 3, 3, 3])}
    df = pd.DataFrame(d)

    assert get_section_number(df) == 3

    d = {"name": [0, 1, 2, 3, 4, 5], "Section": pd.Series([3, 3, 2, 3, 3, 3])}
    df = pd.DataFrame(d)

    assert get_section_number(df) == 3

    d = {"name": [0, 1, 2, 3, 4, 5, 6], "Section": pd.Series([3, 3, 2, 2, 2, 3, 2])}
    df = pd.DataFrame(d)

    assert get_section_number(df) == 2

    d = {"name": [0, 1, 2, 3, 4, 5]}
    df = pd.DataFrame(d)

    assert get_section_number(df) is None

    d = {"name": [0, 1, 2, 3, 4, 5], "Section": pd.Series([1, 2, 3, 4, 5, 6])}
    df = pd.DataFrame(d)

    assert get_section_number(df) == 1
