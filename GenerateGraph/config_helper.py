import configparser
from os import path

config_file_path = path.join(path.dirname(path.abspath(__file__)), 'configuration.ini')
#read configuration file
config = configparser.ConfigParser()
config.read(config_file_path)

def get_config():
    return config