import logging
import re #regex

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
        self.accepted_pattern = self.config['GraphSettings']['SentencePatternRegex'] #this is the acceptable pattern of sentences.

        self.logger.info("PatternFinder initialized.")

    def is_acceptable_pattern(self, entities, pos_tags):
        """
        orders the entities and pos_tags based on index and verifies them if they are in the acceptable patterns.
        Also returns the ordered list
        """
        all_applicable_tokens = []

        for item in entities:
            item['type'] = 'E'
            all_applicable_tokens.append(item)

        for item in pos_tags:
            if item['pos'] == 'VERB':
                item['type'] = 'V'
                all_applicable_tokens.append(item)
            elif item['pos'] == 'PROPN':
                item['type'] = 'P'
                #we need to ignore PROPN because it denotes "the who" part which we already get using BERT.
            elif item['pos'] == 'NOUN':
                item['type'] = 'N'
                all_applicable_tokens.append(item)
            else:
                item['type'] = 'na'
       
        #sort the tokens
        all_applicable_tokens.sort(key=lambda x: x['index'])
        current_pattern = "".join(list(map(lambda x: x['type'], all_applicable_tokens)))

        #regex on the current pattern with the acceptable pattern
        pattern_match = re.search(self.accepted_pattern, current_pattern)

        if pattern_match:
            return (True, all_applicable_tokens)
        else:
            return (False, all_applicable_tokens)

        


