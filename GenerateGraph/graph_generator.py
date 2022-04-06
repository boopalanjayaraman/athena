import numpy as np
import logging
import pyTigerGraph as tg
import json

class GraphGenerator:
    """
    This class is to connect to TigerGraph and create the necessary node or relationship, and check if one of them exists already.
    """

    def __init__(self, config, logger) -> None:
        """
        constructor method. Config and Logger instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.host_name = self.config['GraphSettings']['HostName']
        self.user_name = self.config['GraphSettings']['UserName']
        self.password = self.config['GraphSettings']['Password']

        self.logger.info("GraphGenerator initialized.")

    
    def create_node(self, node_info):
        return None

    def create_relationship(self, relationship_info):
        return None

    def check_node_exists(self, node_info):
        return None

    def check_relationship_exists(self, relationship_info):
        return None

    def add_to_graph(self, content):
        #handle all cases here
        # Entity --> B-ORG, I-ORG = Organization, B-PER, I-PER = Person, B-MISC, I-MISC = Object, B-LOC, I-LOC = Location
        # POS --> VERB = edge, NOUN = Object
        return None