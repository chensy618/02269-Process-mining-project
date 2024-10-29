import pandas as pd

# Load the uploaded CSV file
file_path = 'd:/Github/02269-Process-mining-project/data/cleaned_student_data.csv'  # Update the path accordingly
student_data = pd.read_csv(file_path)

# Convert the 'GradeDate' column to datetime format to enable sorting by date
student_data['GradeDate'] = pd.to_datetime(student_data['GradeDate'])

# Sort the data by 'StudentID' and 'GradeDate' to reorder each student's records chronologically
sorted_student_data = student_data.sort_values(by=['StudentID', 'GradeDate'])

# Reset the index of the sorted data
sorted_student_data.reset_index(drop=True, inplace=True)

# Save the sorted dataset to a new CSV file
sorted_file_path = 'd:/Github/02269-Process-mining-project/data/sorted_student_data_by_date.csv'  # Update the path accordingly
sorted_student_data.to_csv(sorted_file_path, index=False)

# Print the first few rows of the sorted dataset to verify
print(sorted_student_data.head())
