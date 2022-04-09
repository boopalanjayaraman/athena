from datetime import datetime
import numpy as np
import pandas as pd
import logging

from GenerateGraph.domain_words_extractor import DomainWordsExtractor
from GenerateGraph.entity_extractor import EntityExtractor
from GenerateGraph.graph_generator import GraphGenerator
from GenerateGraph.pattern_finder import PatternFinder
from GenerateGraph.pos_extractor import PosExtractor

class MasterDataHandler : 
    """
    This class is to handle the master data input file and call the necessary downstream actions on it.
    Creates further vertexes based on the needs and definitions found in the master data meta data file.
    Also updates the attributes for the master data nodes
    """

    def __init__(self, config, logger, graph_generator: GraphGenerator) -> None:
        """
        constructor method. Config, Logger, Entity Extracor, Pos Extractor, and Domain Words Extractor instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.graph_generator = graph_generator
        self.nodes_list = ['Organization','Person','Object','Location']

        self.logger.info("MasterDataHandler initialized.")

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
        # TODO: here

        return None