
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


    def from_jira_history(self, changelog, created_date):
        logging.debug("Changelog with {} entries".format(changelog.total))

        if created_date is None:
            created_date = date(1970,1,1)

        if self._reverse_history:
            history_data = reversed(changelog.histories)
        else:
            history_data = changelog.histories

        issue = Issue(self._initial_state, created_date, self._ignore_blocker)

        for history in history_data:
            change_date = self._extract_date(history.created)
            for item in history.items:
                if item.field in ['status', 'Markiert']:
                    logging.debug("Field: {}".format(item.field))
                    issue.add_change(change_date, item)

        issue.finalize_history(self._until_date)

        return issue


    def _extract_date(self, date_string):
        return datetime.strptime(date_string[:10], '%Y-%m-%d').date()
