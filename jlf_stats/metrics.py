"""
Metrics
"""
import pandas as pd
import numpy as np
import math
import re
import os
import json
import logging
from datetime import datetime

from jlf_stats.exceptions import MissingConfigItem

class Metrics(object):

    def __init__(self, config, jira_wrapper):

        self.work_items = None
        self.states = []
        self.config = config
        self.source = jira_wrapper

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
                history[work_item.id] = work_item.history.history
            else:
                for type_grouping in types:
                    if work_item.type in self.types[type_grouping]: 
                        history[work_item.id] = work_item.history.history

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

        # for item in self.work_items:
        #     # This is so wrong.  We are decoding then encoding then decoding again...
        #     output.append(json.loads(item.to_JSON()))

        # with open(filename, 'w') as outfile:
        #     json.dump(output, outfile, indent=4, sort_keys=True)
