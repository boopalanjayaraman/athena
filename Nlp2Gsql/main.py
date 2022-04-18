import sys
import logging
from training_pipeline import TrainingPipeline
from log_helper import logger
from config_helper import config
import numpy as np
import pandas as pd


def init():
    print('hello world! NLP 2 GSQL intermediary Language starting.')
    logger.info('##App Start: Module initializing.')
    logger.info('logger is working')
    logger.info('config is working. TestConfig: %s ', config['GeneralSettings']['TestConfig'])
 

def train_model_seq2seq():
    logger.info('train_model_seq2seq is being invoked.')

    data_file = config['InputDataSettings']['InputDataSetFile']

    logger.info('creating a new training pipeline for seq2seq model.')
    training_pipeline = TrainingPipeline(logger, config)
    training_pipeline.start_training(data_file)
    
    logger.info('loading the saved models')
    training_pipeline.load_saved_models(data_file)

    logger.info('evaluating sample sentences')

    sample_sentences = ["who all did {VERB} {ORGANIZATION}",
    "who the did {VERB} {ORGANIZATION}", #changing the sentence framing a little
    "what the hell happen with {ORGANIZATION}", 
    "how {PERSON 1} connected  {PERSON 2}",
    "is the person {PERSON 1} related to the person {PERSON 2}"]

    for sentence in sample_sentences:
        output_sentence = training_pipeline.evaluate_saved_model(sentence)
        print('input sentence:', sentence)
        print('output sentence:', output_sentence)

    logger.info('## processing input data file is finished.')
    

if __name__ == "__main__":
    init()
    train_model_seq2seq()
    