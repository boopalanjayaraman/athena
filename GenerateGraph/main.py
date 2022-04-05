import sys
import logging
from log_helper import logger
from config_helper import config
import entity_extractor

def init():
    print('hello world!')
    logger.info('logger is working')
    logger.info('config is working. TestConfig: %s ', config['GeneralSettings']['TestConfig'])

def read_data():
    logger.info('entity_extractor is being invoked.')
    

if __name__ == "__main__":
    init()
    read_data()