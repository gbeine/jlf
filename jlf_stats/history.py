
import logging

from datetime import datetime
from jlf_stats.issue import Issue

def extract_date(created):
    date = datetime.strptime(created[:10], '%Y-%m-%d').date()
    return datetime.combine(date, datetime.min.time())


def history_from_jira_changelog(changelog, reverse_history, initial_state, created_date, until_date=None):

    logging.debug("Changelog with {} entries".format(changelog.total))
    
    if created_date is None:
        created_date = extract_date("1970-01-01")

    histories = changelog.histories

    if reverse_history:
        history_data = reversed(histories)
    else:
        history_data = histories

    issue = Issue(initial_state, created_date)

    for history in history_data:
        change_date = extract_date(history.created)
        for item in history.items:
            if item.field == 'status' or item.field == 'Markiert':
                logging.error("Field: {}".format(item.field))
            if item.field == 'status':
                issue.addChange(change_date, item)

    issue.finalizeHistory(until_date)
    
    return issue.history()
