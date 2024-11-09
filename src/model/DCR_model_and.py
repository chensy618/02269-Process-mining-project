import json
import pm4py
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.objects.dcr.exporter import exporter as dcr_exporter

# Load the JSON data from the file
with open('src\\pre-requisites\\format_course_prerequisites.json', 'r') as file:
    data = json.load(file)

# Initialize the DCR graph
graph = DcrGraph()
graph_demo = DcrGraph()

# Function to add AND conditions
def add_and_relation(graph, course, relations):
    for relation in relations:
        graph.events.add(relation)
        graph.labels.add(relation)
        graph.label_map[relation] = relation
        graph.conditions[course] = graph.conditions.get(course, set()) | {relation}

# Filter data to only include courses with a non-empty "and" condition and an empty "or" condition
filtered_data = {
    course: prereq 
    for course, prereq in data.items() 
    if 'and' in prereq and prereq['and'] and ('or' not in prereq or not prereq['or'])
}

# Iterate over the filtered data to create the full DCR graph
for course, prerequisites in filtered_data.items():
    graph.events.add(course)
    graph.labels.add(course)
    graph.label_map[course] = course
    add_and_relation(graph, course, prerequisites['and'])

# Use the top 20 courses to create a demo DCR graph for testing
for course, prerequisites in list(filtered_data.items())[:20]:
    graph_demo.events.add(course)
    graph_demo.labels.add(course)
    graph_demo.label_map[course] = course
    add_and_relation(graph_demo, course, prerequisites['and'])

# View and export the DCR demo graph
pm4py.view_dcr(graph_demo)

# View and export the full DCR graph
pm4py.view_dcr(graph)

# Export the DCR demo graph to a file
output_file_demo = 'src\\model\\course_prerequisites_demo.dcr'
dcr_exporter.apply(graph_demo, output_file_demo)
print(f"DCR demo model created and exported to {output_file_demo}")

# Export the full DCR graph to a file
output_file_full = 'src\\model\\course_prerequisites_and.dcr'
dcr_exporter.apply(graph, output_file_full)
print(f"DCR model created and exported to {output_file_full}")
