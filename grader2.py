import warnings

import streamlit as st

from app_utils import dates, errors, fileio, logging_config, models, process, st_helper

logger = logging_config.get_logger()

# st_helper.set_session_state()

if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False
if "student_info" not in st.session_state:
    st.session_state.student_info = None
if "test_results" not in st.session_state:
    st.session_state.test_results = None
if "n_students" not in st.session_state:
    st.session_state.n_students = None

st.title("Series-Based Class Assessment Auto Grader")

with st.expander(label="Upload CSV Files", expanded=not st.session_state.files_uploaded):
    csv_files = st.file_uploader(
        "Upload assessment files and student information file here. For the csv file containing your student info, please make sure it only contains the students in your section and only 'section', 'email', 'first name', and 'last name' columns are in the file. For the assessment csv files, please make sure 'assessment' or 'quiz' is in the file name and student information are correct.",
        type=["csv"],
        accept_multiple_files=True,
    )
    if csv_files:
        if not st.session_state.files_uploaded:
            st.session_state.files_uploaded = True
            st.rerun()

        handler = fileio.FileHandler(csv_files)
        st.session_state.student_info = handler.student_info()
        st.session_state.test_results = handler.test_results()
    else:
        st.session_state.files_uploaded = False
        st.session_state.student_info = None
        st.session_state.test_results = None

if csv_files:
    with st.expander(
        label="Student Information",
        expanded=csv_files is not None and st.session_state.student_info is not None,
    ):
        if st.session_state.student_info is not None and len(st.session_state.student_info) > 1:
            raise errors.TooManyFilesError(
                f"Too many files containing student information: {len(st.session_state.student_info)}, Please upload a maximum of 1 student information file."
            )
        if not st.session_state.student_info:
            warnings.warn("Please include at least 1 student information file.")
            st.warning("Please include at least 1 student information file.")
            st.stop()

        # TODO: process student info, fix multiple email error, fix multiple name error, make sure column is in correct order ...
        st.session_state.student_info[0] = process.process_multiple_email(
            st.session_state.student_info[0]
        )
        student_df = st.data_editor(
            st.session_state.student_info[0],
            hide_index=False,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "section": st.column_config.NumberColumn(
                    "Section",
                    help="Student's class section",
                    required=False,
                ),
                "email": st.column_config.TextColumn(
                    "Email",
                    help="Student's email address",
                    validate=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                ),
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
            },
        )
        st.session_state.student_info[0] = student_df
        st.session_state.n_students = student_df.shape[0]

    with st.form("filter_form"):
        # TODO: date and section selection

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("Filter students")
            name_filter = st.checkbox("Name", value=True)
            email_filter = st.checkbox("Email", value=True)
            section_filter = st.checkbox("Section", value=False)

        with col2:
            st.markdown("Section Info")
            cohort = st.date_input("not implemented")
            section = st.selectbox("not implemented", options=[1, 2, 3])

        submitted = st.form_submit_button("Filter")

st.write(st.session_state.test_results)

# show filtering options
# show grading results summary
# show download excel file button
