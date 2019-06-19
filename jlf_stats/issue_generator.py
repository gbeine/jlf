
import logging

from datetime import date
from datetime import datetime

from jlf_stats.issue import Issue

class Issue_Generator(object):

    def __init__(self, initial_state, reverse_history=False, ignore_blocker=True, until_date=None):
        self._initial_state = initial_state
        self._reverse_history = reverse_history
        self._ignore_blocker = ignore_blocker
        self._until_date = until_date


    def from_jira_issue(self, jira_issue):
        date_created = self._extract_date(jira_issue.fields.created)

        logging.debug("Item {}, created at {}".format(jira_issue.key, date_created))

        issue = Issue(self._initial_state, date_created, self._ignore_blocker)

        if jira_issue.changelog is not None:
            logging.debug("Changelog available for item {}".format(jira_issue.key))
            self._from_jira_history(jira_issue.changelog, issue)
            
        return issue


    def _from_jira_history(self, changelog, issue):
        logging.debug("Changelog with {} entries".format(changelog.total))

        if self._reverse_history:
            history_data = reversed(changelog.histories)
        else:
            history_data = changelog.histories

        for history in history_data:
            change_date = self._extract_date(history.created)
            for item in history.items:
                if item.field in ['status', 'Markiert']:
                    logging.debug("Field: {}".format(item.field))
                    issue.add_change(change_date, item)

        issue.finalize_history(self._until_date)


    def _extract_date(self, date_string):
        return datetime.strptime(date_string[:10], '%Y-%m-%d').date()
