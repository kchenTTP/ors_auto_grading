import streamlit as st
import pandas as pd


# VARIABLES
programs = ['Microsoft Word', 'Microsoft Excel', 'Microsoft PowerPoint']
programs_short = ['word', 'excel', 'ppt']


# FUNCTIONS

## File IOs
@st.cache_data
def read_csv(f) -> pd.DataFrame:
    df = pd.read_csv(f)
    return df

@st.cache_data
def get_section_nums(df: pd.DataFrame) -> list:
    sections = df.Section.unique().tolist()
    sections.sort()
    return sections

@st.cache_data
def get_section_df(df: pd.DataFrame, section_num: int) -> pd.DataFrame:
    df = df.loc[(df.Section == section_num) & (df.Status == 'Active')].sort_values(by=['First Name'], ascending=True)
    df.reset_index(inplace=True)
    return df

@st.cache_data
def get_student_info(df: pd.DataFrame, include_email: bool) -> pd.DataFrame:
    if include_email:
        df = df[['First Name', 'Last Name', 'Email']]
        df['Email'] = df['Email'].str.lower().str.strip().str.replace(' ', '')
    else:
        df = df[['First Name', 'Last Name']]
    
    df['First Name'] = df['First Name'].str.lower().str.strip().str.replace(' ', '')
    df['Last Name'] = df['Last Name'].str.lower().str.strip().str.replace(' ', '')
    return df

@st.cache_data
def convert_to_csv(df: pd.DataFrame) -> str:
    return df.to_csv(index=False).encode('utf-8')




# STREAMLIT APP
st.set_page_config(initial_sidebar_state="collapsed")

# SIDEBAR    
with st.sidebar:
    st.header('Settings')
    with st.form('settings_form',border=True):
        st.subheader('Section Information')
        use_saved_on = st.toggle('Use previously downloaded student info csv file')
        
        settings_saved = st.form_submit_button('Save')
    
    if settings_saved:
        st.success('Settings Saved Successfully', icon='✅')


# MAIN PAGE
st.title('ORS Assessment AutoGrader')

student_info_tab, assessment_tab = st.tabs(['Section Information', 'Assessment Grader'])

## Student Information
with student_info_tab:
    with st.container(border=True):
        st.subheader('Section Information')
        st.markdown('''
                 Upload student information file here. Make sure all student information are correct before uploading or autograder may not work properly.\n
                 > 💡 Toggle the "Use previously downloaded student info csv file" switch on in the sidebar to use the csv file you've downloaded from this page.
                 ''')
        
        student_file = st.file_uploader('Upload student information file here', type='csv',label_visibility='hidden')
    
    if student_file is not None:
        student_df = read_csv(student_file)
        
        sections_list = get_section_nums(student_df)
        section_num = st.selectbox('Which section do you teach?', options=sections_list, index=None)
        st.divider()
        
        if section_num is not None:
            section_df = get_section_df(student_df, section_num)
            student_df = get_student_info(section_df, include_email=True)
            edited_student_df = st.data_editor(student_df, hide_index=False, use_container_width=True, num_rows='dynamic')
            
            student_info_csv = convert_to_csv(edited_student_df)
            st.download_button(
                label="Download student data as CSV",
                data=student_info_csv,
                file_name=f'ORS_section{section_num}_student_info.csv',
                mime='text/csv',
                type='primary'
            )
            

## Assessment AutoGrader
with assessment_tab:
    with st.container(border=True):
        st.subheader('Upload Files')
        uploaded_files = st.file_uploader('Upload assessment result files here', type='csv', accept_multiple_files=True)

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
