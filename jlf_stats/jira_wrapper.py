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

from jlf_stats.issue_generator import Issue_Generator
from jlf_stats.exceptions import MissingConfigItem
from jlf_stats.work import WorkItem
import dateutil.parser


class JiraWrapper(object):
    """
    Wrapper around our JIRA instance
    """

    def __init__(self, config):

        authentication = None

        try:
            source = config['source']
        except KeyError as e:
            raise MissingConfigItem(e, "Missing Config Item:{0}".format(e))

        self.jira = None

        authentication = source['authentication']

        if 'username' in authentication and 'password' in authentication:
            self.jira = jira.client.JIRA({'server': source['server']},
                                         basic_auth=(authentication['username'],
                                                     authentication['password']))
        elif ('access_token' in authentication and
              'access_token_secret' in authentication and
              'consumer_key' in authentication and
              'key_cert'):

            try:
                with open(authentication['key_cert'], 'r') as key_cert_file:
                    key_cert_data = key_cert_file.read()
            except IOError:
                raise MissingConfigItem('key_cert', "key_cert not found:{0}". format(authentication['key_cert']))

            self.jira = jira.client.JIRA({'server': source['server']},
                                         oauth={'access_token': authentication['access_token'],
                                                'access_token_secret': authentication['access_token_secret'],
                                                'consumer_key': authentication['consumer_key'],
                                                'key_cert': key_cert_data})
        else:
            raise MissingConfigItem('authentication', "Authentication misconfigured")

        self.categories = None
        self.cycles = None
        self.types = None
        self.until_date = None

        if 'until_date' in config:
            self.until_date = datetime.strptime(config['until_date'], '%Y-%m-%d').date()

        self.reverse_history = config['reverse_history']
        self.initial_state = config['initial_state']
        self.ignore_blocker = False

        try:
            self.categories = config['categories']
            self.cycles = config['cycles']
        except KeyError as e:
            raise MissingConfigItem(e.message, "Missing Config Item:{0}".format(e.message))

        self.all_issues = None

    def work_items(self):
        """
        All issues
        """
        if self.all_issues is None:
            self.all_issues = self._issues_from_jira()

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

    def _issues_from_jira(self, filter=None):
        """
        Get the actual issues from Jira itself via the Jira REST API
        """

        batch_size = 100
        work_items = []
        
        for category in self.categories:

            logging.debug(category)
            n = 0
            while 1:

                jql = self.categories[category]
                if filter is not None:
                    jql = jql + filter

                logging.debug(jql)

                issue_batch = self.jira.search_issues(jql,
                                                      startAt=n,
                                                      maxResults=batch_size,
                                                      expand='changelog')

                logging.info("Found {} items".format(issue_batch.total))
                
                issue_generator = Issue_Generator(self.initial_state, self.reverse_history, self.ignore_blocker, self.until_date)

                for issue in issue_batch:

                    issue.category = category
                    issue_history = None
                    cycles = {}
                    state_transitions = []

                    item = issue_generator.from_jira_issue(issue)

                    work_items.append(WorkItem(id=issue.key,
                                               title=issue.fields.summary,
                                               state=issue.fields.status.name,
                                               type=issue.fields.issuetype.name,
                                               history=item.history(),
                                               state_transitions=state_transitions,
                                               date_created=item.date_created(),
                                               cycles=cycles,
                                               category=category))

                if len(issue_batch) < batch_size:
                    break
                n += batch_size
                sys.stdout.write('.')
                sys.stdout.flush()

        return work_items
