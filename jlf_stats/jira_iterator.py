
import logging

class Jira_Iterator(object):
    """
    Iterator for a specific JIRA filter to fetch items in batches.

    Attributes
    ----------
    has_more : boolean
        True, if there are more items to be fetched from JIRA

    Methods
    -------
    next_batch() : list
        Fetch the next batch from JIRA.
    """

    def __init__(self, jira, filter, batch_size=100):
        """
        Parameters
        ----------
        jira : 
            The authenticated JIRA connection
        filter : str
            The filter to use for searching
        batch_size : int, optional
            The number of items per batch (default is 100)
        """

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
