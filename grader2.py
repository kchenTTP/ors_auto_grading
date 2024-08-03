import streamlit as st

from app_utils import dates, errors, fileio, logger, models, process, st_helper

# st_helper.set_session_state()

if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False

st.title("Series-Based Class Assessment Auto Grader")

with st.expander(label="Upload CSV Files", expanded=not st.session_state.files_uploaded):
    csv_files = st.file_uploader(
        "Upload assessment files and student information file here.", type=["csv"]
    )
    if csv_files is not None:
        if not st.session_state.files_uploaded:
            st.session_state.files_uploaded = True
            st.rerun()

        # convert to dataframe
        # handler = fileio.FileHandler(csv_files)

        # store df as hashtable then to session_state


# with st.container(border=True):
#     st.subheader("File Upload")
#     csv_files = st.file_uploader(
#         "Upload assessment files and student information file here.", type=["csv"]
#     )

#     if csv_files is not None:
#         handler = fileio.FileHandler(csv_files)
