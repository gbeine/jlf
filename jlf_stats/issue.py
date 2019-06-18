
import logging
import pandas

from datetime import datetime
from datetime import timedelta

class Issue(object):

    def __init__(self, initial_state, created_date, ignore_blocker=False):
        self._current_state = initial_state
        self._last_state = None

        self._created_date = created_date
        self._state_change_date = None
        self._last_state_change_date = created_date

        self._time_in_states = []
        self._finalized = False
        self._is_blocked = False
        
        self._ignore_blocker = ignore_blocker


    def add_change(self, date, change):
        
        if change.field == 'status':
            if self._is_blocked:
                self._last_state = change.toString
                logging.debug("State change to {} on {} while blocked".format(self._current_state, self._state_change_date))
            else:
                self._add_change(date, change)
                self._last_state = self._current_state
                self._current_state = change.toString
                logging.debug("State change to {} on {}".format(self._current_state, self._state_change_date))

        if not self._ignore_blocker and change.field in ['Markiert']:
            self._add_change(date, change)

            if len(change.toString) == 0:
                self._current_state = self._last_state
                self._is_blocked = False
            else:
                self._last_state = self._current_state
                self._current_state = change.toString
                self._is_blocked = True
            logging.debug("State change to {} on {}".format(self._current_state, self._state_change_date))


    def finalize_history(self, date=None):
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


    def _add_change(self, date, change):
        self._state_change_date = date
        days_in_state = self._state_change_date - self._last_state_change_date
        logging.debug("State {} for {} days".format(self._current_state, days_in_state.days))
        self._time_in_states.append({'state': self._current_state, 'days': days_in_state.days})
        self._last_state_change_date = self._state_change_date
