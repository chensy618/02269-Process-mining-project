# import pm4py
# from pm4py.algo.discovery.dcr_discover.variants.dcr_discover import Discover
# from pm4py.objects.dcr.obj import DcrGraph
# from pm4py.visualization.dcr import visualizer as dcr_visualizer

# log = pm4py.read_xes("./src/output_prerequisites_log.xes")
# graph,_ = pm4py.discover_dcr(log)
# pm4py.view_dcr(graph)
# print(graph)
# dcr_graph = dcr_visualizer.apply(graph, variant="dcr")

import pm4py
from pm4py.algo.discovery.dcr_discover.variants.dcr_discover import Discover
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.visualization.dcr import visualizer as dcr_visualizer

# Read the event log
log = pm4py.read_xes("./data/output_prerequisites_log.xes")

# Discover DCR from log
graph, _ = pm4py.discover_dcr(log)

# Visualize the DCR graph
pm4py.view_dcr(graph)
# Apply visualization without the 'variant' parameter
dcr_graph = dcr_visualizer.apply(graph)  # removed the variant="dcr" argument

# Optionally, visualize the result
# pm4py.visualization.dcr.visualizer.view(dcr_graph)
dcr_visualizer.view(dcr_graph)