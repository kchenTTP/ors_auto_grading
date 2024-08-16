import re

import pandas as pd

from .errors import NoStudentEmailError
from .validators import InvalidEmail, ValidEmail, validate_single_email


def process_multiple_email(df: pd.DataFrame) -> pd.DataFrame:
    email_col = None

    # Lowercase + strip space
    for col in ["Email", "email"]:
        try:
            df[col] = df[col].str.strip().str.lower()
            email_col = col
            break
        except Exception:
            continue
    if email_col is None:
        raise NoStudentEmailError("No 'Email' or 'email' column found in the student info data")

    def process_email_cell(cell) -> list[str]:
        email_list = re.split(r"[,;|/\s]+", cell)

        return [validate_single_email(email).email for email in email_list if email]

    df[email_col] = df[email_col].apply(process_email_cell)

    return df
