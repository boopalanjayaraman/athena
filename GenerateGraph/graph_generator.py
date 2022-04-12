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
        self.should_create_graph = (self.config['GraphSettings']['CreateGraph'] == 'True')

        self.connection = tg.TigerGraphConnection(host=self.host_name, username=self.user_name, password=self.password, graphname=self.graph_name, useCert=False)

        self.logger.info("GraphGenerator connection initialized. Creating secret.")
        # For the below statements to execute the graph should be created and available
        # create the secret
        secret = self.config['GraphSettings']['Secret'] #self.connection.createSecret()
        if str.strip(secret) == '':
            secret = self.connection.createSecret()

        token =  self.connection.getToken(secret, setToken=True)

        self.logger.info("GraphGenerator initialized. Created secrets and tokens.")

    def use_graph(self):
        """
        This method executes use graph statement. Default graph name is fetched from the config
        """
        self.logger.info("use graph is being called.")
        full_query = str.format("USE GRAPH {}", self.graph_name)
        result = self.connection.gsql(full_query)

        if ('does not exist.' in result) == True:
            # relying on string result is not a standard way of doing. Need to figure out another way from API if one exists.
            self.logger.info("Graph does not exist. Calling create graph.")
            self.create_graph()
        elif ('Using graph' in result) == False:
            # relying on string result is not a standard way of doing. Need to figure out another way from API if one exists.
            raise Exception("ERR: Use graph query execution failed.")
        else:
            self.logger.info("Graph exists.")

    def create_graph(self):
        """
        This method executes create graph statement, if the configuration is true. Default graph name is fetched from the config.
        """
        self.logger.info("create graph is being called.")
        full_query = str.format("CREATE GRAPH {}", self.graph_name)
        if self.should_create_graph:
            result = self.connection.gsql(full_query)
            success_message = str.format('The graph {} is created', self.graph_name)
            if (success_message in result) == False:
                raise Exception("ERR: Create graph query execution failed.")
            self.logger.info("create graph is completed.")
        else:
            self.logger.info("create graph is not executed because it is configured not to create.")
    
    def create_nodes_schema(self, node_infos):
        """
        This method creates the initial nodes (vertices) with the given list of node_infos
        """
        self.logger.info("create_initial_nodes is called.")

        existing_node_types = self.connection.getVertexTypes(force=True)

        query_list = []
        new_node_available = False

        for node_info in node_infos:
            #skip this if it already exists.
            if node_info in existing_node_types:
                continue
            query_list.append(str.format('CREATE VERTEX {}(PRIMARY_ID id STRING, name STRING) WITH STATS="OUTDEGREE_BY_EDGETYPE", PRIMARY_ID_AS_ATTRIBUTE="true"', node_info['name']))
            new_node_available = True

        full_query = "\n".join(query_list)
        full_query = "USE GLOBAL" + "\n" + full_query
        self.connection.gsql(full_query)

        if new_node_available:
            #adding the created nodes into the graph
            self.add_nodes_to_graph_schema(node_infos)


    def create_relationships_schema(self, relationship_infos):
        """
        This method creates the initial relationships (edges) with the given list of relationship_infos.
        NOTE that all nodes are created using wildcard option. 
        """
        self.logger.info("create_relationships is called.")

        existing_relationship_types = self.connection.getEdgeTypes(force=True)

        query_list = []
        new_relationship_available = False

        for relationship_info in relationship_infos:
            #skip this if it already exists.
            if relationship_info in existing_relationship_types:
                continue
            relationship_name = GraphGenerator.get_relationship_name(relationship_info['name'])
            query_list.append(str.format('CREATE DIRECTED EDGE {} (FROM *, TO *, label STRING, happened DATETIME, month UINT, year UINT) WITH REVERSE_EDGE="reverse_{}"', relationship_name, relationship_name))
            ## CAUTION: wildcard edges creation. Will only consider the vertex types at the time of execution. Future vertices are not considered. Create the master data vertices before this action, if any.
            ## CAUTION: 'r_' is prefixed with the edge name as in 'r_NAME' to avoid the names clashing with reserved keywords.
            new_relationship_available = True

        full_query = "\n".join(query_list)
        full_query = "USE GLOBAL" + "\n" + full_query
        self.connection.gsql(full_query)

        if new_relationship_available:
            #adding the created relationships into the graph
            self.add_relationships_to_graph_schema(relationship_infos)


    def add_nodes_to_graph_schema(self, node_infos):
        """
        This method ports all the nodes (vertexes) created using create_nodes method to a particular graph
        """
        self.logger.info("add_nodes_to_graph is called.")

        existing_node_types = self.connection.getVertexTypes(force=True)
        
        query_list = []
        for node_info in node_infos:
            #skip this if it already exists.
            if node_info in existing_node_types:
                continue
            query_list.append(str.format('ADD VERTEX {} TO GRAPH {};', node_info['name'], self.graph_name))

        add_nodes_query = "\n".join(query_list)
        add_nodes_query = """
        USE GLOBAL
        CREATE GLOBAL SCHEMA_CHANGE JOB add_vertices_to_"""+ self.graph_name +""" {
        """ + add_nodes_query + """
        }
        RUN GLOBAL SCHEMA_CHANGE JOB add_vertices_to_"""+ self.graph_name +"""
        """
        self.connection.gsql(add_nodes_query)


    def add_relationships_to_graph_schema(self, relationship_infos):
        """
        This method ports all the relationships (edges) created using create_relationships method to a particular graph
        """
        self.logger.info("add_relationships_to_graph is called.")

        query_list = []
        for relationship_info in relationship_infos:
            relationship_name = GraphGenerator.get_relationship_name(relationship_info['name'])
            query_list.append(str.format('ADD EDGE {} TO GRAPH {}; ADD EDGE reverse_{} TO GRAPH {};', relationship_name, self.graph_name, relationship_name, self.graph_name))

        add_relationships_query = "\n".join(query_list)
        add_relationships_query = """
        USE GLOBAL
        CREATE GLOBAL SCHEMA_CHANGE JOB add_edges_to_"""+ self.graph_name +""" {
        """ + add_relationships_query + """
        }
        RUN GLOBAL SCHEMA_CHANGE JOB add_edges_to_"""+ self.graph_name +"""
        """
        self.connection.gsql(add_relationships_query)


    def get_relationship_name(verb_token):
        """
        returns the relationship name from verb token
        """
        return "r_" + verb_token
        

    def add_node_to_graph(self, node_token, node_type):
        """
        This method will add new nodes to the graph
        if exists already, it will just return the id
        """
        existing_nodes = self.connection.getVertices(node_type, "", "name=" + node_token['token'])
        node_id = ""
        if len(existing_nodes) > 0:
            node_id = existing_nodes[0]['id']
        else:
            node_count = self.connection.getVertexCount("*").values() #cannot rely on this fully. If we do async methods / do inserts from multiple clients, this will run into concurrency issues 
            node_id = sum(node_count) + 1 #generated with count for now. TODO: How else to reliably generate this id?
            self.connection.upsertVertex(node_type, node_id, { "name": node_token['token']}) 

        return node_id

    def add_relationship_to_graph(self, from_node_type, from_node, relationship, to_node_type, to_node, attributes=None):
        """
        This method will add new relationships between from_node and to_node to the graph 
        """
        self.connection.upsertEdge(from_node_type, from_node, relationship, to_node_type, to_node, attributes)


    def drop_all(self):
        """
        WARNING: destroyer method. Should not be used unless you want to start again.
        clears all the schema.
        """
        self.logger.info("clearing off the schema (drop all).")
        self.connection.gsql('''
        USE GLOBAL
        DROP ALL
        ''')

    def setup_schema(self, node_infos, relationship_infos):
        """
        Sets up schema with Graph for given node_infos and relationship_infos
        """
        self.logger.info("setup_schema is called.")

        self.create_nodes_schema(node_infos)
        self.create_relationships_schema(relationship_infos)


