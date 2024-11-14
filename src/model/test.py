import pandas as pd

import pm4py
import pm4py.objects.dcr
from pm4py.objects.dcr.hierarchical.obj import HierarchicalDcrGraph
graph = HierarchicalDcrGraph()
graph.events.add("activity1")
graph.events.add("activity2")
graph.events.add("activity3")
graph.labels.add("A")
graph.labels.add("B")
graph.labels.add("C")
graph.label_map["activity1"] = "A"
graph.label_map["activity2"] = "B"
graph.label_map["activity3"] = "C"
graph.nestedgroups["group1"]={"activity1","activity2"}
graph.conditions["activity3"] = {"group1"}
graph.marking.included.add("activity1")
graph.marking.included.add("activity2")
graph.marking.included.add("activity3")


pm4py.view_dcr(graph)

# export to the xml file
