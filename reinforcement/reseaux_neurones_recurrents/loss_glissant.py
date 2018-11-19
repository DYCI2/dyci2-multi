import numpy as np
import os
import sys
import torch
import time
from torch.autograd import Variable

dtype = torch.FloatTensor # CPU
# dtype = torch.cuda.FloatTensor # GPU


corpus_dir = '/Users/nliberma/Documents/Thesis/corpus/B50/'
model_dir = '/Users/nliberma/Documents/Thesis/experiment/noir_seq_gru_do_translatif_B50/'


input_size = 88 # taille du vecteur d entree
hidden_size = 100 # taille du vecteur de memoire
window_size = 16 # taille de la fenetre d historique
batch = 1
start = time.time()

class simpleGRU(torch.nn.Module):
	def __init__(self, input_size, hidden_size, batch):
		super(simpleGRU, self).__init__()
		self.hidden_size = hidden_size
		self.rnn = torch.nn.GRU(input_size=input_size, 
					hidden_size=hidden_size,
					num_layers=1)
		self.proj = torch.nn.Linear(hidden_size, input_size)
		self.softmax = torch.nn.Softmax()
		self.hidden = self.init_hidden()
	def init_hidden(self):
		return Variable(torch.randn(1,1, self.hidden_size), requires_grad=True)
	def forward(self, input):
		output, self.hidden = self.rnn(input, self.hidden)
		output = output.squeeze(1)
		output = output[-1].unsqueeze(0)
		prediction = self.softmax(self.proj(output))
		return prediction

loss_function = torch.nn.MSELoss()
model_name = model_dir + str(1) + '/model/model' + str(1)
model = simpleGRU(input_size, hidden_size, batch)
if os.path.exists(model_name):
	model.load_state_dict(torch.load(model_name, map_location=lambda storage, loc: storage))
	print('MODEL LOADED')


for epoch in range(1):
	list_seq = os.listdir(corpus_dir)
	for j in range(window_size+1, 64):
		
		total_loss = 0
		for i in range(len(list_seq)):
			data = np.loadtxt(corpus_dir + list_seq[i], np.int32)
			data_in = torch.FloatTensor(data.tolist()[j-windows_size:j])
			data_in = data_in.unsqueeze(1)
			data_out = torch.FloatTensor(data.tolist()[j])
			data_out = data_out.unsqueeze(1)
			input = Variable(data_in, requires_grad=True)
			output = Variable(data_out, requires_grad=False)
			model.zero_grad()
			model.hidden = model.init_hidden()
			prediction = model(input)
			loss = loss_function(prediction , output)
			total_loss += float(loss.data.numpy())
				
		mean_loss = total_loss / i
		print(str(j) + ' : ' + str(mean_loss))
print('Total time : ' + str(time.time()-start))

