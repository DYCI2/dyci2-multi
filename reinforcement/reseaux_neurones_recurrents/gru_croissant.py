import numpy as np
import os
import sys
import torch
import time
from torch.autograd import Variable

dtype = torch.FloatTensor # CPU
# dtype = torch.cuda.FloatTensor # GPU


model_name = sys.argv[1]

# Dossier contenant les donnees d entrainement
data_dir = ''


input_size = 88 # taille du vecteur d entree
hidden_size = 100 # taille du vecteur de memoire
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
		return Variable(torch.randn(1,1, self.hidden_size), requires_grad=True).cuda()
	def forward(self, input):
		output, self.hidden = self.rnn(input, self.hidden)
		output = output.squeeze(1)
		output = output[-1].unsqueeze(0)
		prediction = self.softmax(self.proj(output))
		return prediction

model = simpleGRU(input_size, hidden_size, batch)
model.cuda()
if os.path.exists(model_name):
	model.load_state_dict(torch.load(model_name))
loss_function = torch.nn.MSELoss()
optimizer = torch.optim.Adagrad(model.parameters(), lr=0.1)

loss_tab = []
for epoch in range(40):
	list_seq = os.listdir(data_dir)
	for i, seq in enumerate(list_seq):
		for sequence_size in range(1,64):
			data = np.loadtxt(data_dir + seq, np.int32)
			data_in = torch.FloatTensor(data.tolist()[0:sequence_size]).cuda()
			data_in = data_in.unsqueeze(1)
			#data_out = torch.LongTensor(np.where(data[sequence_size]>0)[0])
			data_out = torch.FloatTensor(data.tolist()[sequence_size]).cuda()
			data_out = data_out.unsqueeze(1)
			input = Variable(data_in, requires_grad=True)
			output = Variable(data_out, requires_grad=False)
			model.zero_grad()
			model.hidden = model.init_hidden()
			prediction = model(input)
			loss = loss_function(prediction , output)
			loss.backward()
			optimizer.step()
			if i % 100 == 0:
				print("epoch " + str(epoch) + " | loss " + str(loss))
				loss_tab.append(loss)
print(loss_tab)
print('Total time : ' + str(time.time()-start))
torch.save(model.state_dict(), model_name)






