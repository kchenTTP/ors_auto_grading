import streamlit as st

from app_utils import dates, errors, fileio, logger, models, process, st_helper

st_helper.set_session_state()

st.title("TechConnect Series-Based Class Assessment Auto Grader")

with st.container(border=True):
    st.subheader("File Upload")
    csv_files = st.file_uploader(
        "Upload assessment files and student information file here.", type=["csv"]
    )
