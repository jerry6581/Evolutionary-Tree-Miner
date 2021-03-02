import logging
import os
import string

import pandas as pd
import pm4py


class ImportData:
    def __init__(self, path):
        self.logger = logging.getLogger(__name__)
        _, self.file_extension = os.path.splitext(path)
        if self.file_extension == ".xes":
            # import xes file
            self.event_log = pm4py.read_xes(path)
        elif self.file_extension == ".csv":
            # import csv file
            self.input_data = pd.read_csv(path)
        else:
            self.logger.error("Wrong file format! Please pass correct one.")
            exit(1)
        # set of unique events existing in event log
        self.unique_events = []
        # list of traces existing in event log
        self.trace_list = []
        # map of letters and corresponding event names
        self.event_map = {}
        self.extract_events()
        self.create_trace_list()

    def extract_events(self):
        if self.file_extension == ".xes":
            for case_index, case in enumerate(self.event_log):
                for event_index, event in enumerate(case):
                    if not event["concept:name"] in self.unique_events:
                        self.unique_events.append(event["concept:name"])
        elif self.file_extension == ".csv":
            self.unique_events = self.input_data["event"].unique()

    def create_trace_list(self):
        i = 0
        for event in self.unique_events:
            self.event_map[event] = string.ascii_lowercase[i]
            i += 1
        self.unique_events = set(self.event_map.values())
        if self.file_extension == ".xes":
            for case_index, case in enumerate(self.event_log):
                trace = ""
                for event_index, event in enumerate(case):
                    event["concept:name"] = self.event_map[event["concept:name"]]
                    trace += event["concept:name"]
                self.trace_list.append(trace)
        elif self.file_extension == ".csv":
            for key, value in self.event_map.items():
                self.input_data.event.replace(key, value, inplace=True)
            groupbyid_input_data = self.input_data.groupby(["case"]).sum()
            self.trace_list = list(groupbyid_input_data["event"])

