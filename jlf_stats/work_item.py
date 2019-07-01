
import logging

from jlf_stats.work_item_history import Work_Item_History

class Work_Item(object):

    def __init__(self, id, title, state, type, date_created, history):
        logging.debug("Work item {}, created at {}".format(id, date_created))
        self._id = id
        self._title = title
        self._state = state
        self._type = type
        self._date_created = date_created
        self._history = history


    @property
    def history(self):
        return self._history

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def state(self):
        return self._state

    @property
    def type(self):
        return self._type

    @property
    def date_created(self):
        return self._date_created

    def detail(self):

        detail = {'id': self._id,
                  'title': self._title,
                  'state': self._state,
                  'type': self._type,
                  'date_created': self._date_created.replace(tzinfo=None)}  # HACK HACK HACK - for excel's benefit

        return detail
