"""
Metrics
"""
import pandas as pd
import json

class Metrics(object):

    def __init__(self, config, jira_wrapper):

        self.work_items = None
        self.states = []
        self.config = config
        self.source = jira_wrapper


    def history(self, from_date=None, until_date=None, types=None):

        if self.work_items is None:
            self.work_items = self.source.work_items()

        history = {}

        for work_item in self.work_items:
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
