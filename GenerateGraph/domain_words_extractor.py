from lib2to3.pygram import Symbols
from unittest import result
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

    symbolList = ['`','~', '!','@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '[', '}', ']', '|', '\\', ':', ';', '"', '\'',',', '<', '.', '>', '?', '/' ]

    def __init__(self, config, logger) -> None:
        self.config = config
        self.logger = logger

        self.nlp_pipeline = spacy.load("en_core_web_sm")

        self.stop_words = set(stopwords.words('english'))
        self.content_title = config['InputDataSettings']['ContentTitle']
        self.most_common_count = int(config['InputDataSettings']['MostCommon'])

        self.logger.info("DomainWordsExtractor initialized.")

    def extract_domain_words(self, input_file_path, should_log=False, do_full_set=False):

        if input_file_path == None or input_file_path == '':
            input_file_path = self.config['InputDataSettings']['InputDataSetFile']
        
        df = pd.read_csv(input_file_path)

        verblist = []
        nounlist = []
        proplist = []

        #loop for every row
        for index, row in df.iterrows():
            content = str.lower(row['headline'])
            tokenized = [w for w in word_tokenize(content) if not w in self.stop_words and not w in DomainWordsExtractor.symbolList]

            pos_content = self.nlp_pipeline(" ".join(tokenized))

            for token in pos_content: 
                if(token.pos_ == "VERB"):
                    verblist.extend([token.text])
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
        result_dict['VerbsList'] = verb_counter.most_common(self.most_common_count)
        result_dict['NounsList'] = noun_counter.most_common(self.most_common_count)
        result_dict['PropsList'] = prop_counter.most_common(self.most_common_count)

        return result_dict

        


    

