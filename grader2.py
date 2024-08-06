import streamlit as st

from app_utils import dates, errors, fileio, logger, models, process, st_helper

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
    if csv_files is not None:
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

with st.expander(
    label="Student Information",
    expanded=csv_files is not None and st.session_state.student_info is not None,
):
    if st.session_state.student_info is not None and len(st.session_state.student_info) > 1:
        raise errors.TooManyFilesError(
            f"Too many files containing student information: {len(st.session_state.student_info)}, Please upload a maximum of 1 student information file."
        )
    if not st.session_state.student_info:
        raise errors.NoStudentInfoError("Please include at least 1 student information file.")

    # TODO: process student info, fix multiple email error, fix multiple name error, make sure column is in correct order ...
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

st.write(st.session_state.test_results)

# show filtering options
# show grading results summary
# show download excel file button
