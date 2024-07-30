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


class Section(BaseModel):
    students: list[Student]
