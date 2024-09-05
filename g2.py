import warnings

import streamlit as st

from app_utils import (
    datetime_helper,
    errors,
    fileio,
    logging_config,
    models,
    process,
    st_helper,
)

logger = logging_config.get_logger()

# st_helper.set_session_state()

if "start_date" not in st.session_state:
    st.session_state.start_date = datetime_helper.get_start_date()
if "section" not in st.session_state:
    st.session_state.section = 1
if "filter_options" not in st.session_state:
    st.session_state.filter_options = None
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
    st.markdown("""
                - Student Info CSV:
                    - Include only students from your section.
                    - Columns required: `section`, `email`, `first name`, `last name`.
                - Assessment CSV:
                    - Ensure the file name includes "assessment" or "quiz."
                    - Verify that student information is correct""")
    csv_files = st.file_uploader(
        "Upload assessment files and student information file here. For the csv file containing your student info, please make sure it only contains the students in your section and only 'section', 'email', 'first name', and 'last name' columns are in the file. For the assessment csv files, please make sure 'assessment' or 'quiz' is in the file name and student information are correct.",
        type=["csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
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
        st.session_state.section = process.get_section_number(st.session_state.student_info[0])

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
            cohort_start_date = st.date_input("Semester Start Date", st.session_state.start_date)
            section = st.number_input(
                "Section",
                value=st.session_state.section,
                format="%d",
                min_value=1,
                step=1,
                placeholder="Section Number",
            )

        submitted = st.form_submit_button("Filter")

        if submitted:
            if not name_filter and not email_filter and not section_filter:
                st.error("Error: No filter selected")
                st.stop()
            else:
                st.session_state.filter_options = models.FilterOptions(
                    by_name=name_filter,
                    by_email=email_filter,
                    by_section=section_filter,
                    start_date=cohort_start_date,
                    section=section,
                )

st.write(st.session_state.filter_options)
st.write(st.session_state.test_results)

# show filtering options
# show grading results summary
# show download excel file button
