import numpy as np
import pandas as pd
import logging

from GenerateGraph.domain_words_extractor import DomainWordsExtractor
from GenerateGraph.entity_extractor import EntityExtractor
from GenerateGraph.graph_generator import GraphGenerator
from GenerateGraph.pattern_finder import PatternFinder
from GenerateGraph.pos_extractor import PosExtractor

class InputDataHandler : 
    """
    This class is to handle the input data file and call the necessary downstream actions on it.
    Extracts Entities on a given text, Extracts Parts-of-speech on the given text, and extracts domain words.
    Then compares them and forms the necessary relationships before calling the graph generation.
    """

    def __init__(self, config, logger, entity_extractor : EntityExtractor, pos_extractor : PosExtractor, domain_words_extractor: DomainWordsExtractor, pattern_finder: PatternFinder, graph_generator: GraphGenerator) -> None:
        """
        constructor method. Config, Logger, Entity Extracor, Pos Extractor, and Domain Words Extractor instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.entity_extractor = entity_extractor
        self.pos_extractor = pos_extractor
        self.domain_words_extractor = domain_words_extractor
        self.generate_domain_words = (self.config['InputDataSettings']['GenerateDomainWords'] == 'True')
        self.pattern_finder = pattern_finder
        self.graph_generator = graph_generator

        self.logger.info("InputDataHandler initialized.")

    def process_master_data_file(self, master_data_file_path=None):
        """
        Starts processing the input file and does the graph generation pipeline (entity extraction, pos extraction, relationship generation, domain words extraction and graph generation)
        master_data_file_path : is an optional file for graph creation
        """
        self.logger.info("process_master_data_file is called.")
        if master_data_file_path == None:
            master_data_file_path = self.config['InputDataSettings']['MasterDataFile']

        if str.strip(master_data_file_path) == '':
            raise Exception("Input Master Data File Path is unavailable. Please pass the value as input or set the value in the configuration.")

        #find the master data's metadata file under a similar name but with a suffix of _metadata.csv
        masterdata_metadata_file_path = ''
        if str.strip(master_data_file_path) != '':
            masterdata_metadata_file_path = master_data_file_path.replace(master_data_file_path, '.csv', '_metadata.csv')

        #create graph nodes for the master data

        return None

    
    def process_file(self, input_data_file_path=None):
        """
        Starts processing the input file and does the graph generation pipeline (entity extraction, pos extraction, relationship generation, domain words extraction and graph generation)
        master_data_file_path : is an optional file for graph creation
        """
        self.logger.info("process_file is called.")

        if input_data_file_path == None:
            input_data_file_path = self.config['InputDataSettings']['InputDataSetFile']

        if str.strip(input_data_file_path) == '':
            raise Exception("Input Data File Path is unavailable. Please pass the value as input or set the value in the configuration.")

        #automatically extract the domain words and actions
        domain_words_dict = self.domain_words_extractor.extract_domain_words(input_data_file_path, False, True)
        self.logger.info("finished extracting domain words.")

        #read the file with pandas and loop through
        df = pd.read_csv(input_data_file_path)
        for index, row in df.iterrows():
            content = row[self.content_title]

            #extract the entities
            entities = self.entity_extractor.get_entities_bert(content)

            #extract the pos
            pos_tags = self.pos_extractor.get_pos_sentence(content)

            #order them by indexes and see if they match the pattern
            is_valid, ordered_word_list = self.pattern_finder.is_acceptable_pattern(entities, pos_tags)

            if is_valid == False:
                continue

            #match the nouns & verbs with the synonyms dictionary for relationships
            ##### NOT DONE FOR NOW ####
            
            #if pattern is good, then create the graph - node, relationship (ignore if already exists)



        

        
