import streamlit as st


def set_session_state():
    raise NotImplementedError


def clear_student_session_state():
    st.session_state.section_num = None
    st.session_state.n_students = None
    st.session_state.student_df = None
    st.session_state.student_object_list = None


def clear_assessment_session_state():
    st.session_state.word_uploaded = False
    st.session_state.excel_uploaded = False
    st.session_state.ppt_uploaded = False
    st.session_state.word_graded = False
    st.session_state.excel_graded = False
    st.session_state.ppt_graded = False
    st.session_state.zip_file = None
