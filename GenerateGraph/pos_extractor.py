import numpy as np
import pandas as pd
import logging
import spacy

class PosExtractor : 

    def __init__(self, config, logger) -> None:
        self.config = config
        self.logger = logger

        self.nlp_pipeline = spacy.load("en_core_web_sm")

        self.logger.info("PosExtractor initialized.")

    def get_pos_sentence(self, input_content, should_log=False):
        
        posList = []

        nlp_doc = self.nlp_pipeline(input_content)
        for token in nlp_doc: 
            posList.append({ 'token' : token.text, 'pos' : token.pos_, 'lemma': token.lemma_, 'index': token.idx })

        if should_log:
            self.logger.info("posList : %s", posList)

        return posList



