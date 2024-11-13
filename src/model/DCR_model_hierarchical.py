import json
import pm4py
from pm4py.objects.dcr.hierarchical.obj import HierarchicalDcrGraph
from pm4py.objects.dcr.exporter import exporter as dcr_exporter

# Load JSON data for course prerequisites
with open('src\\pre-requisites\\format_course_prerequisites.json', 'r') as file:
    data = json.load(file)

# Initialize hierarchical DCR graph
graph = HierarchicalDcrGraph()
graph_demo = HierarchicalDcrGraph()

# Function to handle AND conditions with nested OR using hierarchical groups
def add_and_relation(graph, course, relations):
    if relations:  # Check if the relations list is empty
        and_group = f"and_group_{course}"
        graph.nestedgroups[and_group] = set()
        for relation in relations:
            if isinstance(relation, list):  # Nested OR within an AND
                or_group = f"or_group_{course}_{len(graph.nestedgroups)}"
                graph.nestedgroups[or_group] = set(relation)
                graph.nestedgroups[and_group].add(or_group)
                graph.marking.included.add(relation)
                graph.marking.included.add(or_group)
                graph.marking.included.add(and_group)
                
                # Add OR group events and label mappings
                for sub_relation in relation:
                    graph.events.add(sub_relation)
                    graph.labels.add(sub_relation)
                    graph.marking.included.add(sub_relation)
                    graph.label_map[sub_relation] = sub_relation
            else:
                graph.events.add(relation)
                graph.labels.add(relation)
                graph.label_map[relation] = relation
                graph.nestedgroups[and_group].add(relation)
                graph.marking.included.add(relation)
                graph.marking.included.add(and_group)

        # Add condition linking the main course event to the AND group
        graph.conditions[course] = graph.conditions.get(course, set()) | {and_group}

# Function to handle OR conditions using hierarchical groups
def add_or_relation(graph, course, relations):
    if relations:  # Check if the relations list is empty
        or_group = f"or_group_{course}"
        graph.nestedgroups[or_group] = set()

        # Flatten the list of relations to handle nested lists (for OR groups within AND conditions)
        flattened_relations = [item for sublist in relations for item in (sublist if isinstance(sublist, list) else [sublist])]
        
        # Add each OR prerequisite as an individual event in the OR group
        for relation in flattened_relations:
            graph.events.add(relation)
            graph.labels.add(relation)
            graph.label_map[relation] = relation
            graph.marking.included.add(relation)
            graph.nestedgroups[or_group].add(relation)

        # Add condition linking the main course event to the OR group
        graph.conditions[course] = graph.conditions.get(course, set()) | {or_group}


# Iterate over data to create the full DCR graph
for course, prerequisites in data.items():
    # Add course event and label mappings
    graph.events.add(course)
    graph.labels.add(course)
    graph.label_map[course] = course
    graph.marking.included.add(course)

    # Add AND and OR relations
    add_and_relation(graph, course, prerequisites.get('and', []))
    add_or_relation(graph, course, prerequisites.get('or', []))

# Demo DCR graph for top 20 courses
for course, prerequisites in list(data.items())[:20]:
    graph_demo.events.add(course)
    graph_demo.labels.add(course)
    graph_demo.marking.included.add(course)
    graph_demo.label_map[course] = course

    # Add AND and OR relations
    add_and_relation(graph_demo, course, prerequisites.get('and', []))
    add_or_relation(graph_demo, course, prerequisites.get('or', []))

# View and export the DCR graphs
pm4py.view_dcr(graph_demo)
pm4py.view_dcr(graph)


# Export the DCR graphs to files
output_file_demo = 'src\\model\\course_prerequisites_demo.dcr'
dcr_exporter.apply(graph_demo, output_file_demo)
print(f"DCR demo model created and exported to {output_file_demo}")

output_file_full = 'src\\model\\course_prerequisites.dcr'
dcr_exporter.apply(graph, output_file_full)
print(f"DCR model created and exported to {output_file_full}")

# export to the xml file
dcr_exporter.apply(graph, "D:\\Github\\02269-Process-mining-project\\data\\dcr_model.xml")
dcr_exporter.apply(graph_demo, "D:\\Github\\02269-Process-mining-project\\data\\dcr_model_demo.xml")

# conformance checking with the event log
# log = pm4py.read_xes("D:\\Github\\02269-Process-mining-project\\data\\student-1-3.xes")
log = pm4py.read_xes("D:\\Github\\02269-Process-mining-project\\data\\students-1000.xes")

conformance_results = pm4py.conformance_dcr(log, graph, group_key="org:resource", return_diagnostics_dataframe=True)
print(conformance_results)

# Export conformance results to CSV
conformance_results.to_csv('D:\\Github\\02269-Process-mining-project\\data\\conformance_results-1000.csv', index=False)
