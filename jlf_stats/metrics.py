"""
Metrics
"""
from jlf_stats.jira_wrapper import JiraWrapper

import pandas as pd
import numpy as np
import math
import re
import os
import json
import logging

from jlf_stats.exceptions import MissingConfigItem

class Metrics(object):

    def __init__(self, config):

        self.source = None
        self.work_items = None
        self.states = []
        self.config = config

        m = re.match("^ENV\(([^\']+)\)", self.config['source']['authentication']['password'])
        if m is not None:
            self.config['source']['authentication']['password'] = os.environ.get(m.group(1), 'undefined')

        self.source = JiraWrapper(self.config)

        if 'throughput_dow' in config:
            self.throughput_dow = config['throughput_dow']
        else:
            self.throughput_dow = 4

        try:
            self.types = config['types']
            self.counts_towards_throughput = config['counts_towards_throughput']
        except KeyError as e:
            raise MissingConfigItem(e.message, "Missing Config Item:{0}".format(e.message))

        # Optional

        try:
            self.states = config['states']
            self.states.append(None)
        except KeyError:
            pass


    def history(self, from_date=None, until_date=None, types=None):

        if self.work_items is None:
            self.work_items = self.source.work_items()

        history = {}

        for work_item in self.work_items:

            if types is None:
                # HACK HACK HACK
                # Also need some consistency around thing_date and date_thing
                if isinstance(self.source, JiraWrapper):
                    history[work_item.id] = work_item.history
                else:
                    history[work_item.id] = history_from_state_transitions(work_item.date_created.date(), work_item.history, until_date)
            else:
                for type_grouping in types:
                    if work_item.type in self.types[type_grouping]: 
                        if isinstance(self.source, JiraWrapper):
                            history[work_item.id] = work_item.history
                        else:
                            history[work_item.id] = history_from_state_transitions(work_item.date_created.date(), work_item.history, until_date)

        if history is not None:
            df = pd.DataFrame(history)
            return df

        return None


    def save_work_items(self, filename=None):

        if filename is None:
            if 'name' in self.config['name']:
                filename = self.config['name'] + '.json'
            else:
                filename = 'local.json'

        if self.work_items is None:
            self.work_items = self.source.work_items()

        output = []

        for item in self.work_items:
            # This is so wrong.  We are decoding then encoding then decoding again...
            output.append(json.loads(item.to_JSON()))

        with open(filename, 'w') as outfile:
            json.dump(output, outfile, indent=4, sort_keys=True)
