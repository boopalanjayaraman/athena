import numpy as np
import pandas as pd
import logging
import spacy

class PosExtractor : 
    """This class is to extract POS tags (Parts of Speech) from a textual content using Spacy. This helps in identifying verbs for creating relationships in the graph."""

    def __init__(self, config, logger) -> None:
        """
        constructor method. Config and Logger instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.nlp_pipeline = spacy.load("en_core_web_sm")

        self.logger.info("PosExtractor initialized.")


    def get_pos_sentence(self, input_content, should_log=False):
        """
        returns the POS tags of a given sentence.
        output format: objects of {'token' : '', 'pos' : '', 'lemma': ''', 'index': 0}
        """
        posList = []

        nlp_doc = self.nlp_pipeline(input_content)
        for token in nlp_doc: 
            posList.append({ 'token' : token.text, 'pos' : token.pos_, 'lemma': token.lemma_, 'index': token.idx })

        return posList



