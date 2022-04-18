import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time
import random 
import math

class Seq2Seq_RNN:

    def __init__(self, config, logger, device, encoder, decoder, input_sequence, output_sequence, pairs) -> None:
        
        self.logger = logger
        self.config = config

        self.encoder = encoder
        self.decoder = decoder
        self.input_sequence = input_sequence
        self.output_sequence = output_sequence
        self.pairs = pairs

        self.device = device

        self.MAX_VOCAB_SIZE = int(config['ModelSettings']['MAX_VOCAB_SIZE'])
        self.MIN_COUNT = int(config['ModelSettings']['MIN_COUNT'])
        self.MAX_SEQUENCE_LENGTH = int(config['ModelSettings']['MAX_SEQUENCE_LENGTH'])
        self.BATCH_SIZE = int(config['ModelSettings']['BATCH_SIZE'])
        self.MAX_LENGTH = int(config['ModelSettings']['MAX_LENGTH'])

        self.encoder_model_file = config['ModelSettings']['Encoder_Model_file']
        self.decoder_model_file = config['ModelSettings']['Attention_Decoder_Model_file']

        self.SOS_token = 0
        self.EOS_token = 1
        self.teacher_forcing_ratio = 0.5

    def train_iters(self, n_iters, print_every=1000, plot_every=100, learning_rate=0.01):

        encoder = self.encoder
        decoder = self.decoder

        start = time.time()
        plot_losses = []
        print_loss_total = 0  # Reset every print_every
        plot_loss_total = 0  # Reset every plot_every

        encoder_optimizer = optim.SGD(encoder.parameters(), lr=learning_rate)
        decoder_optimizer = optim.SGD(decoder.parameters(), lr=learning_rate)

        training_pairs = [self.tensors_from_pair(random.choice(self.pairs))
                        for i in range(n_iters)]
        criterion = nn.NLLLoss()

        for iter in range(1, n_iters + 1):
            training_pair = training_pairs[iter - 1]
            input_tensor = training_pair[0]
            target_tensor = training_pair[1]

            loss = self.train(input_tensor, target_tensor, encoder_optimizer, decoder_optimizer, criterion)
            print_loss_total += loss
            plot_loss_total += loss

            if iter % print_every == 0:
                print_loss_avg = print_loss_total / print_every
                print_loss_total = 0
                print('%s (%d %d%%) %.4f' % (self.time_since(start, iter / n_iters),
                                            iter, iter / n_iters * 100, print_loss_avg))

            if iter % plot_every == 0:
                plot_loss_avg = plot_loss_total / plot_every
                plot_losses.append(plot_loss_avg)
                plot_loss_total = 0

        torch.save(encoder.state_dict(), self.encoder_model_file)
        torch.save(decoder.state_dict(), self.decoder_model_file)

    def train(self, input_tensor, target_tensor, encoder_optimizer, decoder_optimizer, criterion):

        encoder = self.encoder
        decoder = self.decoder

        max_length = self.MAX_LENGTH
  
        encoder_hidden = encoder.initHidden()

        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        input_length = input_tensor.size(0)
        target_length = target_tensor.size(0)

        encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=self.device)

        loss = 0

        for ei in range(input_length):
            encoder_output, encoder_hidden = encoder(input_tensor[ei], encoder_hidden)
            encoder_outputs[ei] = encoder_output[0, 0]

        decoder_input = torch.tensor([[self.SOS_token]], device=self.device)

        decoder_hidden = encoder_hidden

        use_teacher_forcing = True if random.random() < self.teacher_forcing_ratio else False

        if use_teacher_forcing:
            # Teacher forcing: Feed the target as the next input
            for di in range(target_length):
                decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
                loss += criterion(decoder_output, target_tensor[di])
                decoder_input = target_tensor[di]  # Teacher forcing

        else:
            # Without teacher forcing: use its own predictions as the next input
            for di in range(target_length):
                decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
                topv, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze().detach()  # detach from history as input

                loss += criterion(decoder_output, target_tensor[di])
                if decoder_input.item() == self.EOS_token:
                    break

        loss.backward()

        encoder_optimizer.step()
        decoder_optimizer.step()

        return loss.item() / target_length

    def indexes_from_sentence(self, sequence, sentence):
        index_list = []
        for word in sentence.split(' '):
            if word in sequence.word2index:
                index_list.append(sequence.word2index[word])
            else:
                index_list.append(0)
        
        return index_list

    def tensor_from_sentence(self, sequence, sentence):
        indexes = self.indexes_from_sentence(sequence, sentence)
        indexes.append(self.EOS_token)
        return torch.tensor(indexes, dtype=torch.long, device=self.device).view(-1, 1)


    def tensors_from_pair(self, pair):
        input_tensor = self.tensor_from_sentence(self.input_sequence, pair[0])
        target_tensor = self.tensor_from_sentence(self.output_sequence, pair[1])

        return (input_tensor, target_tensor)


    def as_minutes(self, s):
        m = math.floor(s / 60)
        s -= m * 60
        return '%dm %ds' % (m, s)


    def time_since(self, since, percent):
        now = time.time()
        s = now - since
        es = s / (percent)
        rs = es - s
        return '%s (- %s)' % (self.as_minutes(s), self.as_minutes(rs))


    def evaluate(self, sentence):

        max_length = self.MAX_LENGTH
        encoder = self.encoder
        decoder = self.decoder

        with torch.no_grad():
            input_tensor = self.tensor_from_sentence(self.input_sequence, sentence)
            input_length = input_tensor.size()[0]
            encoder_hidden = encoder.initHidden()

            encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=self.device)

            for ei in range(input_length):
                encoder_output, encoder_hidden = encoder(input_tensor[ei],
                                                        encoder_hidden)
                encoder_outputs[ei] += encoder_output[0, 0]

            decoder_input = torch.tensor([[self.SOS_token]], device=self.device)  # SOS

            decoder_hidden = encoder_hidden

            decoded_words = []
            decoder_attentions = torch.zeros(max_length, max_length)

            for di in range(max_length):
                decoder_output, decoder_hidden, decoder_attention = decoder(
                    decoder_input, decoder_hidden, encoder_outputs)
                decoder_attentions[di] = decoder_attention.data
                topv, topi = decoder_output.data.topk(1)
                if topi.item() == self.EOS_token:
                    decoded_words.append('<EOS>')
                    break
                else:
                    decoded_words.append(self.output_sequence.index2word[topi.item()])

                decoder_input = topi.squeeze().detach()

            return decoded_words, decoder_attentions[:di + 1]


    def load_saved_models(self):
        self.encoder.load_state_dict(torch.load(self.encoder_model_file))
        self.decoder.load_state_dict(torch.load(self.decoder_model_file))