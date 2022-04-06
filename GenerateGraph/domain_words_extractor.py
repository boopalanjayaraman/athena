import numpy as np
import pandas as pd
import logging
import spacy
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import  word_tokenize, sent_tokenize

nltk.download('stopwords')
nltk.download('punkt')

class DomainWordsExtractor : 
    """This class is to go through a given full-dataset and understand the most used common words in order to create a list of domain relationships and nouns for the graph."""

    symbolList = ['`','~', '!','@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '[', '}', ']', '|', '\\', ':', ';', '"', '\'',',', '<', '.', '>', '?', '/' ] #list of symbols to omit during tokenization

    def __init__(self, config, logger) -> None:
        """
        constructor method. Config and Logger instances have to be passed on from the caller.
        """
        self.config = config
        self.logger = logger

        self.nlp_pipeline = spacy.load("en_core_web_sm")

        self.stop_words = set(stopwords.words('english'))
        self.content_title = config['InputDataSettings']['ContentTitle']
        self.most_common_count = int(config['InputDataSettings']['MostCommon'])

        self.logger.info("DomainWordsExtractor initialized.")

    def extract_domain_words(self, input_file_path, should_log=False, do_full_set=False):
        """
        Extracts the domain words on a given file.
        do_full_set is by default False. Need to set it to True to run it for the whole file.
        """
        if input_file_path == None or input_file_path == '':
            input_file_path = self.config['InputDataSettings']['InputDataSetFile']
        
        df = pd.read_csv(input_file_path)

        verblist = []
        nounlist = []
        proplist = []

        #loop for every row
        for index, row in df.iterrows():
            content = str.lower(row[self.content_title])
            tokenized = [w for w in word_tokenize(content) if not w in self.stop_words and not w in DomainWordsExtractor.symbolList]

            pos_content = self.nlp_pipeline(" ".join(tokenized))

            for token in pos_content: 
                if(token.pos_ == "VERB"):
                    verblist.extend([token.lemma_]) #lemmatized (for relationship)
                elif(token.pos_ == "PROPN"):
                    proplist.extend([token.text]) 
                elif(token.pos_ == "NOUN"):
                    nounlist.extend([token.text])
            
            if do_full_set == False and index > 99:
                break

        verb_counter = Counter(verblist)
        noun_counter = Counter(nounlist)    
        prop_counter = Counter(proplist)

        #fetch only the most common used words
        result_dict = {}
        result_dict['VerbsList'] = [w[0] for w in verb_counter.most_common(self.most_common_count)]
        result_dict['NounsList'] = [w[0] for w in noun_counter.most_common(self.most_common_count)]
        result_dict['PropsList'] = [w[0] for w in prop_counter.most_common(self.most_common_count)]

        return result_dict

        


    

