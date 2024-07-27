import pandas as pd
from pydantic import BaseModel, ConfigDict, EmailStr


class AnswerKey(BaseModel):
    answers: pd.DataFrame


class Assessment(BaseModel):
    """dataframe of 1 or more rows of data (assessments)"""

    attempts: pd.DataFrame


class Student(BaseModel):
    name: str
    email: list[EmailStr]
    attempts: Assessment


class Section(BaseModel):
    students: list[Student]
