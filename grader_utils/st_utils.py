import datetime

import streamlit as st


def set_st_session_state() -> None:
    if "MAX_ASSESSMENT_FILES" not in st.session_state:
        st.session_state["MAX_ASSESSMENT_FILES"] = 3
    if "programs_dict" not in st.session_state:
        st.session_state["programs_dict"] = {
            "word": "Word",
            "excel": "Excel",
            "ppt": "PowerPoint",
        }
    if "word_answer_key" not in st.session_state:
        st.session_state["word_answer_key"] = None
    if "excel_answer_key" not in st.session_state:
        st.session_state["excel_answer_key"] = None
    if "ppt_answer_key" not in st.session_state:
        st.session_state["ppt_answer_key"] = None

    if "section_num" not in st.session_state:
        st.session_state["section_num"] = None
    if "n_students" not in st.session_state:
        st.session_state["n_students"] = None
    if "student_df" not in st.session_state:
        st.session_state["student_df"] = None
    if "student_object_list" not in st.session_state:
        st.session_state["student_object_list"] = None

    if "word_uploaded" not in st.session_state:
        st.session_state["word_uploaded"] = False
    if "excel_uploaded" not in st.session_state:
        st.session_state["excel_uploaded"] = False
    if "ppt_uploaded" not in st.session_state:
        st.session_state["ppt_uploaded"] = False

    if "word_graded" not in st.session_state:
        st.session_state["word_graded"] = False
    if "excel_graded" not in st.session_state:
        st.session_state["excel_graded"] = False
    if "ppt_graded" not in st.session_state:
        st.session_state["ppt_graded"] = False

    if "start_date" not in st.session_state:
        st.session_state["start_date"] = datetime.datetime.today().replace(day=1)

    if "zip_file" not in st.session_state:
        st.session_state["zip_file"] = None


def clear_student_session_state() -> None:
    st.session_state.section_num = None
    st.session_state.n_students = None
    st.session_state.student_df = None
    st.session_state.student_object_list = None


def clear_assessment_session_state() -> None:
    st.session_state.word_uploaded = False
    st.session_state.excel_uploaded = False
    st.session_state.ppt_uploaded = False
    st.session_state.word_graded = False
    st.session_state.excel_graded = False
    st.session_state.ppt_graded = False
    st.session_state.zip_file = None


def display_student_info_hint(container) -> None:
    container.info(
        "Please select student information file to upload and select the section you are teaching."
    )


def display_assessment_info_hint(container) -> None:
    container.info("Please select assessment files to upload and grade.")
