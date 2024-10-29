import json
import re

# Load the JSON data from the file
with open('src\pre-requisites\course_prerequisites.json', 'r') as file:
    data = json.load(file)

# extract the prerequisites for courses starting with "2"
parsed_data = {}
for course, prereq in data.items():
    # check if the course starts with "2"
    if course.startswith('2'):
        # initialize the lists for the conditions
        or_conditions = []
        and_conditions = []
        
        # check if the prerequisites are defined
        if prereq:
            # split the prerequisites by "and"
            and_parts = re.split(r'(?i)\band\b', prereq)
            
            for part in and_parts:
                # if "or" is present, split the part by "or"
                if 'or' in part:
                    or_conditions.append([p.strip('() ') for p in re.split(r'(?i)\bor\b', part)])
                else:
                    # if no "or" is present, add the part to the "and" conditions
                    and_conditions.append(part.strip('() '))

        # add the parsed data to the dictionary
        parsed_data[course] = {
            'or': or_conditions,
            'and': and_conditions
        }

# create a new JSON file with the parsed data
output_file = 'src\pre-requisites\compute_course_prerequisites.json'
try:
    with open(output_file, 'x') as outfile:
        json.dump(parsed_data, outfile, indent=4)
except FileExistsError:
    with open(output_file, 'w') as outfile:
        json.dump(parsed_data, outfile, indent=4)
        
print(f'Parsed data saved to {output_file}')