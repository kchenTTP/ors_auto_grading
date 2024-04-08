#  cSpell: ignore streamlit, dataframe, selectbox, pydantic, funcs, configdict, answerkey, iloc, iterrows
import datetime
import io
import re
import zipfile
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
from pydantic import BaseModel, ConfigDict, EmailStr

from grader_utils.custom_errors import TooManyFilesError
from grader_utils.file_io import create_zip_file
from grader_utils.st_utils import (
    clear_assessment_session_state,
    clear_student_session_state,
    display_assessment_info_hint,
    display_student_info_hint,
    set_st_session_state,
)


# FUNCTIONS & CLASSES
@dataclass
class ExcelFileWrapper:
    filename: str
    data: io.BytesIO


class QuestionAnswerPair(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    answer: str


class AnswerKey(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    program: str
    dataframe: pd.DataFrame
    questions_and_answers: list[QuestionAnswerPair]


class Assessment(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    program: str
    timestamp: datetime.datetime
    firstname: str
    lastname: str
    score: str
    dataframe: pd.DataFrame
    response: list[QuestionAnswerPair]


class Student(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
    )

    firstname: str
    lastname: str
    email: list[EmailStr]
    word: Optional[list[Assessment]] = []
    excel: Optional[list[Assessment]] = []
    ppt: Optional[list[Assessment]] = []

    def generate_report(self):
        report_dicts = []

        if self.word:
            word_df = st.session_state.word_answer_key.dataframe
            for assess in self.word:
                word_df = pd.concat([word_df, assess.dataframe], axis=1)
            report_dicts.append(
                {
                    "program": "word",
                    "report": word_df,
                }
            )

        if self.excel:
            excel_df = st.session_state.excel_answer_key.dataframe
            for assess in self.excel:
                excel_df = pd.concat([excel_df, assess.dataframe], axis=1)
            report_dicts.append(
                {
                    "program": "excel",
                    "report": excel_df,
                }
            )

        if self.ppt:
            ppt_df = st.session_state.ppt_answer_key.dataframe
            for assess in self.ppt:
                ppt_df = pd.concat([ppt_df, assess.dataframe], axis=1)
            report_dicts.append(
                {
                    "program": "ppt",
                    "report": ppt_df,
                }
            )

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, "xlsxwriter")
        for report in report_dicts:
            report["report"].to_excel(writer, sheet_name=report["program"])

        writer.close()

        return ExcelFileWrapper(
            filename=f"{self.firstname} {self.lastname}_report.xlsx",
            data=output,
        )


class DataFrameUtils:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def __repr__(self) -> str:
        return repr(self.df)

    def get_section_nums(self) -> list:
        if not self.__is_student_dataframe(self.df):
            raise ValueError(
                "'Section' Info Not Found\n \
                Data does not contain a column named 'Section' (case-sensitive). \
                Please make sure you're using the right file or rename the column containing the section numbers to 'Section'."
            )

        sections = self.df.Section.unique().tolist()
        sections.sort()

        return sections

    def get_section_df(self, section_num: int) -> pd.DataFrame:
        if not self.__is_student_dataframe(self.df):
            raise ValueError(
                "'Section' Info Not Found\n \
                Data does not contain a column named 'Section' (case-sensitive). \
                Please make sure you're using the right file or rename the column containing the section numbers to 'Section'."
            )

        filtered_df = self.df.loc[
            (self.df.Section == section_num) & (self.df.Status == "Active")
        ].sort_values(by=["First Name"], ascending=True)
        self.__section_info_all = filtered_df.reset_index()

        return self.__section_info_all

    def get_student_info(self, include_email: bool = True) -> pd.DataFrame:
        if not self.__is_student_dataframe(self.df):
            raise ValueError(
                "Not Student Data\n \
                Data does not contain a column named 'Section' (case-sensitive). \
                Please make sure you're using the right file or rename the column containing the section numbers to 'Section'."
            )

        if include_email:
            stu_info_df = self.__section_info_all[["First Name", "Last Name", "Email"]]
            stu_info_df["Email"] = stu_info_df["Email"].str.lower().str.strip().str.replace(" ", "")
        else:
            stu_info_df = self.__section_info_all[["First Name", "Last Name"]]

        stu_info_df["First Name"] = (
            stu_info_df["First Name"].str.lower().str.strip().str.replace(" ", "")
        )
        stu_info_df["Last Name"] = (
            stu_info_df["Last Name"].str.lower().str.strip().str.replace(" ", "")
        )

        return stu_info_df

    def get_student_object_list(self) -> list:
        # TODO: Check if dataframe contains only 3 columns (firstname, lastname, email)
        sol = []
        for _, row in self.df.iterrows():
            sol.append(
                Student(
                    firstname=row["First Name"],
                    lastname=row["Last Name"],
                    email=row["Email"].split(","),
                )
            )

        return sol

    def __is_student_dataframe(self, df: pd.DataFrame) -> bool:
        cols = [col.lower() for col in df.columns]

        if "section" not in cols:
            return False

        return True

    def __is_assessment_dataframe(self, df: pd.DataFrame) -> bool:
        cols = [col.lower() for col in df.columns]

        if "timestamp" not in cols:
            return False

        return True

    def convert_to_csv(self) -> bytes:
        return self.df.to_csv(index=False).encode("utf-8")

    def get_q_a_list(self, q_a_row: pd.DataFrame) -> list[QuestionAnswerPair]:
        q_a_list = []
        for q, a in q_a_row.iterrows():
            question = str(q)
            answer = str(a.iloc[0])
            pattern = r"^=[\w\W]+$"
            if bool(re.match(pattern, answer)):
                answer = "(" + answer + ")"

            q_a_list.append(QuestionAnswerPair(question=question, answer=answer))

        return q_a_list

    def get_answer_key(self, program: str) -> AnswerKey:
        if not self.__is_assessment_dataframe(self.df):
            raise ValueError(
                f"Not Assessment Data\n \
                Data does not contain a column named Timestamp in provided columns (case-sensitive).\n \
                {self.df.columns}\n \
                Please make sure you're using the right file."
            )

        answer_row = self.df.loc[self.df.Score == "100 / 100"].tail(1).reset_index(drop=True)
        df_for_answerkey = answer_row.copy()
        answer_row = answer_row.iloc[:, 5:].T
        q_a_list = self.get_q_a_list(answer_row)
        df_for_answerkey.at[0, "Timestamp"] = "Answer Key"
        df_for_answerkey.at[0, "Score"] = np.nan
        df_for_answerkey = df_for_answerkey.drop(
            ["Email Address", "First Name", "Last Name"], axis=1
        )
        df_for_answerkey.set_index("Timestamp", inplace=True)
        df_for_answerkey = df_for_answerkey.T

        return AnswerKey(
            program=program, dataframe=df_for_answerkey, questions_and_answers=q_a_list
        )

    def to_assessment(self, program: str) -> Assessment:
        timestamp = self.df["Timestamp"].to_list()[0]
        firstname = self.df["First Name"].to_list()[0]
        lastname = self.df["Last Name"].to_list()[0]
        score = self.df["Score"].to_list()[0]
        answer_row = self.df.iloc[:, 5:].T
        response = self.get_q_a_list(answer_row)

        df_for_assessment = self.df.drop(["Email Address", "First Name", "Last Name"], axis=1)
        df_for_assessment.set_index("Timestamp", inplace=True)
        df_for_assessment = df_for_assessment.T

        return Assessment(
            program=program,
            timestamp=timestamp,
            firstname=firstname,
            lastname=lastname,
            score=score,
            dataframe=df_for_assessment,
            response=response,
        )

    def filter_date(self, date: datetime.date or tuple[datetime.date] or None) -> pd.DataFrame:
        if not self.__is_assessment_dataframe(self.df):
            raise ValueError(
                f"Not Assessment Data\n \
                Data does not contain a column named Timestamp in provided columns (case-sensitive).\n \
                {self.df.columns}\n \
                Please make sure you're using the right file."
            )

        self.df.Timestamp = pd.to_datetime(
            self.df.Timestamp, format="%m/%d/%Y %H:%M:%S", errors="coerce"
        )

        return self.df[self.df["Timestamp"].dt.date >= date]

    def filter_firstname(self, names: pd.DataFrame) -> pd.DataFrame:
        if not self.__is_assessment_dataframe(self.df):
            raise ValueError(
                f"Not Assessment Data\n \
                Data does not contain a column named Timestamp in provided columns (case-sensitive).\n \
                {self.df.columns}\n \
                Please make sure you're using the right file."
            )

        self.df["First Name"] = self.df["First Name"].str.strip().str.lower()
        self.df["Last Name"] = self.df["Last Name"].str.strip().str.lower()
        self.df["Email Address"] = self.df["Email Address"].str.strip().str.lower()
        processed_df = self.df[self.df["First Name"].isin(names["First Name"])]
        processed_df.reset_index(drop=True, inplace=True)

        return processed_df

    def filter_lastname(self, names: pd.DataFrame) -> pd.DataFrame:
        if not self.__is_assessment_dataframe(self.df):
            raise ValueError(
                f"Not Assessment Data\n \
                Data does not contain a column named Timestamp in provided columns (case-sensitive).\n \
                {self.df.columns}\n \
                Please make sure you're using the right file."
            )

        self.df["First Name"] = self.df["First Name"].str.strip().str.lower()
        self.df["Last Name"] = self.df["Last Name"].str.strip().str.lower()
        self.df["Email Address"] = self.df["Email Address"].str.strip().str.lower()
        processed_df = self.df[self.df["Last Name"].isin(names["Last Name"])]
        processed_df.reset_index(drop=True, inplace=True)

        return processed_df

    def filter_email(self, names: pd.DataFrame) -> pd.DataFrame:
        if not self.__is_assessment_dataframe(self.df):
            raise ValueError(
                f"Not Assessment Data\n \
                Data does not contain a column named Timestamp in provided columns (case-sensitive).\n \
                {self.df.columns}\n \
                Please make sure you're using the right file."
            )

        self.df["First Name"] = self.df["First Name"].str.strip().str.lower()
        self.df["Last Name"] = self.df["Last Name"].str.strip().str.lower()
        self.df["Email Address"] = self.df["Email Address"].str.strip().str.lower()
        processed_df = self.df[self.df["Email Address"].isin(names["Email"])]
        processed_df.reset_index(drop=True, inplace=True)

        return processed_df

    def get_student_grades(self) -> list[Assessment]:
        assessments_list = []

        for _, row in self.df.iterrows():
            assessment_util = DataFrameUtils(row.to_frame().T)
            assessment = assessment_util.to_assessment(program=f._is_type)

            for student in st.session_state.student_object_list:
                if (
                    student.lastname == assessment.lastname
                    and student.firstname == assessment.firstname
                ):
                    match f._is_type:
                        case "word":
                            student.word.append(assessment)
                        case "excel":
                            student.excel.append(assessment)
                        case "ppt":
                            student.ppt.append(assessment)
            assessments_list.append(assessment)

        return assessments_list

    def error_message(self):
        # Create custom error and message so I don't have to repeat myself in every single method
        pass


class FileUtils:
    def __init__(self, file: io.BytesIO) -> None:
        self.__file = file
        self.__filename = file.name
        self._is_type = self.__check_file_purpose()

    def __repr__(self) -> str:
        return self.__filename

    @property
    def file(self) -> io.BytesIO:
        return self.__file

    @property
    def filename(self) -> str:
        return self.__filename

    @st.cache_data(hash_funcs={"__main__.FileUtils": lambda x: hash(x.file.getvalue())})
    def to_dataframe_utils(self):
        return DataFrameUtils(pd.read_csv(self.__file))

    def __check_file_purpose(self):
        if "word" in self.__filename.lower():
            return "word"
        if "excel" in self.__filename.lower():
            return "excel"
        if "powerpoint" in self.__filename.lower() or "ppt" in self.__filename.lower():
            return "ppt"
        return "info"


# STREAMLIT APP
st.set_page_config(initial_sidebar_state="expanded")

set_st_session_state()


# SIDEBAR
with st.sidebar:
    st.header("Section Information")
    student_info_placeholder = st.empty()
    section_setting_container = st.container()

    if st.session_state.section_num is None:
        display_student_info_hint(container=student_info_placeholder)

    st.header("Assessment Information")
    assessment_info_placeholder = st.empty()
    assessment_setting_container = st.container()

    if (
        not st.session_state.word_uploaded
        or not st.session_state.excel_uploaded
        or not st.session_state.ppt_uploaded
    ):
        display_assessment_info_hint(container=assessment_info_placeholder)

    start_date = assessment_setting_container.date_input(
        "Select the starting date of current cohort.",
        value=datetime.datetime.today().replace(day=1),
        format="MM/DD/YYYY",
    )
    st.session_state.start_date = start_date


# MAIN APP
st.title(":rainbow[ORS Assessment AutoGrader]")

student_info_tab, assessment_tab = st.tabs(["Section Information", "Assessment Grader"])

with student_info_tab:
    with st.container(border=True):
        st.subheader("Section Information")
        student_file = st.file_uploader(
            "Upload student information file here. Make sure all student information is correct before uploading or autograder may not work properly.\n\n \
                Make sure there is a 'Section' and 'Status' column (case-sensitive)",
            type="csv",
        )

    if student_file is not None:
        students = FileUtils(student_file)
        student_data_utils = students.to_dataframe_utils()

        sections_list = student_data_utils.get_section_nums()
        section_num = section_setting_container.selectbox(
            "Which section do you teach?", options=sections_list, index=None
        )

        if section_num is not None:
            st.session_state.section_num = section_num

            section_df = student_data_utils.get_section_df(section_num)
            student_df = student_data_utils.get_student_info()

            edited_student_df = st.data_editor(
                student_df,
                hide_index=False,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "firstname": st.column_config.TextColumn(
                        "First Name",
                        help="Student's first name",
                        required=True,
                        max_chars=50,
                    ),
                    "lastname": st.column_config.TextColumn(
                        "Last Name",
                        help="Student's last name",
                        required=True,
                        max_chars=50,
                    ),
                    "email": st.column_config.TextColumn(
                        "Email",
                        help="Student's email address",
                        validate=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    ),
                },
            )

            st.session_state.student_df = DataFrameUtils(edited_student_df)
            st.session_state.n_students = edited_student_df.shape[0]

            student_info_placeholder.empty()
            with student_info_placeholder.container(border=True):
                st.markdown(f"__Section: {st.session_state.section_num}__")
                st.markdown(f"__Total Students: {st.session_state.n_students}__")

            student_object_list = st.session_state.student_df.get_student_object_list()
            st.session_state.student_object_list = student_object_list

            # student_info_csv_data = DataFrameUtils(edited_student_df).convert_to_csv()

            # st.download_button(
            #     label="Download student data as CSV",
            #     data=student_info_csv_data,
            #     file_name=f"ORS_Section{section_num}_Student_Info.csv",
            #     mime="text/csv",
            #     type="primary",
            # )
    else:
        clear_student_session_state()
        display_student_info_hint(container=student_info_placeholder)

with assessment_tab:
    assessment_test_upload_container = st.container(border=True)
    assessment_df_display_placeholder = st.empty()

    assessment_test_upload_container.subheader("Assessment Files")
    assessment_files = assessment_test_upload_container.file_uploader(
        "Upload assessment result files here, make sure the name of the program is in the file name.\n\n \
            Ex. 'Word' or 'Excel' or 'PowerPoint' (case-insensitive)",
        type="csv",
        accept_multiple_files=True,
    )

    if assessment_files is not None:
        # Read File
        n_files = len(assessment_files)
        if n_files > st.session_state.MAX_ASSESSMENT_FILES:
            raise TooManyFilesError(
                f"Too many files uploaded. Please upload a maximum of {st.session_state.MAX_ASSESSMENT_FILES} assessment files."
            )

        assessment_file_utils_list = [FileUtils(file) for file in assessment_files]

        program_idx_map = {}
        program_df_utils_list = []

        if assessment_files:
            assessment_info_container = assessment_info_placeholder.container(border=True)
            for i, f in enumerate(assessment_file_utils_list):
                match f._is_type:
                    case "word":
                        st.session_state.word_uploaded = True
                    case "excel":
                        st.session_state.excel_uploaded = True
                    case "ppt":
                        st.session_state.ppt_uploaded = True
                    case _:
                        st.error(
                            "File Not recognized: Please make sure 'Word' or 'Excel' or 'PowerPoint' is in the file name (case-insensitive)."
                        )

                st.subheader(st.session_state.programs_dict.get(f._is_type))

                program_name = st.session_state.programs_dict.get(f._is_type)
                program_idx_map[f._is_type] = i

                program_df_util = f.to_dataframe_utils()
                program_df_utils_list.append(program_df_util)

                answer_key = program_df_util.get_answer_key(f._is_type)
                match f._is_type:
                    case "word":
                        st.session_state.word_answer_key = answer_key
                        st.session_state.word_graded = True
                    case "excel":
                        st.session_state.excel_answer_key = answer_key
                        st.session_state.excel_graded = True
                    case "ppt":
                        st.session_state.ppt_answer_key = answer_key
                        st.session_state.ppt_graded = True

                # filter dataframe base on start date
                date_filtered_df_util = DataFrameUtils(
                    program_df_util.filter_date(st.session_state.start_date)
                )

                # filter dataframe base on last name
                if st.session_state.student_df is not None:
                    lastname_filtered_df_util = DataFrameUtils(
                        date_filtered_df_util.filter_lastname(st.session_state.student_df.df)
                    )

                    final_filtered_df_util = lastname_filtered_df_util
                    edited_filtered_df = st.data_editor(
                        final_filtered_df_util.df,
                        hide_index=False,
                        use_container_width=True,
                        num_rows="dynamic",
                    )
                    edited_filtered_df_util = DataFrameUtils(edited_filtered_df)
                    edited_filtered_df_util.get_student_grades()

                assessment_info_container.markdown(f"__{program_name}__")
        else:
            clear_assessment_session_state()

        # TODO: Display Results
        # Display name mismatches
        # Dataframe of grading summary
        # Put individual students in a list inside the sidebar: DataFrame(Name, n_assessments, dates of assessments, grade)
        # Display Student information
        ## Name: Number of assessments
    else:
        display_assessment_info_hint(container=assessment_info_placeholder)

    generate_report_btn_placeholder = st.empty()

    if (
        st.session_state.word_graded is True
        or st.session_state.excel_graded is True
        or st.session_state.ppt_graded is True
    ):
        generate_btn_clicked = generate_report_btn_placeholder.button("Create Report")

        if generate_btn_clicked:
            student_reports = [
                student.generate_report() for student in st.session_state.student_object_list
            ]  # List of ExcelFileWrapper class
            # TODO: Create all student list
            section_report = ...

            st.session_state.zip_file = create_zip_file(student_reports)

    if st.session_state.zip_file is not None:
        generate_report_btn_placeholder.download_button(
            label="Download Reports",
            data=st.session_state.zip_file.getvalue(),
            file_name=f"ORS_Section_{st.session_state.section_num}_All_Student_Report.zip",
            type="primary",
        )

# TODO: Third tab/Page for analysis
