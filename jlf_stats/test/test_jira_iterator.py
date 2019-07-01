
import unittest

from unittest.mock import MagicMock
from unittest.mock import Mock

from jlf_stats.jira_iterator import Jira_Iterator

class TestJiraIterator(unittest.TestCase):
    
    def test_single_batch(self):
        iterator = Jira_Iterator(self._jira_single_batch(), None)
        self.assertTrue(iterator.has_more)
        iterator.next_batch()
        self.assertFalse(iterator.has_more)        

    def test_triple_batch(self):
        iterator = Jira_Iterator(self._jira_triple_batch(), None)
        self.assertTrue(iterator.has_more)
        iterator.next_batch()
        self.assertTrue(iterator.has_more)
        iterator.next_batch()
        self.assertTrue(iterator.has_more)
        iterator.next_batch()
        self.assertFalse(iterator.has_more)        

    def _jira_single_batch(self):
        attrs = {'total.return_value': 80}

        search_result = MagicMock(**attrs)
        search_result.__len__.return_value = 80

        attrs = {'search_issues.return_value': search_result}
        jira_mock = Mock(**attrs)
        
        return jira_mock

    def _jira_triple_batch(self):
        attrs = {'total.return_value': 260}

        search_result_one = MagicMock(**attrs)
        search_result_one.__len__.return_value = 100

        search_result_three = MagicMock(**attrs)
        search_result_three.__len__.return_value = 80

        attrs = {'search_issues.side_effect': [search_result_one, search_result_one, search_result_three]}
        jira_mock = Mock(**attrs)

        return jira_mock
