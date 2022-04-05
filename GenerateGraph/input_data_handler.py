import numpy as np
import pandas as pd
import logging

class InputDataHandler : 

    def __init__(self, config, logger, entity_extractor, pos_extractor, domain_words_extractor) -> None:
        self.config = config
        self.logger = logger

        self.entity_extractor = entity_extractor
        self.pos_extractor = pos_extractor
        self.domain_words_extractor = domain_words_extractor

        self.logger.info("InputDataHandler initialized.")

    
    def process_file(self, input_data_file=None):

        self.logger.info("InputDataHandler initialized.")