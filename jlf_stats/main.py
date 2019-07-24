
from datetime import datetime

from jlf_stats.work_item_generator import Work_Item_Generator
from jlf_stats.work_item_processor import Work_Item_Processor
from jlf_stats.jira_wrapper import Jira_Wrapper

class Main(object):

    def __init__(self, config):
        self._reverse_history = False
        self._ignore_blocker = False
        self._initial_state = 'Open'
        self._until_date = None

        self._init_config(config)
        self._init_work_item_processor()
        self._init_work_item_generator()
        self._init_jira_wrapper()


    @property
    def jira_wrapper(self):
        return self._jira_wrapper


    @property
    def work_item_processor(self):
        return self._work_item_processor


    @property
    def publisher(self):
        return self._publisher


    def _init_config(self, config):
        try:
            self._source = config['source']

            if 'reverse_history' in config:
                self._reverse_history = config['reverse_history']
            else:
                self._reverse_history = False

            if 'ignore_blocker' in config:
                self._ignore_blocker = config['ignore_blocker']
            else:
                self._ignore_blocker = True

            if 'initial_state' in config:
                self._initial_state = config['initial_state']
            else:
                self._initial_state = u'Open'

            if 'until_date' in config:
                self._until_date = datetime.strptime(config['until_date'], '%Y-%m-%d').date()
            else:
                self._until_date = datetime.now().date()

        except KeyError as e:
            raise MissingConfigItem(e, "Missing Config Item:{0}".format(e))


    def _init_work_item_processor(self):
        self._work_item_processor = Work_Item_Processor()


    def _init_work_item_generator(self):
        self._work_item_generator = Work_Item_Generator(self._initial_state, self._reverse_history, self._ignore_blocker, self._until_date)


    def _init_jira_wrapper(self):
        if self._work_item_generator is None:
            self._init_work_item_generator()
        self._jira_wrapper = Jira_Wrapper(self._source, self._work_item_generator)
