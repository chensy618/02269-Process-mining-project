import pandas as pd

# load the dataset
file_path = 'D:\\Github\\02269-Process-mining-project\\data\\cleaned_student_data.csv'
df = pd.read_csv(file_path)

# extract the course code from the course title
filted_df = df[df['CourseTitle'].astype(str).str.startswith('02')]

# save the filtered dataset
filtered_file_path = 'D:\\Github\\02269-Process-mining-project\\data\\filtered_student_data_02courses.csv'
print(f"Saving the filtered dataset to {filtered_file_path}")
filted_df.to_csv(filtered_file_path, index=False)
print(filted_df.head())
               