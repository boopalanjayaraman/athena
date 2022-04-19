import numpy as np
import logging
import pyTigerGraph as tg
import json
import re #regex
import datetime

class GraphConnector:
    """
    This class is to connect to TigerGraph and run the auto-generated query.
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
        self.graph_name = self.config['GraphSettings']['GraphName']
        self.secret = ''
        self.api_token = ''

        self.connection = tg.TigerGraphConnection(host=self.host_name, username=self.user_name, password=self.password, graphname=self.graph_name, gsqlVersion="3.5.0", useCert=True)

        self.logger.info("GraphConnector initialized.")


    def initialize_token(self):
        self.logger.info("GraphConnector connection initialized. Creating secret.")
        # For the below statements to execute the graph should be created and available
        # create the secret
        self.secret = self.config['GraphSettings']['Secret'] 
        if str.strip(self.secret) == '' or self.graph_auto_created == True:
            self.secret = self.connection.createSecret()

        self.api_token = self.config['GraphSettings']['ApiToken'] 
        if str.strip(self.api_token) == '' or self.graph_auto_created == True:
            self.api_token =  self.connection.getToken(self.secret, setToken=True)


    def use_graph(self):
        """
        This method executes use graph statement. Default graph name is fetched from the config
        """
        self.logger.info("use graph is being called.")
        full_query = str.format("USE GRAPH {}", self.graph_name)
        result = self.connection.gsql(full_query)

        result = str.lower(result)
        not_exists_message = str.lower(str.format("Graph '{}' does not exist.", self.graph_name))
        using_graph_message = str.lower("Using graph")

        if (not_exists_message in result) == True:
            # relying on string result is not a standard way of doing. Need to figure out another way from API if one exists.
            self.logger.info("Graph does not exist.")
        elif (using_graph_message in result) == False:
            # relying on string result is not a standard way of doing. Need to figure out another way from API if one exists.
            raise Exception("ERR: Use graph query execution failed.")
        else:
            self.logger.info("Graph exists. Using it.")
 

    def get_relationship_name(verb_token):
        """
        returns the relationship name from verb token
        """
        return "r_" + verb_token
        
    
    def run_gsql(self, gsql):
        """
        runs the gsql against the graph
        """
        self.logger.info("use graph is being called.")
        self.logger.info(str.format("INPUT GSQL: {}", gsql))

        result = self.connection.gsql(gsql)
        return result
