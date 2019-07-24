
import argparse

class Args(object):
    
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='Get forward looking metrics from JIRA')

        self._parser.add_argument('-n',
                        action="store",
                        dest="num_weeks",
                        type=int,
                        default=6)

        self._parser.add_argument('-c',
                        action="store",
                        dest="config_filename",
                        default='config.json')


    @property
    def args(self):
        return self._parser.parse_args()