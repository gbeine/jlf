import unittest

from datetime import date

from jlf_stats.issue import Issue
from jlf_stats.issue_generator import Issue_Generator

class TestIssueGenerator(unittest.TestCase):

    def test_init(self):
        issue_generator = Issue_Generator('Open')
        self.assertIsInstance(issue_generator, Issue_Generator)


    def test_simple_issue(self):
        issue_generator = Issue_Generator('Open')
        self.assertIsInstance(issue_generator, Issue_Generator)
        jira_issue = self._create_jira_issue()
        issue = issue_generator.from_jira_issue(jira_issue)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 3)
 

    def test_simple_issue_revert(self):
        issue_generator = Issue_Generator('Open', reverse_history=True)
        self.assertIsInstance(issue_generator, Issue_Generator)
        jira_issue = self._create_jira_issue()
        jira_issue.changelog.histories = list(reversed(jira_issue.changelog.histories))
        issue = issue_generator.from_jira_issue(jira_issue)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 3)


    def test_simple_issue_with_until_date(self):
        issue_generator = Issue_Generator('Open', until_date=date(2018,1,11))
        self.assertIsInstance(issue_generator, Issue_Generator)
        jira_issue = self._create_jira_issue()
        issue = issue_generator.from_jira_issue(jira_issue)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 10)


    def _create_jira_issue(self):
        return type('JiraIssue', (object,), {
            "key": "TEST-1",
            "fields": type('Field', (object,), { "created": "2018-01-01" }),
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

