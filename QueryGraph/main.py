import pickle as pickle
from flask import Flask
from flask import request
import sys
import logging
from os import path
from graph_connector import GraphConnector
from gsql_converter import GsqlConverter
from parameter_tokenizer import ParameterTokenizer
from training_pipeline import TrainingPipeline
from pos_extractor import PosExtractor
from entity_extractor import EntityExtractor
from query_pipeline import QueryPipeline
from log_helper import logger
from config_helper import config


app = Flask(__name__)

query_pipeline = None


def init():
    print('hello world! Query service starting.')
    logger.info('##App Start: Module initializing.')
    logger.info('logger is working')
    logger.info('config is working. TestConfig: %s ', config['GeneralSettings']['TestConfig'])

    global query_pipeline

    if(query_pipeline == None):
        #prepare the extractors
        entity_extractor = EntityExtractor(config, logger)
        pos_extractor = PosExtractor(config, logger)

        #prepare the parameter tokenizer
        parameter_tokenizer = ParameterTokenizer(logger, config, entity_extractor, pos_extractor)

        # prepare the NLP model - Load the saved NLP to IL converter - seq2seq models
        data_file = config['InputDataSettings']['InputDataSetFile']
        data_file = path.join(path.dirname(path.abspath(__file__)), data_file)
        seq2seq_pipeline = TrainingPipeline(logger, config)
        seq2seq_pipeline.load_saved_models(data_file)

        #prepare the gsql converter 
        gsql_converter = GsqlConverter(logger, config)

        #prepare the graph connector 
        graph_connector = GraphConnector(config, logger)

        # prepare the query pipeline
        query_pipeline = QueryPipeline(logger, config, parameter_tokenizer, seq2seq_pipeline, gsql_converter, graph_connector)
        logger.info('##App Start: Initialized the query pipeline successfully.')

'''
query graph method
'''
@app.route("/queryGraphNLP")
def query_graph_nlp():
    
    query = request.args['q']
    logger.info('calling the query pipeline for the input NLP query.')
    result = query_pipeline.process_nlp_query(query)

    return result

'''
ping method
'''
@app.route("/")
def ping():
    return 'hello, query service working.'


if __name__ == '__main__':
    init()
    app.run()
    
