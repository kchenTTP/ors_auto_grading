import pandas as pd
import numpy as np
import os
# from dataclasses import dataclass


# File IO
# TODO: Just use a File class with read and write methods to capture all the IO instead of a separate DataLoader & ExcelWriter class
class DataLoader:
    def __init__(self) -> None:
        pass

    # load csv
    # preprocess data
    # store data to corresponding classes


class ExcelWriter:
    def __init__(self) -> None:
        pass

    # worksheet
    # create excel file


class ReportGenerator:
    def __init__(self) -> None:
        pass

    # generate full report
    # generate individual report
    # generate answer key report
    # calculate statistics


# Student Info
class Student:
    def __init__(self) -> None:
        pass

    # Name
    # Info
    # List of Assessments
    # Individual Report


# Assessment (dataclass)
class Assessment:
    pass

    # Program Name
    # Test Date
    # Score
    # Right and wrong answers


# Questions and Answer Keys (dataclass)
class Answer:
    pass

    # Program Name
    # Questions
    # Answer Key


# TODO: Change os.path code to using pathlib module
# Create Folders & Upload Files
cwd = os.getcwd()
data_dir = "data"
if not os.path.exists(data_dir):
    path = os.path.join(cwd, data_dir)
    os.mkdir(os.path.join(cwd, data_dir))
    print("Folder created at: {}".format(path))
else:
    path = os.path.join(cwd, data_dir)

# set assessment dates
test_dates = [
    "2023-09-13",
    "2023-09-16",
    "2023-10-14",
    "2023-10-28",
    "2023-11-04",
    "2023-11-18",
    "2023-11-25",
    "2023-12-02",
    "2023-12-09",
]
test_dates = [pd.to_datetime(date) for date in test_dates]
print(test_dates)


# set what software the assessment is for
programs = ["word", "excel", "powerpoint"]
program = "excel"
student_csv = os.path.join(path, "ors_stu_info.csv")
test_responses = os.path.join(path, f"ors_{program}_assessment_responses.csv")
print(test_responses)


# Set Variables
df = pd.read_csv(student_csv)
print(df)

# drop unactive students
df = df.loc[df.Drop != True]
student_info = df[["FirstName", "LastName", "Email"]]
names = df[["FirstName", "LastName"]]
names.loc[names.FirstName == "Eleanor", ["FirstName"]] = "E"

# fix error values firstname = lastname
names.iloc[2, 0] = names.iloc[2][0].split(" ")[0]
names.iloc[2, 1] = names.iloc[2][1].split(" ")[1]
names.FirstName = names.FirstName.str.lower().str.strip()
names.LastName = names.LastName.str.lower().str.replace(" ", "")

fullnames = pd.DataFrame(names.FirstName + " " + names.LastName, columns=["fullname"])
fullnames.sort_values(by="fullname", inplace=True)


# Process Responses
test_df = pd.read_csv(test_responses)
print(test_df.info())

# rename columns
col_names_to_replace = list(test_df.columns)
col_names = ["timestamp", "email", "score", "firstname", "lastname"]

for i in range(1, len(col_names_to_replace) - 4):
    col_names.append(f"Q{i}")

col_mapper = dict.fromkeys(col_names_to_replace)
for i, col in enumerate(col_names_to_replace):
    col_mapper[col] = col_names[i]

test_df.rename(columns=col_mapper, inplace=True)


# Preprocess first and last name
test_df.firstname = test_df.firstname.str.strip().str.lower()
test_df.lastname = test_df.lastname.str.strip().str.lower()
print(test_df.head(5))

# correct error values: elsa divinagracia = elsa
test_df.loc[
    (test_df.lastname == "wilson") & (test_df.firstname == "elsa divinagracia"),
    "firstname",
] = "elsa"


# Get Answers
answer_row = test_df[test_df.score == "100 / 100"].tail(1).reset_index(drop=True)
answer_row.iloc[:, :5] = np.nan
answer_key = answer_row.iloc[:, 5:]
answer_dict = answer_key.to_dict(orient="records")[0]

print(answer_dict)


# Get Data Base on Test Date and Student Name

# convert timestamp to datetime dtype
test_df.timestamp = pd.to_datetime(
    test_df.timestamp, format="%m/%d/%Y %H:%M:%S", errors="coerce"
)
print(test_df.info())

# get all tests from test dates
all_word_assessment = test_df[
    test_df.timestamp.dt.date.isin([d.date() for d in test_dates])
]

# check student names and test count
print(
    all_word_assessment[all_word_assessment.firstname.isin(names.FirstName)]
    .firstname.value_counts()
    .sort_index()
)

# all section 4 word test data
sect4_word_test = all_word_assessment[
    all_word_assessment.firstname.isin(names.FirstName)
]
sect4_word_test.reset_index(drop=True, inplace=True)


# Generate Excel Reports

# Filter Incorrect Answers
info_df = sect4_word_test.iloc[:, :5]  # student info
responses_df = sect4_word_test.iloc[:, 5:]  # student response
wrong_answer_filter = responses_df != pd.concat(
    [answer_key] * responses_df.shape[0], ignore_index=True
)
wrong_answer_df = responses_df[
    wrong_answer_filter
]  # retain answer values that are incorrect

# final dataframe with all student information and the questions the got wrong
final_results = pd.concat([info_df, wrong_answer_df], axis=1)
print(final_results.head(2))


# Save All Results to Dictionary
cols_to_show_list = []
grades_dict = {}
cols_to_drop = ["timestamp", "email", "score", "firstname", "lastname"]

# iterate through each row
for i, row in final_results.iterrows():
    cols = list(
        final_results.columns[row.notna()]
    )  # columns that don't contain null values
    cols_to_show_list.append(cols)

    # student answers
    stu_name = row.firstname.strip() + " " + row.lastname.strip()
    test_time = str(row.timestamp)

    # check if name exists
    if grades_dict.get(stu_name) == None:
        grades_dict[stu_name] = {}
    if grades_dict[stu_name].get(test_time) == None:
        grades_dict[stu_name][test_time] = {
            "score": row.score.split(" / ")[0],
            "res": pd.DataFrame(row.loc[cols]).T.drop(columns=cols_to_drop),
            "ans": answer_row[cols].drop(columns=cols_to_drop),
        }
    else:
        print(row.timestamp)


# Get everyones score -> Save to one single excel file
pre_class_scores = []
post_class_scores = []

for name in fullnames.fullname.to_list():
    print(name)
    scores_list = []
    for i, tup in enumerate(grades_dict[name].items()):
        # get pre-class assessment score
        if i == 0:
            _, score_dict = tup
            pre_score = float(score_dict["score"])
            pre_class_scores.append(pre_score)
            print("pre-class:", pre_score)
            continue

        _, score_dict = tup
        scores_list.append(float(score_dict["score"]))

    # get post-class assessment highest score
    if len(scores_list) == 0:
        post_class_scores.append(np.NaN)
        print("post-class:", np.NAN)
    else:
        highest_grade_idx = np.argmax(np.array(scores_list))
        highest_score = scores_list[highest_grade_idx]
        post_class_scores.append(highest_score)
        print("post-class:", highest_score)
    print("------")

full_student_grades = pd.DataFrame(
    [fullnames.fullname.to_list(), pre_class_scores, post_class_scores]
).T
full_student_grades.columns = ["name", "pre-class", "post-class"]
print(full_student_grades)


# Save Results -> DataFrame -> Excel
out_path = os.path.join(cwd, "output", program)
os.makedirs(out_path, exist_ok=True)
print("Folder created at: {}".format(out_path))


# Full student report
full_report_path = os.path.join(out_path, f"0_all_student_{program}_report.xlsx")

if os.path.exists(full_report_path):
    raise Exception(
        f"File already exists at: {full_report_path}\n"
        "To create new report remove existing file"
    )
else:
    full_student_grades.to_excel(
        full_report_path, sheet_name=f"{program}_grades", index=False
    )
    if os.path.exists(full_report_path):
        print("Full student report created")


# Answers
# check length of data
names.shape[0] == final_results.firstname.value_counts().count()
names.shape[0] == final_results.lastname.value_counts().count()

questions = pd.DataFrame(col_names_to_replace.copy(), index=col_names).T
questions.iloc[0, 0] = "Questions"
questions.iloc[:, 1:5] = np.nan
print(questions)

answer_row.iloc[0, 0] = "Answers"
print(answer_row)

# concat all dataframes and save as excel file
n_files = 0

for i, row in names.iterrows():
    fname = row.FirstName
    lname = row.LastName

    cols = final_results.columns[
        final_results[final_results.firstname == fname].notna().any()
    ]
    report = pd.concat(
        [questions, answer_row, final_results[final_results.firstname == fname]], axis=0
    ).reset_index(drop=True)[cols]
    report.fillna("-", inplace=True)
    report.drop(columns=["email", "firstname", "lastname"], inplace=True)
    report.rename(columns={"timestamp": "Index"}, inplace=True)
    report.set_index("Index", inplace=True)

    file_path = os.path.join(out_path, f"{fname}_{lname}_{program}_report.xlsx")
    report.to_excel(file_path, f"{fname}_{lname}")

    if os.path.exists(file_path):
        print(f"{fname} {lname}: Report created")
        n_files += 1
    else:
        raise Exception(f"Failed to create report for: {fname} {lname}")
print("---------")
print(f"{n_files} reports created for: {program}")


# Save Answer Key
answer_df = answer_row.iloc[:, 5:]
questions_list = col_names_to_replace[5:]
answer_df.columns = questions_list

answer_path = os.path.join(out_path, f"0_{program}_answers.xlsx")
answer_df.to_excel(answer_path, f"{program}", index=False)

if os.path.exists(answer_path):
    print(f"{program}: Answer key saved")
else:
    raise Exception(f"Failed to save answer key for: {program}")
