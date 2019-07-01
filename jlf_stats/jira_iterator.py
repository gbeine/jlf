
import logging

class Jira_Iterator(object):

    def __init__(self, jira, filter, batch_size=100):
        self._jira = jira
        self._filter = filter
        self._batch_size = batch_size
        
        self._position = 0
        self._has_more = True


    @property
    def has_more(self):
        return self._has_more


    def next_batch(self):
        jql = self._filter
        logging.debug(jql)
        
        batch =  self._jira.search_issues(jql,
                                          startAt=self._position,
                                          maxResults=self._batch_size,
                                          expand='changelog')

        logging.info("Found {} items".format(batch.total))

        if len(batch) < self._batch_size:
            self._has_more = False

        self._position += self._batch_size

        return batch
