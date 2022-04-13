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

    def already_handled_by_entities(self, noun_index, entity_index_pairs):
        """
        This method figures out if a noun token is already handled by entities tokens
        If so, it should be omitted
        For ex., Agilent technologies ENTITY & technologies NOUN based on their index values
        """
        for index_pair in entity_index_pairs:
            if noun_index >= index_pair['startIndex'] or noun_index <= index_pair['index']:
                return True
        #noun token not handled by entities already
        return False


    def is_acceptable_pattern(self, entities, pos_tags, domain_nouns_set):
        """
        orders the entities and pos_tags based on index and verifies them if they are in the acceptable patterns.
        Also returns the ordered list
        """
        all_applicable_tokens = []

        entity_index_pairs = []
        for item in entities:
            item['type'] = 'E'
            all_applicable_tokens.append(item)
            entity_index_pairs.append({'startIndex': item['startIndex'], 'index': item['index']})

        for item in pos_tags:
            if item['pos'] == 'VERB':
                item['type'] = 'V'
                all_applicable_tokens.append(item)
            elif item['pos'] == 'PROPN':
                item['type'] = 'P'
                #we need to ignore PROPN because it denotes "the who" part which we already get using BERT.
            elif item['pos'] == 'NOUN':
                item['type'] = 'N'

                if (self.already_handled_by_entities(item['index'], entity_index_pairs) == False) and (item['token'] in domain_nouns_set):
                    all_applicable_tokens.append(item)
            else:
                item['type'] = 'na'
       
        #sort the tokens
        all_applicable_tokens.sort(key=lambda x: x['index'])
        current_pattern = "".join(list(map(lambda x: x['type'], all_applicable_tokens)))

        #regex on the current pattern with the acceptable pattern
        pattern_match = re.match(self.accepted_pattern, current_pattern)

        self.logger.info(str.format("current pattern: {}.", current_pattern))

        if pattern_match != None:
            return (True, all_applicable_tokens)
        else:
            return (False, all_applicable_tokens)

        


