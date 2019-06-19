
import logging

from pandas import Series
from pandas import to_datetime
from datetime import datetime
from datetime import timedelta

class Issue(object):

    def __init__(self, initial_state, date_created, ignore_blocker=True):
        self._ignore_blocker = ignore_blocker

        self._current_state = initial_state
        self._last_state = None

        if isinstance(date_created, datetime):
            date_created = date_created.date()

        self._date_created = date_created
        self._state_change_date = None
        self._last_state_change_date = date_created

        self._time_in_states = []
        self._history = []
        self._total_days = 0
        self._finalized = False
        self._is_blocked = False


    def add_change(self, change_date, change):

        if isinstance(change_date, datetime):
            change_date = change_date.date()
        
        if change.field == 'status':
            if self._is_blocked:
                self._last_state = change.toString
                logging.debug("State change to {} on {} while blocked".format(self._current_state, self._state_change_date))
            else:
                self._add_change(change_date, change)
                self._last_state = self._current_state
                self._current_state = change.toString
                logging.debug("State change to {} on {}".format(self._current_state, self._state_change_date))

        if not self._ignore_blocker and change.field in ['Markiert']:
            self._add_change(change_date, change)

            if len(change.toString) == 0:
                self._current_state = self._last_state
                self._is_blocked = False
            else:
                self._last_state = self._current_state
                self._current_state = change.toString
                self._is_blocked = True
            logging.debug("State change to {} on {}".format(self._current_state, self._state_change_date))


    def finalize_history(self, final_date=None):
        if self._finalized:
            return

        final_state_days = 1
        if final_date is not None:
            if isinstance(final_date, datetime):
                final_date = final_date.date()

            final_days = final_date - self._last_state_change_date
            final_state_days = final_days.days

        self._time_in_states.append({'state': self._current_state, 'days':  final_state_days})
        self._finalized = True


    def history(self):
        if not self._history:
            self._create_history()

        dates = [self._date_created + timedelta(days=x) for x in range(0, self._total_days)]

        return Series(self._history, index=to_datetime(dates))


    def total_days(self):
        if not self._history:
            self._create_history()

        return self._total_days


    def date_created(self):
        return self._date_created


    def _add_change(self, date, change):
        self._state_change_date = date
        days_in_state = self._state_change_date - self._last_state_change_date
        logging.debug("State {} for {} days".format(self._current_state, days_in_state.days))
        self._time_in_states.append({'state': self._current_state, 'days': days_in_state.days})
        self._last_state_change_date = self._state_change_date


    def _create_history(self):
        if not self._finalized:
            self.finalize_history()

        for state_days in self._time_in_states:
            state = state_days['state']
            days = state_days['days']

            days_in_state = [state] * days

            self._history += days_in_state
            self._total_days += days

        logging.debug("Issue exists for {} days".format(self._total_days))
