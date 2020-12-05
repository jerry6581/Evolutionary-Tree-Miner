import pm4py
import logging


# pm4py supports access and manipulation of event log data through the IEEE XES- and csv format.
class ImportData:

    def __init__(self, path):
        # import xes file
        self.logger = logging.getLogger(__name__)
        self.event_log = pm4py.read_xes(path)
        # import csv file
        # self.input_data = pd.read_csv(path)
        self.unique_events = set()
        self.trace_list = []

    def extract_traces_and_events(self):
        for case_index, case in enumerate(self.event_log):
            trace = ""
            self.logger.info("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
            for event_index, event in enumerate(case):
                self.logger.info("event index: %d  event activity: %s" % (event_index, event["concept:name"]))
                self.unique_events.add(event["concept:name"].replace(" ", "-"))
                trace += event["concept:name"]
            self.trace_list.append(trace)



