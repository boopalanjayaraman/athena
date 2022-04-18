import spacy

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from tqdm import tqdm 
from io import open

from seq2seq_rnn import Seq2Seq_RNN
from attention_decoder_rnn import AttnDecoderRNN
from encoder_rnn import EncoderRNN
from data_preprocessor import DataPreprocessor


class TrainingPipeline:

    def __init__(self, logger, config) -> None:

        self.logger = logger
        self.config = config

        # prepare the nlp pipeline
        self.nlp_pipeline = spacy.load("en_core_web_sm")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')        

        self.data_preprocessor = DataPreprocessor(self.config, self.logger)

        self.hidden_size = int(config['ModelSettings']['Hidden_Size'])
        self.dropout =  float(config['ModelSettings']['Dropout'])
        self.iterations = int(config['ModelSettings']['Iterations'])
        self.print_every = int(config['ModelSettings']['Print_Every'])

        self.MAX_LENGTH = int(config['ModelSettings']['MAX_LENGTH'])

        self.seq2seq_model = None


    def start_training(self, data_file_path):

        self.logger.info("TrainingPipeline start method is called")

        # prepare the data
        input_sequence, output_sequence, pairs = self.data_preprocessor.prepare_data(data_file_path)
        

        # prepare encoder, decoder and the training seq2seq handler
        encoder = EncoderRNN(input_sequence.n_words, self.hidden_size, self.device).to(self.device)
        attn_decoder = AttnDecoderRNN(self.hidden_size, output_sequence.n_words, self.device, dropout_p= self.dropout, max_length=self.MAX_LENGTH).to(self.device)
        seq2seq_handler = Seq2Seq_RNN(self.config, self.logger, self.device, encoder, attn_decoder, input_sequence, output_sequence, pairs)

        # call the training iterations
        seq2seq_handler.train_iters(self.iterations, print_every=self.print_every)

        # evaluate it


    def load_saved_models(self, data_file_path):

        self.logger.info("load_saved_models method is called")
        # prepare the data
        input_sequence, output_sequence, pairs = self.data_preprocessor.prepare_data(data_file_path)

        # prepare encoder, decoder and the training seq2seq handler
        encoder = EncoderRNN(input_sequence.n_words, self.hidden_size, self.device).to(self.device)
        attn_decoder = AttnDecoderRNN(self.hidden_size, output_sequence.n_words, self.device, dropout_p= self.dropout, max_length=self.MAX_LENGTH).to(self.device)
        seq2seq_handler = Seq2Seq_RNN(self.config, self.logger, self.device, encoder, attn_decoder, input_sequence, output_sequence, pairs)

        #load the saved models
        seq2seq_handler.load_saved_models()
        self.seq2seq_model = seq2seq_handler


    def evaluate_saved_model(self, input_sentence):

        self.logger.info("evaluate_saved_model method is called")
        output_words, attentions = self.seq2seq_model.evaluate(input_sentence)
        output_sentence = ' '.join(output_words)
        self.logger.info(str.format("input sentence: {}", input_sentence))
        self.logger.info(str.format("output sentence: {}", output_sentence))

        return output_sentence

    


    


    

