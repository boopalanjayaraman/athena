import numpy as np
import pandas as pd

from sequence import Sequence

class DataPreprocessor :

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def read_data(self, data_file_path):
        
        self.logger.info("read_data is called.")
        self.logger.info("starting to read the data file")

        df = pd.read_csv(data_file_path)

        pairs = []

        for index, row in df.iterrows():
            pairs.append([row['lemmatized_question'], row['sequence']])

        input_sequence = Sequence("lemmatized_question")
        output_sequence = Sequence("sequence")

        return input_sequence, output_sequence, pairs


    def prepare_data(self, data_file_path):

        self.logger.info("prepare_data is called.")

        input_sequence, output_sequence, pairs = self.read_data(data_file_path)

        for pair in pairs:
            input_sequence.add_sentence(pair[0])
            output_sequence.add_sentence(pair[1])

        self.logger.info("prepared data, counted words and vocabulary.")

        return input_sequence, output_sequence, pairs