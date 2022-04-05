import numpy as np
import pandas as pd
import logging

class InputDataHandler : 
    """
    This class is to handle the input data file and call the necessary downstream actions on it.
    Extracts Entities on a given text, Extracts Parts-of-speech on the given text, and extracts domain words.
    Then compares them and forms the necessary relationships before calling the graph generation.
    """

    def __init__(self, config, logger, entity_extractor, pos_extractor, domain_words_extractor) -> None:
        """
        constructor method. Config, Logger, Entity Extracor, Pos Extractor, and Domain Words Extractor instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.entity_extractor = entity_extractor
        self.pos_extractor = pos_extractor
        self.domain_words_extractor = domain_words_extractor
        self.generate_domain_words = (self.config['InputDataSettings']['GenerateDomainWords'] == 'True')

        self.logger.info("InputDataHandler initialized.")

    
    def process_file(self, input_data_file_path=None, master_data_file_path = None):
        """
        Starts processing the input file and does the graph generation pipeline (entity extraction, pos extraction, relationship generation, domain words extraction and graph generation)
        master_data_file_path : is an optional file for graph creation
        """
        self.logger.info("process_file is called.")

        if input_data_file_path == None:
            input_data_file_path = self.config['InputDataSettings']['InputDataSetFile']

        if str.strip(input_data_file_path) == '':
            raise Exception("Input Data File Path is unavailable. Please pass the value as input or set the value in the configuration.")

        if master_data_file_path == None:
            master_data_file_path = self.config['InputDataSettings']['MasterDataFile']

        #find the master data's metadata file under a similar name but with a suffix of _metadata.csv
        masterdata_metadata_file_path = ''
        if str.strip(master_data_file_path) != '':
            masterdata_metadata_file_path = master_data_file_path.replace(master_data_file_path, '.csv', '_metadata.csv')

        #automatically extract the domain words and actions
        #read the file with pandas and loop through
            #extract the entities
            #extract the pos
            #order them by indexes and see if they match the pattern
            #match the nouns & verbs with the synonyms dictionary for relationships
            #if pattern is good, then create the graph - node, relationship (ignore if already exists)
            #create graph nodes for the master data
        

        

        
