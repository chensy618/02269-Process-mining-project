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

# Function to add AND conditions with nested OR using placeholders
def add_and_relation(graph, course, relations):
    for relation in relations:
        if isinstance(relation, list):  # Nested OR relationship within an AND condition
            # Create a placeholder event for the OR group within the AND relation
            placeholder_event = f"subgroup_{course}_and"
            graph.events.add(placeholder_event)
            graph.labels.add(placeholder_event)
            graph.marking.included.add(relation)
            graph.label_map[placeholder_event] = f"Subgroup for {course} (OR)"

            # Add each OR condition event explicitly to the subgroup
            for sub_relation in relation:
                graph.events.add(sub_relation)
                graph.labels.add(sub_relation)
                graph.label_map[sub_relation] = sub_relation

                # Link each individual event to the placeholder for clear grouping
                graph.conditions[placeholder_event] = graph.conditions.get(placeholder_event, set()) | {sub_relation}

            # Add a condition from the main course to the placeholder event (representing the OR group)
            graph.conditions[course] = graph.conditions.get(course, set()) | {placeholder_event}
        else:
            # Standard AND condition, linking directly
            graph.conditions[course] = graph.conditions.get(course, set()) | {relation}

# Function to handle OR conditions using a placeholder event
def add_or_relation(graph, course, relations):
    # Flatten the OR groups into a single list of responses
    flattened_relations = [relation for or_group in relations for relation in or_group]
    
    # Only proceed if there are OR conditions
    if flattened_relations:
        # Create a placeholder event for all OR conditions for the course
        placeholder_event = f"subgroup_{course}_or"
        graph.events.add(placeholder_event)
        graph.labels.add(placeholder_event)
        graph.label_map[placeholder_event] = f"Subgroup for {course} (OR)"

        # Add each OR prerequisite as an individual event in the subgroup
        for relation in flattened_relations:
            graph.events.add(relation)
            graph.labels.add(relation)
            graph.label_map[relation] = relation

            # Link each individual event to the placeholder for clear grouping
            graph.conditions[placeholder_event] = graph.conditions.get(placeholder_event, set()) | {relation}

        # Add a condition from the main course to the placeholder event (representing the OR group)
        graph.conditions[course] = graph.conditions.get(course, set()) | {placeholder_event}

# Iterate over the parsed data to create the full DCR graph
for course, prerequisites in data.items():
    # Add the course as an event in the DCR graph
    graph.events.add(course)
    graph.labels.add(course)
    graph.label_map[course] = course

    # Handle AND conditions
    add_and_relation(graph, course, prerequisites.get('and', []))
    
    # Handle OR conditions
    add_or_relation(graph, course, prerequisites.get('or', []))

# Use the top 20 courses to create a demo DCR graph for testing
for course, prerequisites in list(data.items())[:20]:
    # Add the course as an event in the demo DCR graph
    graph_demo.events.add(course)
    graph_demo.labels.add(course)
    graph_demo.label_map[course] = course

    # Handle AND conditions
    add_and_relation(graph_demo, course, prerequisites.get('and', []))
    
    # Handle OR conditions
    add_or_relation(graph_demo, course, prerequisites.get('or', []))

# View and export the DCR demo graph
pm4py.view_dcr(graph_demo)

# View and export the full DCR graph
pm4py.view_dcr(graph)

# Export the DCR demo graph to a file
output_file_demo = 'src\\model\\course_prerequisites_demo.dcr'
dcr_exporter.apply(graph_demo, output_file_demo)
print(f"DCR demo model created and exported to {output_file_demo}")

# Export the full DCR graph to a file
output_file_full = 'src\\model\\course_prerequisites.dcr'
dcr_exporter.apply(graph, output_file_full)
print(f"DCR model created and exported to {output_file_full}")


log = pm4py.read_xes("D:\\Github\\02269-Process-mining-project\\data\\original_data.xes")
align_res = pm4py.optimal_alignment_dcr(log, graph, return_diagnostics_dataframe=True)
print(align_res)
conf_res = pm4py.conformance_dcr(log, graph, return_diagnostics_dataframe=True)
print(conf_res)
# export the results to a csv file
conf_res.to_csv('D:\\Github\\02269-Process-mining-project\\data\\conformance_results.csv', index=False)
align_res.to_csv('D:\\Github\\02269-Process-mining-project\\data\\alignment_results.csv', index=False)