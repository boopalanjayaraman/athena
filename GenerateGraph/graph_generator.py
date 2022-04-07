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
        self.graph_name = self.config['GraphSettings']['GraphName']

        self.connection = tg.TigerGraphConnection(self.host_name, self.graph_name, self.user_name, self.password)

        self.logger.info("GraphGenerator initialized.")

    
    def create_nodes(self, node_infos):
        """
        This method creates the initial nodes (vertices) with the given list of node_infos
        """
        self.logger.info("create_initial_nodes is called.")

        query_list = []
        for node_info in node_infos:
            query_list.append(str.format('CREATE VERTEX {}(PRIMARY_ID id STRING, name STRING) WITH STATS="OUTDEGREE_BY_EDGETYPE", PRIMARY_ID_AS_ATTRIBUTE="true"', node_info['name']))

        full_query = "\n".join(query_list)
        self.connection.gsql(full_query)


    def create_relationships(self, relationship_infos):
        """
        This method creates the initial relationships (edges) with the given list of relationship_infos.
        NOTE that all nodes are created using wildcard option. 
        """
        self.logger.info("create_relationships is called.")
        query_list = []
        for relationship_info in relationship_infos:
            query_list.append(str.format('CREATE DIRECTED EDGE r_{} (FROM *, TO *, label STRING, happened DATETIME, month UINT, year UINT) WITH REVERSE_EDGE="reverse_r_{}"', relationship_info['name'], relationship_info['name']))
            ## CAUTION: wildcard edges creation. Will only consider the vertex types at the time of execution. Future vertices are not considered. Create the master data vertices before this action, if any.

            ## CAUTION: 'r_' is prefixed with the edge name as in 'r_NAME' to avoid the names clashing with reserved keywords.

        full_query = "\n".join(query_list)
        self.connection.gsql(full_query)
        return None

    def add_to_graph(self, file_name):
        #handle all cases here
        # Entity --> B-ORG, I-ORG = Organization, B-PER, I-PER = Person, B-MISC, I-MISC = Object, B-LOC, I-LOC = Location
        # POS --> VERB = edge, NOUN = Object
        return None

    def setup_schema(self, node_infos, relationship_infos):
        """
        Sets up schema with Graph for given node_infos and relationship_infos
        """
        self.logger.info("setup_schema is called.")
        self.logger.info("clearing off the schema (drop all).")
        self.connection.gsql('''
        USE GLOBAL
        DROP ALL
        ''')

        self.create_nodes(node_infos)
        self.create_relationships(relationship_infos)


