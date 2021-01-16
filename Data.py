import pm4py
import logging
import string
import pandas as pd


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
        self.event_map = {}

    def extract_traces_and_events(self):
        for case_index, case in enumerate(self.event_log):
            # trace = ""
            self.logger.info("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
            for event_index, event in enumerate(case):
                self.logger.info("event index: %d  event activity: %s" % (event_index, event["concept:name"]))
                self.unique_events.add(event["concept:name"])
                # trace += event["concept:name"]
            # self.trace_list.append(trace)

    def change_event_names(self):
        # if len(list(self.unique_events)[0]) != 1:
        i = 0
        for event in self.unique_events:
            self.event_map[event] = string.ascii_lowercase[i]
            i += 1
        self.unique_events = set(self.event_map.values())
        for case_index, case in enumerate(self.event_log):
            trace = ""
            for event_index, event in enumerate(case):
                logging.info(f"Replace {event['concept:name']} into {self.event_map[event['concept:name']]}")
                # event["concept:name"] = self.event_map[event["concept:name"]]
                trace += event["concept:name"]
            self.trace_list.append(trace)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%I:%M:%S', level=logging.INFO)
    import_data = ImportData("Artificial - Loan Process.xes")
    import_data.extract_traces_and_events()
    # logging.info(import_data.event_log)
    # logging.info(import_data.unique_events)
    # logging.info(import_data.trace_list)
    import_data.change_event_names()
    logging.info(import_data.event_map)
    # logging.info(import_data.event_log)
    logging.info(import_data.unique_events)
    logging.info(import_data.trace_list)
