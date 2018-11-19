import numpy as np
import random
import os
import math

import utils
from datas.Dataset import Dataset

class TestingSet(Dataset):

	"""
	If test dataset needs another preprocess, batch function, and so on.
	"""
	
	def __init__(self, **kwargs):
		Dataset.__init__(self, **kwargs)
		#self.preprocess()
		self.preprocess_harmony()

	"""	
	def preprocess(self):
		# Initialize variables
		files = []
		self.wrongs_idx = [[]]
		num_file = 0

		# Get all files in the directory
		path = os.path.join(utils.getRoot(), self.directory)
		for file in os.listdir(path):
			files.append(utils.getPath(self.directory, file))

		# Convert all files retrieved
		for file in files:
			base = file.split('/')[-1].split('.')[:-1]
			ext = file.split('/')[-1].split('.')[-1]
			if len(base) > 1:
				outname = ".".join([base[0], base[1], "txt"])
			else:
				outname = ".".join([base[0], "txt"])
			if ext == "xml":
				self.converter.reset()
				self.datas.append([])
				(score_info, _, notes) = utils.xml_parser(file)
				self.converter.setKappa(score_info.divisions)
				for note in notes:
					matrix = self.converter.convert_note(note)
					for elem in matrix:
						self.datas[num_file].append(elem)

				with open(utils.getPath(self.directory, outname), 'r') as file:
					for line in file:
						indices = line.split(',')[:-1]
						for ind in indices:
							self.wrongs_idx[num_file].append(int(ind))
				self.wrongs_idx.append([])
				num_file += 1
	"""

	#def next_batch(self, batch_size=None, for_future=True):
	"""
		Creates a new batch for test dataset.
	"""
	"""
		batch_size = self.batch_size if batch_size == None else batch_size

		inputs 	= np.zeros((batch_size, self.time_size, self.note_size))
		outputs = np.ones((batch_size, self.output_size))
		outputs[:, :] = self.right_value()

		#for n in xrange(0, len(self.datas)):
		for n in range(batch_size):
			# Choose a random file
			idx 	= random.randint(0, len(self.datas) - 1)
			notes 	= self.datas[idx]

			# Choose a starting note, and a ending note
			start 	= random.randint(0, len(notes)-1-self.time_size)
			end 	= start + self.time_size

			for i in range(start, end):
				if i in self.wrongs_idx[idx]:
					outputs[n, :] = np.zeros((self.output_size))
					# Future BiRNN
					if (i-start) >= self.past and for_future:
						outputs[n, self._future_index] = 1 
					# Past BiRNN
					if (-start) < self.past and not for_future:
						outputs[n, self._past_index] = 1

			inputs[n, :, :]	= notes[start:end]

		return inputs, outputs
	"""