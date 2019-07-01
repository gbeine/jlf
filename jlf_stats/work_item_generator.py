
import logging

from datetime import date
from datetime import datetime

from jlf_stats.work_item import Work_Item
from jlf_stats.work_item_history import Work_Item_History

class Work_Item_Generator(object):

    def __init__(self, initial_state, reverse_history=False, ignore_blocker=True, until_date=None):
        self._initial_state = initial_state
        self._reverse_history = reverse_history
        self._ignore_blocker = ignore_blocker
        self._until_date = until_date


    def from_jira_issue(self, jira_issue):
        date_created = self._extract_date(jira_issue.fields.created)

        if jira_issue.changelog is not None:
            logging.debug("Changelog available for item {}".format(jira_issue.key))
            work_item_history = self._from_jira_history(jira_issue.changelog, date_created)

        work_item = Work_Item(jira_issue.key,
                              jira_issue.fields.summary,
                              jira_issue.fields.status.name,
                              jira_issue.fields.issuetype.name,
                              date_created,
                              work_item_history)
            
        return work_item


    def _from_jira_history(self, changelog, date_created):
        logging.debug("Changelog with {} entries".format(changelog.total))

        work_item_history = Work_Item_History(self._initial_state, date_created, self._ignore_blocker)
        
        if self._reverse_history:
            history_data = reversed(changelog.histories)
        else:
            history_data = changelog.histories

        for history in history_data:
            change_date = self._extract_date(history.created)
            for item in history.items:
                if item.field in ['status', 'Markiert']:
                    logging.debug("Field: {}".format(item.field))
                    work_item_history.add_change(change_date, item)

        work_item_history.finalize_history(self._until_date)
        
        return work_item_history


    def _extract_date(self, date_string):
        return datetime.strptime(date_string[:10], '%Y-%m-%d').date()
