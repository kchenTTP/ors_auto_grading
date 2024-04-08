from pydantic import BaseModel, ConfigDict
import pandas as pd


class AnswerKey(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    program: str
    dataframe: pd.DataFrame
    
# class Assessment(BaseModel):
#     model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

#     program: str
#     timestamp: datetime.datetime
#     firstname: str
#     lastname: str
#     score: str
#     dataframe: pd.DataFrame

class Assessment:
    def __init__(self, assessment: pd.Series) -> None:
        self.__df
        self.program = kwargs["program"]
        self.firstname = kwargs["First Name"]
        self.lastname = kwargs["Last Name"]
        self.data = 
    
    def get_name(self):
        