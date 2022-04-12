import numpy as np
import pandas as pd
import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import logging

class EntityExtractor : 
    """This class is to extract Entities from a textual content using BERT."""
    
    def __init__(self, config, logger) -> None:
        """
        constructor method. Config and Logger instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.load_bert_from_local = (config['GeneralSettings']['LoadBERTFromLocal'] == 'True')
        self.local_bert_path = config['GeneralSettings']['LocalBERTPath']
        self.remote_bert_path = config['GeneralSettings']['RemoteBERTPath']

        if self.load_bert_from_local:
            self.tokenizer = AutoTokenizer.from_pretrained(self.local_bert_path, local_files_only=True)
            self.model = AutoModelForTokenClassification.from_pretrained(self.local_bert_path, local_files_only=True)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(self.remote_bert_path)
            self.model = AutoModelForTokenClassification.from_pretrained(self.remote_bert_path)
        
        self.nlp_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer)

        self.confidence_score = float(config['InputDataSettings']['ERConfidenceScore']) # 0.7

        self.logger.info("EntityExtractor initialized.")


    def get_entities_bert(self, input_content, should_log=False):
        """
        uses BERT to extract the entities from the given input_content.
        input_content : a line of string. 
        """
        ner_results = self.nlp_pipeline(input_content)

        if(should_log):
            self.logger.info("entities extracted ner_results: %s", ner_results)

        entityList = []
        current_token = ''
        last_index = 0
        last_token_apostrophe = False

        #filter entites with less confidence
        confidence_score =  0.7 if self.confidence_score == None else self.confidence_score
        filtered_results = list(filter(lambda x: x['score'] > confidence_score, ner_results))

        for entity in filtered_results: 

            if entity['word'].startswith('##'): #bert specific prefix
                current_token += entity['word'][2:]
                entityList[-1] = { 'token' : current_token, 'entity' : entity['entity'], 'index': entity['index']}

            elif entity['word'] == "'": #apostrophe
                last_token_apostrophe = True
                current_token += entity['word'] 
                entityList[-1] = { 'token' : current_token, 'entity' : entity['entity']} #appending to last token

            elif last_token_apostrophe == True:
                current_token += entity['word'] 
                entityList[-1] = { 'token' : current_token, 'entity' : entity['entity']} #appending to last token
                last_token_apostrophe = False

            elif ((entity['index'] - last_index) <= 1 and (last_index != 0)):
                current_token += ' '+ entity['word']  
                entityList[-1] = { 'token' : current_token, 'entity' : entity['entity']} #appending to last token

            else:
                current_token = entity['word']
                entityList.append({ 'token' : current_token, 'entity' : entity['entity'], 'index': entity['index']})

            last_index = entity['index']  
            
        filter_one_letter_tokens = filter(lambda x: len(x['token']) > 1, entityList)

        if(should_log):
            self.logger.info("entities extracted final: %s", filter_one_letter_tokens)

        return list(filter_one_letter_tokens)



