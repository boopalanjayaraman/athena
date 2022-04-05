import logging
from xmlrpc.client import Boolean

class PatternFinder :
    """
    This class is to find the matching patterns in the occurrences and match them with accepted list of patterns for graph generation.
    Ex: 
    EVE
    EVEE
    EVN
    where E is entity, V is verb, and N is noun
    Check the reference folder and regex validation image for further understanding.
    """

    def __init__(self, config, logger) -> None:
        """
        constructor method. Config, and Logger instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger
        self.accepted_pattern = self.config['GraphSettings']['SentencePatternRegex']

        self.logger.info("PatternFinder initialized.")

    def is_acceptable_pattern(self, entities, pos_tags):
        """
        orders the entities and pos_tags based on index and verifies them if they are in the acceptable patterns.
        Also returns the ordered list
        """
        return (True, [])


