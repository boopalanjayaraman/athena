import numpy as np
import pandas as pd
import logging
import spacy
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import  word_tokenize, sent_tokenize
import json
import os.path

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

        #installed with tar
        self.nlp_pipeline = spacy.load("en_core_web_sm")

        self.stop_words = set(stopwords.words('english'))
        self.content_title = config['InputDataSettings']['ContentTitle']
        self.most_common_count = int(config['InputDataSettings']['MostCommon'])
        self.use_optimal_most_common_count = (config['InputDataSettings']['UseOptimalMostCommonCount'] == 'True')
        self.common_word_coverage_percent = float(config['InputDataSettings']['CommonWordCoveragePercent'])

        self.dump_domain_word_lists = (config['GeneralSettings']['DumpDomainWordLists'] == 'True')
        self.preload_domain_word_lists = (config['GeneralSettings']['PreloadDomainWordLists'] == 'True')
        self.domain_verb_list_path = config['GeneralSettings']['DomainVerbListPath']
        self.domain_noun_list_path = config['GeneralSettings']['DomainNounListPath']

        if self.use_optimal_most_common_count and self.common_word_coverage_percent == 0.0:
           self.common_word_coverage_percent = 0.7 

        self.logger.info("DomainWordsExtractor initialized.")

    def extract_domain_words(self, input_file_path, should_log=False, do_full_set=False):
        """
        Extracts the domain words on a given file.
        do_full_set is by default False. Need to set it to True to run it for the whole file.
        """
        self.logger.info("extract_domain_words called.")

        #check if preloaded domain words lists are available, if so deserialize them, load them, and return the dict
        if self.preload_domain_word_lists:
            if str.strip(self.domain_verb_list_path) != '' and str.strip(self.domain_noun_list_path) != '' and os.path.isfile(self.domain_verb_list_path) and os.path.isfile(self.domain_noun_list_path):
                result_dict = {}
                with open(self.domain_verb_list_path, 'r', encoding ='utf8') as verb_json_file_r:
                    result_dict['VerbsList'] = json.load(verb_json_file_r)
                with open(self.domain_noun_list_path, 'r', encoding ='utf8') as noun_json_file_r:
                    result_dict['NounsList'] = json.load(noun_json_file_r)
                result_dict['PropsList'] = []

                self.logger.info("Loaded the extracted domain words from files (preload option).")
                return result_dict

        #else go on with the usual flow
        if input_file_path == None or input_file_path == '':
            input_file_path = self.config['InputDataSettings']['InputDataSetFile']
        
        df = pd.read_csv(input_file_path)

        verblist = []
        nounlist = []
        proplist = []

        #loop for every row
        for index, row in df.iterrows():
            try:
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
            except:
                self.logger.debug( str.format("Error processing row {}. Content: {}", index, row[self.content_title]))
                continue

        verb_counter = Counter(verblist)
        noun_counter = Counter(nounlist)    
        prop_counter = Counter(proplist)

        optimal_most_common_verb_count = self.get_optimal_most_common_count(verb_counter) if self.use_optimal_most_common_count else self.most_common_count
        optimal_most_common_noun_count = self.get_optimal_most_common_count(noun_counter) if self.use_optimal_most_common_count else self.most_common_count
        optimal_most_common_prop_count = self.get_optimal_most_common_count(prop_counter) if self.use_optimal_most_common_count else self.most_common_count

        #fetch only the most common used words
        result_dict = {}
        result_dict['VerbsList'] = [w[0] for w in verb_counter.most_common(optimal_most_common_verb_count)]
        result_dict['NounsList'] = [w[0] for w in noun_counter.most_common(optimal_most_common_noun_count)]
        result_dict['PropsList'] = [w[0] for w in prop_counter.most_common(optimal_most_common_prop_count)]

        #dump the domain verbs and nouns if configured
        if self.dump_domain_word_lists:
            if str.strip(self.domain_verb_list_path) != '' and str.strip(self.domain_noun_list_path) != '':
                with open(self.domain_verb_list_path, 'w', encoding ='utf8') as verb_json_file_w:
                    json.dump(result_dict['VerbsList'], verb_json_file_w, allow_nan=True)
                    self.logger.info(str.format("dumped the extracted domain verbs into a file. {}", self.domain_verb_list_path))

                with open(self.domain_noun_list_path, 'w', encoding ='utf8') as noun_json_file_w:
                    json.dump(result_dict['NounsList'], noun_json_file_w, allow_nan=True)
                    self.logger.info(str.format("dumped the extracted domain nouns into a file. {}", self.domain_noun_list_path))
                self.logger.info("dumped the extracted domain words into files.")
                

        self.logger.info("extract_domain_words finished.")
        self.logger.info(str.format("VerbsList: {}, NounsList:{}, PropsList:{}", len(result_dict['VerbsList']), len(result_dict['NounsList']), len(result_dict['PropsList'])))

        return result_dict

        
    def get_optimal_most_common_count(self, word_counter : Counter):
        """
        Decides the optimal most common count for the word counter
        To cover 70% of the word set
        """
        self.logger.info("get_optimal_most_common_count is called.")

        total_occurrences = sum([w[1] for w in word_counter.most_common()])
        current_occurrences = 0
        current_count = 0
        for w in word_counter.most_common():
            current_occurrences += w[1]
            current_count += 1
            if(float(current_occurrences / total_occurrences) > self.common_word_coverage_percent):
                break

        self.logger.info("get_optimal_most_common_count is finished.")
        self.logger.info(str.format("Coverage: total_occurrences:{}, covered_occurrences:{}, total_count of words:{}, considered count: {}", total_occurrences, current_occurrences, len(word_counter), current_count))

        return current_count




    

