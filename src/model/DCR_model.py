import json
import pm4py
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.objects.dcr.exporter import exporter as dcr_exporter

# Load the JSON data from the file
with open('src\pre-requisites\compute_course_prerequisites.json', 'r') as file:
    data = json.load(file)

# Initialize the DCR graph
graph = DcrGraph()
graph_demo = DcrGraph()

# Function to add conditions (AND relationships)
def add_conditions(graph, course, conditions):
    for condition in conditions:
        if isinstance(condition, list):  # Nested AND relationships
            for sub_condition in condition:
                graph.conditions[course] = graph.conditions.get(course, set()) | {sub_condition}
        else:
            graph.conditions[course] = graph.conditions.get(course, set()) | {condition}

# Function to add responses (OR relationships)
def add_responses(graph, course, responses):
    for or_group in responses:
        for response in or_group:
            graph.responses[course] = graph.responses.get(course, set()) | {response}

# Iterate over the parsed data to create the DCR graph
for course, prerequisites in data.items():
    # Add the course as an event in the DCR graph
    graph.events.add(course)
    graph.labels.add(course)
    graph.label_map[course] = course

    # Handle AND conditions
    add_conditions(graph, course, prerequisites.get('and', []))
    
    # Handle OR conditions
    add_responses(graph, course, prerequisites.get('or', []))
    
# Generate a demo DCR graph for testing by using the top 20 courses in the JSON file
for course, prerequisites in list(data.items())[:20]:
    # Add the course as an event in the DCR graph
    graph_demo.events.add(course)
    graph_demo.labels.add(course)
    graph_demo.label_map[course] = course

    # Handle AND conditions
    add_conditions(graph_demo, course, prerequisites.get('and', []))
    
    # Handle OR conditions
    add_responses(graph_demo, course, prerequisites.get('or', []))

pm4py.view_dcr(graph_demo)
pm4py.view_dcr(graph)

# Export the DCR graph to a file
dcr_exporter.apply(graph, 'src\model\compute_course_prerequisites.dcr')

