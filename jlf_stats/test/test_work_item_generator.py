import unittest

from datetime import date

from jlf_stats.work_item import Work_Item
from jlf_stats.work_item_generator import Work_Item_Generator

class TestWorkItemGenerator(unittest.TestCase):

    def test_init(self):
        work_item_generator = Work_Item_Generator('Open')
        self.assertIsInstance(work_item_generator, Work_Item_Generator)


    def test_simple_issue(self):
        work_item_generator = Work_Item_Generator('Open')
        self.assertIsInstance(work_item_generator, Work_Item_Generator)
        jira_issue = self._create_jira_issue()
        work_item = work_item_generator.from_jira_issue(jira_issue)
        self.assertIsInstance(work_item, Work_Item)
        self.assertEqual(work_item.history.total_days, 3)
 

    def test_simple_issue_revert(self):
        work_item_generator = Work_Item_Generator('Open', reverse_history=True)
        self.assertIsInstance(work_item_generator, Work_Item_Generator)
        jira_issue = self._create_jira_issue()
        jira_issue.changelog.histories = list(reversed(jira_issue.changelog.histories))
        work_item = work_item_generator.from_jira_issue(jira_issue)
        self.assertIsInstance(work_item, Work_Item)
        self.assertEqual(work_item.history.total_days, 3)


    def test_simple_issue_with_until_date(self):
        work_item_generator = Work_Item_Generator('Open', until_date=date(2018,1,11))
        self.assertIsInstance(work_item_generator, Work_Item_Generator)
        jira_issue = self._create_jira_issue()
        work_item = work_item_generator.from_jira_issue(jira_issue)
        self.assertIsInstance(work_item, Work_Item)
        self.assertEqual(work_item.history.total_days, 10)


    def _create_jira_issue(self):
        status = type('Status', (object,), { "name": "Open" })
        issuetype = type('IssueType', (object,), { "name": "Task" })
        return type('JiraIssue', (object,), {
            "key": "TEST-1",
            "fields": type('Field', (object,), { "created": "2018-01-01", "summary": "Summary Test 1", "status": status, "issuetype": issuetype }),
            "changelog": self._create_changelog()
             })


    def _create_changelog(self):
        # Remember: Every time a mock returns a mock a fairy dies
        histories = [
            type('History', (object,), {
                "created": "2018-01-01",
                "items": [
                    type('Change', (object,), { "field": 'status', "fromString": "Open", "toString": "In Progress" }),
                    type('Change', (object,), { "field": 'unknown', "fromString": "Me", "toString": "You" })
                ]}),
            type('History', (object,), {
                "created": "2018-01-03",
                "items": [
                    type('Change', (object,), { "field": 'status', "fromString": "In Progress", "toString": "Closed" })
                ]}) 
        ]
        return type('Changelog', (object,), { "histories": histories, "total": len(histories)})

