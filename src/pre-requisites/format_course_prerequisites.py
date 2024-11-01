import json
import re

# Load the JSON data from the file
with open('src\\pre-requisites\\course_prerequisites.json', 'r') as file:
    data = json.load(file)

parsed_data = {}
for course, prereq in data.items():
    # Check if the course starts with "2" and is four digits
    if course.startswith('2') and len(course) == 4:
        course = '0' + course  # Add leading "0" for four-digit courses starting with "2"
    
    # Initialize the lists for the conditions
    or_conditions = []
    and_conditions = []
    
    # Check if the prerequisites are defined
    if prereq:
        # Split the prerequisites by "and"
        and_parts = re.split(r'(?i)\band\b', prereq)
        
        for part in and_parts:
            # If "or" is present, split the part by "or"
            if 'or' in part:
                or_conditions.append([p.strip('() ') for p in re.split(r'(?i)\bor\b', part)])
            else:
                # If no "or" is present, add the part to the "and" conditions
                and_conditions.append(part.strip('() '))

    # Add the parsed data to the dictionary
    parsed_data[course] = {
        'or': or_conditions,
        'and': and_conditions
    }

# Create a new JSON file with the parsed data
output_file = 'src\\pre-requisites\\format_course_prerequisites.json'
try:
    with open(output_file, 'x') as outfile:
        json.dump(parsed_data, outfile, indent=4)
except FileExistsError:
    with open(output_file, 'w') as outfile:
        json.dump(parsed_data, outfile, indent=4)
        
print(f'Parsed data saved to {output_file}')
