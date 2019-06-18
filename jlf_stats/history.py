from datetime import date, datetime, timedelta
import pandas as pd
import logging

def extract_date(created):
    return datetime.strptime(created[:10], '%Y-%m-%d').date()


def time_in_states(histories, reverse_history, initial_state, from_date=None, until_date=None):
    """
    How long did an issue spend in each state in its history.

    For the first state it was in count 'from' the start of the period we
    are interested in, typically when the issue was created

    For the last state it was in count from the time the state was entered
    until the date specified in 'until' - typically today's date
    """

    time_in_states = []

    current_state = initial_state

    if from_date is None:
        from_date = date(1970, 1, 1)

    if hasattr(from_date, 'date'):
        prev_state_change_date = from_date.date()
    else:
        prev_state_change_date = from_date

    if reverse_history:
        history_data = reversed(histories)
    else:
        history_data = histories

    for history in history_data:
        for item in history.items:
            if item.field == 'status':
                state_change_date = extract_date(history.created)

                days_in_state = state_change_date - prev_state_change_date

                if current_state is None:
                    current_state = item.fromString

                logging.debug("State {} for {} days".format(current_state, days_in_state.days))

                time_in_states.append({'state': current_state,
                                       'days': days_in_state.days})

                current_state = item.toString
                prev_state_change_date = state_change_date
                logging.debug("State change to {} on {}".format(current_state, state_change_date))

    if until_date is not None:
        final_state_days = until_date - prev_state_change_date

        time_in_states.append({'state': current_state,
                               'days':  final_state_days.days})
    else:
        time_in_states.append({'state': current_state,
                               'days':  1})

    return time_in_states


def history_from_jira_changelog(changelog, reverse_history, initial_state, created_date, until_date=None):

    logging.debug("Changelog with {} entries".format(changelog.total))
    issue_history = time_in_states(changelog.histories, reverse_history, initial_state, from_date=created_date, until_date=until_date)

    issue_day_history = []
    history = None
    total_days = 0

    for state_days in issue_history:

        state = state_days['state']
        days = state_days['days']

        days_in_state = [state] * days

        issue_day_history += days_in_state
        total_days += days

    dates = [created_date + timedelta(days=x) for x in range(0, total_days)]    
    logging.debug("Issue exists for {} days".format(len(dates)))
 
    try:
        history = pd.Series(issue_day_history, index=dates)
    except (AssertionError, ValueError) as e:
        print(dates)
        print(issue_day_history)
        print(e)
        exit(1)

    return history
