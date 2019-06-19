import unittest

from datetime import date
from pandas import Series
from pandas import to_datetime
from pandas.util.testing import assert_series_equal

from jlf_stats.issue import Issue

class TestIssue(unittest.TestCase):
    
    def test_dummy(self):
        issue = Issue('Open', date(2018,1,1))
        self.assertIsInstance(issue, Issue)


    def test_simple_state_changes_3days(self):
        issue = Issue('Open', date(2018,1,1))
        change = self._create_change('status', 'New', 'Open')
        issue.add_change(date(2018,1,2), change)
        change = self._create_change('status', 'Open', 'Closed')
        issue.add_change(date(2018,1,3), change)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 0)
        history = issue.history()
        self.assertEqual(issue.total_days(), 3)
        expected = self._create_series(['Open', 'Open', 'Closed'], ['2018-01-01', '2018-01-02', '2018-01-03'])
        assert_series_equal(history, expected)


    def test_simple_state_changes_today_with_finalize(self):
        issue = Issue('Open', date(2018,1,1))
        change = self._create_change('status', 'New', 'Open')
        issue.add_change(date(2018,1,2), change)
        change = self._create_change('status', 'Open', 'Closed')
        issue.add_change(date(2018,1,3), change)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 0)
        issue.finalize_history(date.today())
        history = issue.history()
        expected_days = date.today() - date(2018,1,1)
        self.assertEqual(issue.total_days(), expected_days.days)


    def test_state_changes_with_block(self):
        issue = Issue('Open', date(2018,1,1), False)
        change = self._create_change('status', 'New', 'Open')
        issue.add_change(date(2018,1,2), change)
        change = self._create_change('Markiert', '', 'Hindernis')
        issue.add_change(date(2018,1,3), change)
        change = self._create_change('Markiert', 'Hindernis', '')
        issue.add_change(date(2018,1,6), change)
        change = self._create_change('status', 'Open', 'Closed')
        issue.add_change(date(2018,1,10), change)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 0)
        history = issue.history()
        self.assertEqual(issue.total_days(), 10)
        expected_states = ['Open', 'Open', 'Hindernis', 'Hindernis', 'Hindernis', 'Open', 'Open', 'Open', 'Open', 'Closed']
        expected_dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10']
        expected = self._create_series(expected_states, expected_dates)
        assert_series_equal(history, expected)

    def test_state_changes_with_block_moving(self):
        issue = Issue('Open', date(2018,1,1), False)
        change = self._create_change('status', 'New', 'Open')
        issue.add_change(date(2018,1,2), change)
        change = self._create_change('Markiert', '', 'Hindernis')
        issue.add_change(date(2018,1,3), change)
        change = self._create_change('status', 'Open', 'In Progress')
        issue.add_change(date(2018,1,5), change)
        change = self._create_change('Markiert', 'Hindernis', '')
        issue.add_change(date(2018,1,7), change)
        change = self._create_change('status', 'In Progress', 'Closed')
        issue.add_change(date(2018,1,10), change)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 0)
        history = issue.history()
        self.assertEqual(issue.total_days(), 10)
        expected_states = ['Open', 'Open', 'Hindernis', 'Hindernis', 'Hindernis', 'Hindernis', 'In Progress', 'In Progress', 'In Progress', 'Closed']
        expected_dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10']
        expected = self._create_series(expected_states, expected_dates)
        assert_series_equal(history, expected)


    def test_state_changes_ignore_block(self):
        issue = Issue('Open', date(2018,1,1))
        change = self._create_change('status', 'New', 'Open')
        issue.add_change(date(2018,1,2), change)
        change = self._create_change('Markiert', '', 'Hindernis')
        issue.add_change(date(2018,1,3), change)
        change = self._create_change('Markiert', 'Hindernis', '')
        issue.add_change(date(2018,1,6), change)
        change = self._create_change('status', 'Open', 'Closed')
        issue.add_change(date(2018,1,10), change)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 0)
        history = issue.history()
        self.assertEqual(issue.total_days(), 10)
        expected_states = ['Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Closed']
        expected_dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10']
        expected = self._create_series(expected_states, expected_dates)
        assert_series_equal(history, expected)


    def _create_change(self, field, from_string, to_string):
        return type('Dummy', (object,), { "field": field, "fromString": from_string, "toString": to_string })


    def _create_series(self, states, dates):
        return Series(states, index=to_datetime(dates))
