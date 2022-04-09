from datetime import datetime
import numpy as np
import pandas as pd
import logging

from GenerateGraph.domain_words_extractor import DomainWordsExtractor
from GenerateGraph.entity_extractor import EntityExtractor
from GenerateGraph.graph_generator import GraphGenerator
from GenerateGraph.pattern_finder import PatternFinder
from GenerateGraph.pos_extractor import PosExtractor

class InputDataHandler : 
    """
    This class is to handle the input data file and call the necessary downstream actions on it.
    Extracts Entities on a given text, Extracts Parts-of-speech on the given text, and extracts domain words.
    Then compares them and forms the necessary relationships before calling the graph generation.
    """

    def __init__(self, config, logger, entity_extractor : EntityExtractor, pos_extractor : PosExtractor, domain_words_extractor: DomainWordsExtractor, pattern_finder: PatternFinder, graph_generator: GraphGenerator) -> None:
        """
        constructor method. Config, Logger, Entity Extracor, Pos Extractor, and Domain Words Extractor instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.entity_extractor = entity_extractor
        self.pos_extractor = pos_extractor
        self.domain_words_extractor = domain_words_extractor
        self.generate_domain_words = (self.config['InputDataSettings']['GenerateDomainWords'] == 'True')
        self.pattern_finder = pattern_finder
        self.graph_generator = graph_generator
        self.nodes_list = ['Organization','Person','Object','Location']
        self.domain_verbs_set = set()
        self.domain_nouns_set = set()
        self.content_title = config['InputDataSettings']['ContentTitle']
        self.date_title = config['InputDataSettings']['DateTitle']


        self.logger.info("InputDataHandler initialized.")

    def process_master_data_file(self, master_data_file_path=None):
        """
        Starts processing the input file and does the graph generation pipeline (entity extraction, pos extraction, relationship generation, domain words extraction and graph generation)
        master_data_file_path : is an optional file for graph creation
        """
        self.logger.info("process_master_data_file is called.")
        if master_data_file_path == None:
            master_data_file_path = self.config['InputDataSettings']['MasterDataFile']

        if str.strip(master_data_file_path) == '':
            raise Exception("Input Master Data File Path is unavailable. Please pass the value as input or set the value in the configuration.")

        #find the master data's metadata file under a similar name but with a suffix of _metadata.csv
        masterdata_metadata_file_path = ''
        if str.strip(master_data_file_path) != '':
            masterdata_metadata_file_path = master_data_file_path.replace(master_data_file_path, '.csv', '_metadata.csv')

        #create graph nodes for the master data

        return None

    
    def process_file(self, input_data_file_path=None):
        """
        Starts processing the input file and does the graph generation pipeline (entity extraction, pos extraction, relationship generation, domain words extraction and graph generation)
        master_data_file_path : is an optional file for graph creation
        """
        self.logger.info("process_file is called.")

        if input_data_file_path == None:
            input_data_file_path = self.config['InputDataSettings']['InputDataSetFile']

        if str.strip(input_data_file_path) == '':
            raise Exception("Input Data File Path is unavailable. Please pass the value as input or set the value in the configuration.")

        #automatically extract the domain words and actions
        domain_words_dict = self.domain_words_extractor.extract_domain_words(input_data_file_path, False, True)
        self.logger.info("finished extracting domain words.")
        #converting the list to a set for better performance while checking.
        self.domain_verbs_set = set(domain_words_dict['VerbsList'])
        self.domain_nouns_set = set(domain_words_dict['NounsList'])

        #set up schema for graph here
        self.setup_schema(domain_words_dict)


        #read the file with pandas and loop through
        df = pd.read_csv(input_data_file_path)
        for index, row in df.iterrows():
            content = row[self.content_title]
            date = row[self.date_title]
            #extract the entities
            entities = self.entity_extractor.get_entities_bert(content)

            #extract the pos
            pos_tags = self.pos_extractor.get_pos_sentence(content)

            #order them by indexes and see if they match the pattern
            #also get the relevant words only as part of this
            is_valid, ordered_word_list = self.pattern_finder.is_acceptable_pattern(entities, pos_tags)

            if is_valid == False:
                continue

            #match the nouns & verbs with the synonyms dictionary for relationships
            ##### NOT DONE FOR NOW ####
            
            #if pattern is good, then create the graph - node, relationship (ignore if already exists)
            #create the entity, verb, noun connections in files
            self.process_tokens_with_graph(ordered_word_list, date)
            
    def process_tokens_with_graph(self, ordered_word_list, date):
        """
        Splits the ordered word list along with their types (E,V,N), checks them and creates them in the graph
        WORDS ONLY IN THE DOMAIN DICTIONARY will be considered for creation.
        """
        # get the verb, check against domain dictionary, and if exists, get its relationship name.
        # if the verb does not exist in the dictionary, continue.
        # get the entity / noun BEFORE the verb, get the entity type, get the id if already exists, or add this entity and get the id.
        # get the entity(s) / noun(s) AFTER the verb, get the entity type, get the id if already exists, or add this entity and get the id.
        # add the relationship between the first and the latter ones. 
        # PROS and CONS - considers only the first VERB.

        verb_tokens = list(filter(lambda x: x['type']=='V', ordered_word_list))
        if len(verb_tokens) == 0:
            return
        
        first_verb_token = verb_tokens[0]
        if first_verb_token not in self.domain_verbs_set:
            return

        relationship_name = GraphGenerator.get_relationship_name(first_verb_token['lemma']) # THIS 'lemma' IS IMPORTANT.
        occurrence_date = datetime.fromisoformat(date)
        relationship_attributes = {  "happened": date, "month": occurrence_date.month, "year" : occurrence_date.year} 
        
        subject_part_tokens = []
        object_part_tokens = []
        verb_read = False

        for token in ordered_word_list:
            if token['type'] == 'V':
                verb_read = True
                continue
            elif token['type'] == 'N' and verb_read == True:
                object_part_tokens.append(token)
            elif token['type'] == 'N' and verb_read == False:
                subject_part_tokens.append(token)
            elif token['type'] == 'E' and verb_read == True:
                object_part_tokens.append(token)
            elif token['type'] == 'E' and verb_read == False:
                subject_part_tokens.append(token)
        
        for subject_token in subject_part_tokens:
            #check and get the subject node / id from the graph for mapping.
            #if it does not exist, create it.
            subject_node_type = self.get_node_type(subject_token)
            subject_node = self.graph_generator.add_node_to_graph(subject_token, subject_node_type)

            for object_token in object_part_tokens:
                #check and get the object node / id from the graph for mapping.
                #if it does not exist, create it.
                object_node_type = self.get_node_type(object_token)
                object_node = self.graph_generator.add_node_to_graph(object_token, object_node_type)

                #add the relationship between the subject and object nodes
                self.graph_generator.add_relationship_to_graph(subject_node_type, subject_node, relationship_name, object_node_type, object_node, relationship_attributes)


    def setup_schema(self, domain_words_dict):
        """
        sets up the schema with graph by executing relevant queries from the domain words dictionary
        """
        #get nodes information
        nodes_list = self.nodes_list
        node_infos = [ {'name': w} for w in nodes_list ]
        #get relationships information
        verbs_list = domain_words_dict['VerbsList']
        relationship_infos = [ {'name': w} for w in verbs_list ]
        #set up schema with graph
        self.graph_generator.setup_schema(node_infos, relationship_infos)
        self.logger.info("finished setting up schema from domain.")


    def get_node_type(self, token):
        """
        """
        # Entity --> B-ORG, I-ORG = Organization, B-PER, I-PER = Person, B-MISC, I-MISC = Object, B-LOC, I-LOC = Location
        # POS --> VERB = edge, NOUN = Object
        node_type = ''

        if (token['type'] == 'E') and ((token['entity'] == 'B-ORG') or (token['entity'] == 'I-ORG')):
            node_type = 'Organization'
        elif token['type'] == 'E' and ((token['entity'] == 'B-PER') or (token['entity'] == 'I-PER')):
            node_type = 'Person'
        elif token['type'] == 'E' and ((token['entity'] == 'B-MISC') or (token['entity'] == 'I-MISC')):
            node_type = 'Object'
        elif token['type'] == 'E' and ((token['entity'] == 'B-LOC') or (token['entity'] == 'I-LOC')):
            node_type = 'Location'
        elif token['type'] == 'N':
            node_type = 'Object'
        
        return node_type


        

        
