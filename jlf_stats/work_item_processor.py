
import logging
import pandas


class Work_Item_Processor(object):

    def __init__(self):
        logging.error("Init")
        self._work_items = []


    def add_work_item(self, work_item):
        # TODO: recalculations here, depending on config
        self._work_items.append(work_item)


    def history(self, from_date=None, until_date=None, types=None):

        history = {}

        for work_item in self._work_items:
            history[work_item.id] = work_item.history.history

        if history is not None:
            df = pandas.DataFrame(history)
            return df

        return None
