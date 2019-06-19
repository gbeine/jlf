
import logging

from datetime import datetime
from jlf_stats.issue import Issue

def extract_date(date_string):
    return datetime.strptime(date_string[:10], '%Y-%m-%d').date()


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
            if item.field in ['status', 'Markiert']:
                logging.debug("Field: {}".format(item.field))
                issue.add_change(change_date, item)

    issue.finalize_history(until_date)
    
    return issue.history()
