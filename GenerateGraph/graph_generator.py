import numpy as np
import logging
import pyTigerGraph as tg
import json
import re #regex

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
        self.secret = ''
        self.api_token = ''

        self.connection = tg.TigerGraphConnection(host=self.host_name, username=self.user_name, password=self.password, graphname=self.graph_name, gsqlVersion="3.5.0", useCert=True)

        self.logger.info("GraphGenerator initialized.")


    def initialize_token(self):
        self.logger.info("GraphGenerator connection initialized. Creating secret.")
        # For the below statements to execute the graph should be created and available
        # create the secret
        self.secret = self.config['GraphSettings']['Secret'] 
        if str.strip(self.secret) == '':
            self.secret = self.connection.createSecret()

        self.api_token = self.config['GraphSettings']['ApiToken'] 
        if str.strip(self.api_token) == '':
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
            self.logger.info("Graph does not exist. Calling create graph.")
            self.create_graph()
        elif (using_graph_message in result) == False:
            # relying on string result is not a standard way of doing. Need to figure out another way from API if one exists.
            raise Exception("ERR: Use graph query execution failed.")
        else:
            self.logger.info("Graph exists. Using it.")


    def create_graph(self):
        """
        This method executes create graph statement, if the configuration is true. Default graph name is fetched from the config.
        """
        self.logger.info("create graph is being called.")
        full_query = str.format("CREATE GRAPH {} ()", self.graph_name)
        if self.should_create_graph:
            #execute create graph
            result = self.connection.gsql(full_query)

            success_message = str.lower(str.format('The graph {} is created', self.graph_name))
            result = str.lower(result)

            if (success_message in result) == False:
                raise Exception("ERR: Create graph query execution failed.")
            self.logger.info("create graph is completed.")
        else:
            self.logger.info("create graph is not executed because it is configured not to create.")
            raise Exception("ERR: Create graph is not executed because it is configured not to create.")
    

    def create_nodes_schema(self, node_infos):
        """
        This method creates the initial nodes (vertices) with the given list of node_infos
        """
        self.logger.info("create_nodes_schema is called.")
        self.logger.info("getting existing vertex types.")

        #existing_node_types = self.connection.getVertexTypes(force=True)
        existing_node_types = self.get_existing_vertex_types_gsql()
        existing_node_types = [str.lower(n) for n in existing_node_types]

        query_list = []
        new_node_available = False
        to_be_added = []

        for node_info in node_infos:
            #skip this if it already exists.
            if str.lower(node_info['name']) in existing_node_types:
                continue
            query_list.append(str.format('CREATE VERTEX {}(PRIMARY_ID id STRING, name STRING) WITH STATS="OUTDEGREE_BY_EDGETYPE", PRIMARY_ID_AS_ATTRIBUTE="true"', node_info['name']))
            new_node_available = True
            to_be_added.append(node_info)

        full_query = "\n".join(query_list)
        full_query = "USE GLOBAL" + "\n" + full_query
        self.logger.info("creating vertex types globally.")
        result = self.connection.gsql(full_query)

        self.logger.info(str.format("result: {}", result))

        if new_node_available:
            #adding the created nodes into the graph
            self.logger.info("adding new nodes to graph's schema.")
            self.add_nodes_to_graph_schema(to_be_added)


    def create_relationships_schema(self, relationship_infos):
        """
        This method creates the initial relationships (edges) with the given list of relationship_infos.
        NOTE that all nodes are created using wildcard option. 
        """
        self.logger.info("create_relationships_schema is called.")
        self.logger.info("getting existing edge types.")

        #existing_relationship_types = self.connection.getEdgeTypes(force=True)
        existing_relationship_types = self.get_existing_edges_types_gsql()
        existing_relationship_types = [str.lower(r) for r in existing_relationship_types]

        query_list = []
        new_relationship_available = False
        to_be_added = []

        for relationship_info in relationship_infos:
            #skip this if it already exists.
            relationship_name = GraphGenerator.get_relationship_name(relationship_info['name'])
            if str.lower(relationship_name) in existing_relationship_types:
                continue
            query_list.append(str.format('CREATE DIRECTED EDGE {} (FROM *, TO *, label STRING, happened DATETIME, month UINT, year UINT) WITH REVERSE_EDGE="reverse_{}"', relationship_name, relationship_name))
            ## CAUTION: wildcard edges creation. Will only consider the vertex types at the time of execution. Future vertices are not considered. Create the master data vertices before this action, if any.
            ## CAUTION: 'r_' is prefixed with the edge name as in 'r_NAME' to avoid the names clashing with reserved keywords.
            new_relationship_available = True
            to_be_added.append(relationship_info)

        full_query = "\n".join(query_list)
        full_query = "USE GLOBAL" + "\n" + full_query
        self.logger.info("creating relationship types globally.")
        result = self.connection.gsql(full_query)

        self.logger.info(str.format("result: {}", result))

        if new_relationship_available:
            #adding the created relationships into the graph
            self.logger.info("adding new relationships to graph's schema.")
            self.add_relationships_to_graph_schema(to_be_added)


    def add_nodes_to_graph_schema(self, node_infos):
        """
        This method ports all the nodes (vertexes) created using create_nodes method to a particular graph
        """
        self.logger.info("add_nodes_to_graph_schema is called.")

        query_list = []
        for node_info in node_infos:
            query_list.append(str.format('ADD VERTEX {} TO GRAPH {};', node_info['name'], self.graph_name))

        add_nodes_query = "\n".join(query_list)
        add_nodes_query = """
        USE GLOBAL
        CREATE GLOBAL SCHEMA_CHANGE JOB add_vertices_to_"""+ self.graph_name +""" {
        """ + add_nodes_query + """
        }
        RUN GLOBAL SCHEMA_CHANGE JOB add_vertices_to_"""+ self.graph_name +"""
        """
        result = self.connection.gsql(add_nodes_query)

        self.logger.info(str.format("result: {}", result))
        


    def get_existing_vertex_types_gsql(self):
        """
        This gets the list of existing vertices using GSQL and parses the output using regular expression
        """
        self.logger.info("get_existing_vertices_gsql is called.")

        query = "SHOW VERTEX **"

        existing_vertices_result = self.connection.gsql(query)

        self.logger.info(str.format("result: {}", existing_vertices_result))

        existing_vertices = re.findall("VERTEX (.+)\(.+\)", existing_vertices_result)
        return existing_vertices


    def get_existing_edges_types_gsql(self):
        """
        This gets the list of existing edges using GSQL and parses the output using regular expression
        """
        self.logger.info("get_existing_edges_gsql is called.")

        query = "SHOW EDGE **"

        existing_edges_result = self.connection.gsql(query)
        existing_edges = re.findall("DIRECTED EDGE (r_.+)\(.+\)", existing_edges_result)
        return existing_edges


    def add_relationships_to_graph_schema(self, relationship_infos):
        """
        This method ports all the relationships (edges) created using create_relationships method to a particular graph
        """
        self.logger.info("add_relationships_to_graph_schema is called.")

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
        result = self.connection.gsql(add_relationships_query)

        self.logger.info(str.format("result: {}", result))


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
        if(self.api_token == ''):
            self.initialize_token()

        existing_nodes = self.connection.getVertices(node_type, "", str.format('name="{}"', node_token['token']))
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
        if(self.api_token == ''):
            self.initialize_token()

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

        #check and use / create graph if necessary before creating the schema.
        self.use_graph()

        self.create_nodes_schema(node_infos)
        self.create_relationships_schema(relationship_infos)


