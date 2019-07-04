"""
Wrapper around the JIRA API to allow us to categorize issues by
project/component/label etc and report on:

- Work in Progress
- Work completed - including Cycle Time
- Work history
- Cumulative Flow
- Throughput
- Rate at which types of work are created

Also abstracts away from batch searching and other implementation
details we don't want to present to the user.
"""

import jira.client
import sys

from datetime import date, datetime
import logging

from jlf_stats.jira_iterator import Jira_Iterator
from jlf_stats.exceptions import MissingConfigItem
import dateutil.parser


class Jira_Wrapper(object):
    """
    Wrapper around our JIRA instance
    """

    def __init__(self, source, work_item_generator):

        self._connect(source['server'], source['authentication'])
        self._work_item_generator = work_item_generator

        self.all_issues = None
        

    def work_items(self, work_items, filter=None):
        """
        All issues
        """
        if self.all_issues is None:
            self.all_issues = self._issues_from_jira(work_items, filter)

        return self.all_issues


    def totals(self):
        """
        What are current totals of work in our various states
        """

        # We can get this by doing a count of the last day of the CFD

        cfd = self.cfd()

        return None

###############################################################################
# Internal methods
###############################################################################

    def _connect(self, server, credentials):

        self._jira = None

        if 'username' in credentials and 'password' in credentials:
            self._jira = jira.client.JIRA({'server': server},
                                         basic_auth=(credentials['username'],
                                                     credentials['password']))
        elif ('access_token' in credentials and
              'access_token_secret' in credentials and
              'consumer_key' in credentials and
              'key_cert'):

            try:
                with open(credentials['key_cert'], 'r') as key_cert_file:
                    key_cert_data = key_cert_file.read()
            except IOError:
                raise MissingConfigItem('key_cert', "key_cert not found:{0}". format(credentials['key_cert']))

            self._jira = jira.client.JIRA({'server': server},
                                         oauth={'access_token': credentials['access_token'],
                                                'access_token_secret': credentials['access_token_secret'],
                                                'consumer_key': credentials['consumer_key'],
                                                'key_cert': key_cert_data})
        else:
            raise MissingConfigItem('credentials', "Authentication misconfigured")


    def _issues_from_jira(self, work_items, filter):
        """
        Get the actual issues from Jira itself via the Jira REST API
        """

        work_item_list = []
        
        iterator = Jira_Iterator(self._jira, filter)
            
        while iterator.has_more:
            issue_batch = iterator.next_batch()

            logging.info("Found {} items".format(issue_batch.total))

            for issue in issue_batch:
                item = self._work_item_generator.from_jira_issue(issue)
                work_item_list.append(item)
                work_items.add_work_item(item)

                sys.stdout.write('.')
                sys.stdout.flush()

        return work_item_list
