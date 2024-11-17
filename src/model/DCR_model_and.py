import json
import pm4py
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.objects.dcr.exporter import exporter as dcr_exporter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import pandas as pd
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer

# Load the JSON data from the file
with open('D:/Github/02269-Process-mining-project/src/pre-requisites/format_course_prerequisites.json', 'r') as file:
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
        graph.marking.included.add(relation)
        graph.marking.included.add(course)
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

# include all the activities in the DCR graph, add marking for each activity


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



log = pm4py.read_xes("D:\\Github\\02269-Process-mining-project\\data\\students-10000.xes")
print("please wait, this may take a while...")
conf_res = pm4py.conformance_dcr(log, graph, return_diagnostics_dataframe=True)
# export the results to a csv file
conf_res.to_csv('D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\conformance_results.csv', index=False)

print(conf_res.head())

print(type(log))  # 确认 log 的类型
print(log[:5])    # 打印 log 的前 5 个元素，观察其结构


# 确保时间戳列正确解析
log["time:timestamp"] = pd.to_datetime(log["time:timestamp"])

# Helper function to filter DataFrame by Case IDs
def filter_log_by_case_ids(df, case_ids):
    return df[df["case:concept:name"].isin(case_ids)]

# 将 DataFrame 转换为 EventLog
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

# 分割日志
print("Splitting the log based on fitness values...")
fitting_case_ids = conf_res[conf_res['dev_fitness'] == 1]['case_id'].tolist()
non_fitting_case_ids = conf_res[conf_res['dev_fitness'] < 1]['case_id'].tolist()

fitting_log_df = filter_log_by_case_ids(log, fitting_case_ids)
non_fitting_log_df = filter_log_by_case_ids(log, non_fitting_case_ids)

# 转换为 EventLog
print("Converting DataFrames to EventLog format...")
fitting_log = dataframe_to_eventlog(fitting_log_df)
non_fitting_log = dataframe_to_eventlog(non_fitting_log_df)

# 导出为 XES 文件
print("Exporting the logs to XES format...")
xes_exporter.apply(fitting_log, "D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\fitting_log_and.xes")
xes_exporter.apply(non_fitting_log, "D:\\Github\\02269-Process-mining-project\\data\\conformance_checking\\non_fitting_log_and.xes")

print("Logs successfully split and exported!")

# Helper function to generate and visualize Petri net
def generate_petri_net(event_log, log_name):
    print(f"Generating Petri net for {log_name}...")

    # Apply the Alpha Miner algorithm
    net, initial_marking, final_marking = alpha_miner.apply(event_log)

    # Visualize the Petri net
    print(f"Visualizing Petri net for {log_name}...")
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    # Save the Petri net visualization
    pn_visualizer.save(gviz, f"D:\\Github\\02269-Process-mining-project\\data\\{log_name}_petri_net_and.png")

    print(f"Petri net for {log_name} generated and saved!")

# Attention : the following code is commneted out, because it costs too much time to run
# Generate Petri nets for both logs
# generate_petri_net(fitting_log, "fitting_log_and")
# generate_petri_net(non_fitting_log, "non_fitting_log_and")











