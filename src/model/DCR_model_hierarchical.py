import json
import pm4py
from pm4py.objects.dcr.hierarchical.obj import HierarchicalDcrGraph
from pm4py.objects.dcr.exporter import exporter as dcr_exporter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import pandas as pd
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer



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
                graph.nestedgroups_map[relation] = and_group
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
            graph.nestedgroups_map[relation] = or_group

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
dcr_exporter.apply(graph, "D:\\Github\\02269-Process-mining-project\\data\\dcr_model_hierarchical.xml")
dcr_exporter.apply(graph_demo, "D:\\Github\\02269-Process-mining-project\\data\\dcr_model_demo_hierarchical.xml")

# conformance checking with the event log
# log = pm4py.read_xes("D:\\Github\\02269-Process-mining-project\\data\\student-1-3.xes")
log = pm4py.read_xes("D:\\Github\\02269-Process-mining-project\\data\\students-10000.xes")
print("please wait, this may take a while...")
conformance_results = pm4py.conformance_dcr(log, graph, group_key="org:resource", return_diagnostics_dataframe=True)
print(conformance_results)

# Export conformance results to CSV
conformance_results.to_csv('D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\conformance_results_hierarchical.csv', index=False)

# Ensure the timestamp column is correctly parsed
log["time:timestamp"] = pd.to_datetime(log["time:timestamp"])

# Helper function to filter DataFrame by Case IDs
def filter_log_by_case_ids(df, case_ids):
    return df[df["case:concept:name"].isin(case_ids)]

# Convert DataFrame to EventLog
def dataframe_to_eventlog(df):
    event_log = EventLog()
    for case_id, group in df.groupby("case:concept:name"):
        trace = Trace()
        trace.attributes["concept:name"] = case_id
        for _, event_data in group.iterrows():
            event = {
                key: event_data[key] for key in df.columns if not pd.isnull(event_data[key])
            }
            trace.append(event)
        event_log.append(trace)
    return event_log

# Generate and save Petri net
def generate_petri_net(event_log, log_name):
    print(f"Generating Petri net for {log_name}...")
    net, initial_marking, final_marking = alpha_miner.apply(event_log)

    # Visualize the Petri net
    print(f"Visualizing Petri net for {log_name}...")
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    # Save the Petri net visualization
    pn_visualizer.save(gviz, f"D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\{log_name}_petri_net_hierarchical.png")

    print(f"Petri net for {log_name} generated and saved!")

# Split the log based on deviation
print("Splitting the log based on deviation values...")
conformant_case_ids = conformance_results[conformance_results['no_dev_total'] < 5]['case_id'].tolist()
non_conformant_case_ids = conformance_results[conformance_results['no_dev_total'] >= 5]['case_id'].tolist()

conformant_log_df = filter_log_by_case_ids(log, conformant_case_ids)
non_conformant_log_df = filter_log_by_case_ids(log, non_conformant_case_ids)

# Convert DataFrames to EventLogs
print("Converting DataFrames to EventLog format...")
conformant_log = dataframe_to_eventlog(conformant_log_df)
non_conformant_log = dataframe_to_eventlog(non_conformant_log_df)

# Export the logs to XES format
print("Exporting the logs to XES format...")
xes_exporter.apply(conformant_log, "D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\conformant_log_hierarchical.xes")
xes_exporter.apply(non_conformant_log, "D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\non_conformant_log_hierarchical.xes")

# Attention : the following code is commneted out, because it costs too much time to run
# Generate Petri nets
# generate_petri_net(conformant_log, "test_conformant_log")
# generate_petri_net(non_conformant_log, "test_non_conformant_log")

print("Logs successfully split, exported!")
