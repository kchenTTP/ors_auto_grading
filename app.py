#  cSpell: ignore streamlit, dataframe, selectbox, pydantic, funcs
import io
from pydantic import BaseModel, EmailStr, PastDate
import streamlit as st
import pandas as pd


# VARIABLES
programs = ["Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint"]
programs_short = ["word", "excel", "ppt"]


# FUNCTIONS & CLASSES
class QuestionAnswerPair(BaseModel):
    question: str
    answer: str


class AnswerKey(BaseModel):
    program: str
    questions_and_answers: list[QuestionAnswerPair]


class Assessment(BaseModel):
    software: str
    timestamp: PastDate
    score: float
    response: list[QuestionAnswerPair]


class Student(BaseModel):
    name: str
    email: EmailStr
    tests: list[Assessment]
    report: None  # TODO: File Object?


class DataFrameUtils:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def __repr__(self) -> str:
        return repr(self.df)

    def get_section_nums(self) -> list:
        if not self.__is_student_dataframe(self.df):
            raise ValueError(
                "Error: 'Section' Info Not Found\n \
                Data does not contain a column named 'Section' (case-sensitive). \
                Please make sure you're using the right file or rename the column containing the section numbers to 'Section'."
            )

        sections = self.df.Section.unique().tolist()
        sections.sort()

        return sections

    def get_section_df(self, section_num: int) -> pd.DataFrame:
        if not self.__is_student_dataframe(self.df):
            raise ValueError(
                "Error: 'Section' Info Not Found\n \
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
                "Error: Not Student Data\n \
                Data does not contain a column named 'Section' (case-sensitive). \
                Please make sure you're using the right file or rename the column containing the section numbers to 'Section'."
            )

        if include_email:
            stu_info_df = self.__section_info_all[["First Name", "Last Name", "Email"]]
            stu_info_df["Email"] = (
                stu_info_df["Email"].str.lower().str.strip().str.replace(" ", "")
            )
        else:
            stu_info_df = self.__section_info_all[["First Name", "Last Name"]]

        stu_info_df["First Name"] = (
            stu_info_df["First Name"].str.lower().str.strip().str.replace(" ", "")
        )
        stu_info_df["Last Name"] = (
            stu_info_df["Last Name"].str.lower().str.strip().str.replace(" ", "")
        )
        return stu_info_df

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

    def convert_to_excel(self) -> None:
        # TODO: Write to excel function
        pass

    # TODO: Make data validation methods


class FileUtils:
    def __init__(self, file: io.BytesIO) -> None:
        self.__file = file
        self.__filename = file.name

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


# STREAMLIT APP
st.set_page_config(initial_sidebar_state="collapsed")

# SIDEBAR
with st.sidebar:
    st.header("Settings")
    with st.form("settings_form", border=True):
        st.subheader("Section Information")
        use_saved_on = st.toggle("Use previously downloaded student info csv file")

        settings_saved = st.form_submit_button("Save")

    if settings_saved:
        st.success("Settings Saved Successfully", icon="✅")


# MAIN PAGE
st.title("ORS Assessment AutoGrader")

student_info_tab, assessment_tab = st.tabs(["Section Information", "Assessment Grader"])

## Student Information
with student_info_tab:
    with st.container(border=True):
        st.subheader("Section Information")
        st.markdown(
            """
            Upload student information file here. Make sure all student information are correct before uploading or autograder may not work properly.\n
            > 💡 Toggle the "Use previously downloaded student info csv file" switch on in the sidebar to use the csv file you've downloaded from this page.
            """
        )

        student_file = st.file_uploader(
            "Upload student information file here",
            type="csv",
            label_visibility="hidden",
        )

    if student_file is not None:
        students = FileUtils(student_file)
        student_data_utils = students.to_dataframe_utils()

        sections_list = student_data_utils.get_section_nums()
        section_num = st.selectbox(
            "Which section do you teach?", options=sections_list, index=None
        )
        st.divider()

        if section_num is not None:
            section_df = student_data_utils.get_section_df(section_num)
            student_df = student_data_utils.get_student_info()
            # *Important: Student Information Variable
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
                        validate="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    ),
                },
            )

            student_info_csv_data = DataFrameUtils(edited_student_df).convert_to_csv()

            st.download_button(
                label="Download student data as CSV",
                data=student_info_csv_data,
                file_name=f"ORS_Section{section_num}_Student_Info.csv",
                mime="text/csv",
                type="primary",
            )


## Assessment AutoGrader
with assessment_tab:
    with st.container(border=True):
        st.subheader("Upload Files")
        uploaded_files = st.file_uploader(
            "Upload assessment result files here",
            type="csv",
            accept_multiple_files=True,
        )

    # if uploaded_files is not None:
    #     n_files = len(uploaded_files)

    #     with st.container(border=True):
    #         st.subheader('Class Information')
    #         student_data = st.selectbox('Select student information', options=[file.name for file in uploaded_files], index=None)
    #         if uploaded_files:
    #             section_num = st.number_input('Which section do you teach?', min_value=1, max_value=4, value=None)

    #     ## Select Programs to grade
    #     with st.container(border=True):
    #         st.subheader('Select Programs')
    #         # for p, ps in zip(programs, programs_short):
    #         #     st.checkbox(f'{p}', key=f'select_{ps}')
    #         select_word = st.checkbox(f':blue[Microsoft Word]', key='select_word')
    #         select_excel = st.checkbox(f':green[Microsoft Excel]', key='select_excel')
    #         select_ppt = st.checkbox(f':orange[Microsoft PowerPoint]', key='select_ppt')

    #         if select_word:
    #             word_name = st.selectbox('Select Word assessment data', options=[file.name for file in uploaded_files], index=None)
    #         if select_excel:
    #             excel_name = st.selectbox('Select Excel assessment data', options=[file.name for file in uploaded_files], index=None)
    #         if select_ppt:
    #             ppt_name = st.selectbox('Select PowerPoint assessment data', options=[file.name for file in uploaded_files], index=None)

    # ## Show Student Data
    # if uploaded_files is not None:
    #     st.write(uploaded_files)
    #     for file in uploaded_files:
    #         if select_word and file.name == word_name:
    #             word_file = file
    #             st.write(word_file)
    #             st.write(type(word_file))
    #             word_df = pd.read_csv(word_file)
    #             st.dataframe(word_df)
    #         if select_excel and file.name == excel_name:
    #             excel_file = file
    #         if select_ppt and file.name == ppt_name:
    #             ppt_file = file
