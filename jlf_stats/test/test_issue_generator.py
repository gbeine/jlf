import unittest

from datetime import date

from jlf_stats.issue import Issue
from jlf_stats.issue_generator import Issue_Generator

class TestIssueGenerator(unittest.TestCase):

    def test_init(self):
        issue_generator = Issue_Generator('Open')
        self.assertIsInstance(issue_generator, Issue_Generator)


    def test_simple_history(self):
        issue_generator = Issue_Generator('Open')
        self.assertIsInstance(issue_generator, Issue_Generator)
        changelog = self._create_changelog()
        issue = issue_generator.from_jira_history(changelog, date(2018,1,1))
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 3)
 

    def test_simple_history_revert(self):
        issue_generator = Issue_Generator('Open', reverse_history=True)
        self.assertIsInstance(issue_generator, Issue_Generator)
        changelog = self._create_changelog()
        changelog.histories = list(reversed(changelog.histories))
        issue = issue_generator.from_jira_history(changelog, date(2018,1,1))
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 3)


    def test_history_without_created_date(self):
        issue_generator = Issue_Generator('Open')
        self.assertIsInstance(issue_generator, Issue_Generator)
        changelog = self._create_changelog()
        issue = issue_generator.from_jira_history(changelog, None)
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.total_days(), 17535)


    def test_history_with_until_date(self):
        issue_generator = Issue_Generator('Open', until_date=date(2018,1,10))
        self.assertIsInstance(issue_generator, Issue_Generator)
        changelog = self._create_changelog()
        issue = issue_generator.from_jira_history(changelog, None)
        self.assertIsInstance(issue, Issue)
        expected_days = date(2018,1,10) - date(1970,1,1)
        self.assertEqual(issue.total_days(), expected_days.days)


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

