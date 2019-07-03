
from datetime import datetime

from jlf_stats.work_item_generator import Work_Item_Generator
from jlf_stats.jira_wrapper import Jira_Wrapper

class Main(object):

    def __init__(self, config):
        self._reverse_history = False
        self._ignore_blocker = False
        self._initial_state = 'Open'
        self._until_date = None

        self._init_config(config)
        self._init_work_item_generator()
        self._init_jira_wrapper()


    @property
    def jira_wrapper(self):
        return self._jira_wrapper


    def _init_config(self, config):
        try:
            self._source = config['source']
            self._reverse_history = config['reverse_history']
            self._initial_state = config['initial_state']

            if 'until_date' in config:
                self._until_date = datetime.strptime(config['until_date'], '%Y-%m-%d').date()

        except KeyError as e:
            raise MissingConfigItem(e, "Missing Config Item:{0}".format(e))


    def _init_work_item_generator(self):
        self._work_item_generator = Work_Item_Generator(self._initial_state, self._reverse_history, self._ignore_blocker, self._until_date)


    def _init_jira_wrapper(self):
        if self._work_item_generator is None:
            self._init_work_item_generator()
        self._jira_wrapper = Jira_Wrapper(self._source, self._work_item_generator)