import sys
import logging
from domain_words_extractor import DomainWordsExtractor
from entity_extractor import EntityExtractor
from graph_generator import GraphGenerator
from input_data_handler import InputDataHandler
from pattern_finder import PatternFinder
from pos_extractor import PosExtractor
from log_helper import logger
from config_helper import config


def init():
    print('hello world!')
    logger.info('##App Start: GenerateGraph Module initializing.')
    logger.info('logger is working')
    logger.info('config is working. TestConfig: %s ', config['GeneralSettings']['TestConfig'])
 

def read_data():
    logger.info('read_data is being invoked.')

    entity_extractor = EntityExtractor(config=config, logger=logger)
    pos_extractor = PosExtractor(config=config, logger=logger)
    domain_words_extractor = DomainWordsExtractor(config=config, logger=logger)
    pattern_finder = PatternFinder(config=config, logger=logger)
    graph_generator = GraphGenerator(config=config, logger=logger)

    #initialize the input file processor
    input_data_handler = InputDataHandler(config=config, logger=logger,  entity_extractor=entity_extractor, pos_extractor=pos_extractor, domain_words_extractor=domain_words_extractor, pattern_finder=pattern_finder, graph_generator=graph_generator)
    logger.info('initialized all necessary instances.')
    
    #process the file
    logger.info('## starting to process the input data file.')
    input_data_handler.process_file()
    

if __name__ == "__main__":
    init()
    read_data()