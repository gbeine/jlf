import unittest

from datetime import date
from pandas import Series
from pandas import to_datetime
from pandas.util.testing import assert_series_equal

from jlf_stats.work_item_history import Work_Item_History

class TestWorkItemHistory(unittest.TestCase):
    
    def test_init(self):
        work_item_history = Work_Item_History('Open', date(2018,1,1))
        self.assertIsInstance(work_item_history, Work_Item_History)


    def test_simple_state_changes_3days(self):
        work_item_history = Work_Item_History('Open', date(2018,1,1))
        self.assertIsInstance(work_item_history, Work_Item_History)
        change = self._create_change('status', 'New', 'Open')
        work_item_history.add_change(date(2018,1,2), change)
        change = self._create_change('status', 'Open', 'Closed')
        work_item_history.add_change(date(2018,1,3), change)
        self.assertEqual(work_item_history.total_days, 3)
        history = work_item_history.history
        expected = self._create_series(['Open', 'Open', 'Closed'], ['2018-01-01', '2018-01-02', '2018-01-03'])
        assert_series_equal(history, expected)


    def test_simple_state_changes_today_with_finalize(self):
        work_item_history = Work_Item_History('Open', date(2018,1,1))
        self.assertIsInstance(work_item_history, Work_Item_History)
        change = self._create_change('status', 'New', 'Open')
        work_item_history.add_change(date(2018,1,2), change)
        change = self._create_change('status', 'Open', 'Closed')
        work_item_history.add_change(date(2018,1,3), change)
        work_item_history.finalize_history(date.today())
        expected_days = date.today() - date(2018,1,1)
        self.assertEqual(work_item_history.total_days, expected_days.days)


    def test_state_changes_with_block(self):
        work_item_history = Work_Item_History('Open', date(2018,1,1), False)
        self.assertIsInstance(work_item_history, Work_Item_History)
        change = self._create_change('status', 'New', 'Open')
        work_item_history.add_change(date(2018,1,2), change)
        change = self._create_change('Markiert', '', 'Hindernis')
        work_item_history.add_change(date(2018,1,3), change)
        change = self._create_change('Markiert', 'Hindernis', '')
        work_item_history.add_change(date(2018,1,6), change)
        change = self._create_change('status', 'Open', 'Closed')
        work_item_history.add_change(date(2018,1,10), change)
        self.assertEqual(work_item_history.total_days, 10)
        history = work_item_history.history
        expected_states = ['Open', 'Open', 'Hindernis', 'Hindernis', 'Hindernis', 'Open', 'Open', 'Open', 'Open', 'Closed']
        expected_dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10']
        expected = self._create_series(expected_states, expected_dates)
        assert_series_equal(history, expected)

    def test_state_changes_with_block_moving(self):
        work_item_history = Work_Item_History('Open', date(2018,1,1), False)
        self.assertIsInstance(work_item_history, Work_Item_History)
        change = self._create_change('status', 'New', 'Open')
        work_item_history.add_change(date(2018,1,2), change)
        change = self._create_change('Markiert', '', 'Hindernis')
        work_item_history.add_change(date(2018,1,3), change)
        change = self._create_change('status', 'Open', 'In Progress')
        work_item_history.add_change(date(2018,1,5), change)
        change = self._create_change('Markiert', 'Hindernis', '')
        work_item_history.add_change(date(2018,1,7), change)
        change = self._create_change('status', 'In Progress', 'Closed')
        work_item_history.add_change(date(2018,1,10), change)
        self.assertEqual(work_item_history.total_days, 10)
        history = work_item_history.history
        expected_states = ['Open', 'Open', 'Hindernis', 'Hindernis', 'Hindernis', 'Hindernis', 'In Progress', 'In Progress', 'In Progress', 'Closed']
        expected_dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10']
        expected = self._create_series(expected_states, expected_dates)
        assert_series_equal(history, expected)


    def test_state_changes_ignore_block(self):
        work_item_history = Work_Item_History('Open', date(2018,1,1))
        self.assertIsInstance(work_item_history, Work_Item_History)
        change = self._create_change('status', 'New', 'Open')
        work_item_history.add_change(date(2018,1,2), change)
        change = self._create_change('Markiert', '', 'Hindernis')
        work_item_history.add_change(date(2018,1,3), change)
        change = self._create_change('Markiert', 'Hindernis', '')
        work_item_history.add_change(date(2018,1,6), change)
        change = self._create_change('status', 'Open', 'Closed')
        work_item_history.add_change(date(2018,1,10), change)
        self.assertEqual(work_item_history.total_days, 10)
        history = work_item_history.history
        expected_states = ['Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Closed']
        expected_dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10']
        expected = self._create_series(expected_states, expected_dates)
        assert_series_equal(history, expected)


    def _create_change(self, field, from_string, to_string):
        return type('Change', (object,), { "field": field, "fromString": from_string, "toString": to_string })


    def _create_series(self, states, dates):
        return Series(states, index=to_datetime(dates))
