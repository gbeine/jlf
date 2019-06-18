
import logging
import pandas

from datetime import datetime
from datetime import timedelta

class Issue(object):

    def __init__(self, initial_state, created_date):
        self._current_state = initial_state
        self._last_state = None

        self._created_date = created_date
        self._state_change_date = None
        self._last_state_change_date = created_date

        self._time_in_states = []
        self._finalized = False

    def addChange(self, date, change):
        self._state_change_date = date
        days_in_state = self._state_change_date - self._last_state_change_date
        
        # only if not blocker!
        if self._current_state is None:
            self._current_state = change.fromString

        logging.debug("State {} for {} days".format(self._current_state, days_in_state.days))

        self._time_in_states.append({'state': self._current_state, 'days': days_in_state.days})

        # only if not blocker!
        self._last_state = self._current_state
        self._current_state = change.toString
        self._last_state_change_date = self._state_change_date
        logging.debug("State change to {} on {}".format(self._current_state, self._state_change_date))

    def finalizeHistory(self, date=None):
        if self._finalized:
            return

        final_state_days = 1
        if date is not None:
            final_date = datetime.combine(date, datetime.min.time())
            final_days = final_date - self._last_state_change_date
            final_state_days = final_days.days

        self._time_in_states.append({'state': self._current_state, 'days':  final_state_days})
        self._finalized = True

    def history(self):
        if not self._finalized:
            self.finalizeHistory()

        history = []
        total_days = 0

        for state_days in self._time_in_states:
            state = state_days['state']
            days = state_days['days']

            days_in_state = [state] * days

            history += days_in_state
            total_days += days

        dates = [self._created_date + timedelta(days=x) for x in range(0, total_days)]
        logging.debug("Issue exists for {} days".format(total_days))

        return pandas.Series(history, index=dates)
