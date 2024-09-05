import datetime

import pandas as pd
from pydantic import BaseModel, ConfigDict, EmailStr


class AnswerKey(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    answers: pd.DataFrame


class Assessment(BaseModel):
    """dataframe of 1 or more rows of data (assessments)"""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    attempts: pd.DataFrame


class Student(BaseModel):
    name: str
    email: list[EmailStr]
    attempts: Assessment


class SectionInfo(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    section: int
    data: pd.DataFrame


class FilterOptions(BaseModel):
    by_name: bool
    by_email: bool
    by_section: bool
    start_date: datetime.date
    section: int | None
