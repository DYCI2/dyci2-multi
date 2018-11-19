import numpy as np
import random
import os
import math
import sys 

import utils
import converter as cv
import rng

class Dataset(object):
	"""
	Class for creating dataset (train, test, validation).
	"""

	def __init__(self, **kwargs):
		"""
		Initialize a dataset from datas (already converted)

		Parameters
		----------
		See dyci2 module (run function)
		"""
		self._past_index 		= 0
		self._future_index 		= 0
		self._right_index 		= 1

		self.directory = kwargs["directory"]
		self.datas = [[]]
		self.converter = cv.Converter()
		self.config(**kwargs)
		self.time_size = self.past + self.future + 1

	def config(self, **kwargs):
		for key, value in kwargs.items():
			self.__setattr__(key, value)

	def right_value(self):
		"""
		Generate output for sequence without false notes.

		Parameters
		----------

		Returns
		-------
		res:	array
				[0, 1] if self._right_index == 1.
		"""
		res = np.zeros(self.output_size)
		res[self._right_index] = 1
		return res

	def preprocess(self):
		"""
		Convert all files in self.directory in right format for feeding neural network
		(array format).
		All converted files are stocked in self.datas.

		Parameters
		----------

		Returns
		-------
		"""

		# Initialize variables
		files = []
		num_file = 0
		self.wrongs_idx = [[]]

		# Get all files in the directory
		path = os.path.join(utils.getRoot(), self.directory)
		for file in os.listdir(path):
			files.append(utils.getPath(self.directory, file))

		# Convert all files retrieved
		for data in files:
			self.converter.reset()
			self.datas.append([])
			(score_info, _, notes) = utils.xml_parser(data)
			self.converter.setKappa(score_info.divisions)
			num_note = 0
			for note in notes:
				try:
					matrix = self.converter.convert_note(note)
					for elem in matrix:
						self.datas[num_file].append(elem)	
						
						#Old preprocessing, now random notes are proceeded in next_bach()
						#new_note, has_changed = rng.random_note(elem, self.epsilon)
						#self.datas[num_file].append(new_note)
						#if has_changed:
						#	self.wrongs_idx[num_file].append(num_note)
						#num_note += 1
				except AssertionError as err:
					print(err)
					print(data)
					sys.exit(2)
			self.wrongs_idx.append([])
			num_file += 1

	def preprocess_harmony(self):
		"""
		Same as above. But in the process we take harmony into account.
		"""
		# Initialize variables
		files = []
		num_file = 0
		# Get all files in the directory
		path = os.path.join(utils.getRoot(), self.directory)
		for file in os.listdir(path):
			if file.split('/')[-1].split('.')[0][-2:] == "_m":
				files.append(utils.getPath(self.directory, file))

		# Convert all files retrieved
		for data in files:
			self.converter.reset()
			self.datas.append([])
			(score_info, _, notes) = utils.xml_parser(data)
			# Retrieve harmony file with data file
			path =  "".join([data.split('/')[-1].split('.')[0][:-2], "_h", ".xml"])
			data_h = utils.getPath(self.directory, path)
			if not os.path.isfile(data_h):
				continue
			# Convert harmony file
			harmonies =	utils.xml_harmony_parser(data_h)
			# Append harmony note (xmlnote)
			notes = [notes]
			for harmony in harmonies:
				notes.append(harmony)
			#print len(notes)
			self.converter.setKappa(score_info.divisions)
			self.datas[num_file] = self.converter.convert_with_harmony(notes, self.datas, num_file)
			num_file += 1
		temp= []
		for i in range(0, len(self.datas)-1):
			if len(self.datas[i]) > 10:
				temp.append(self.datas[i])
		self.datas = temp

	def init_inputs(self, inputs):
		"""
		Initialize inputs with only rest.

		Parameters
		----------
		inputs:		Array
					The shape is : (batch.shape, time.shape, note.shape).

		Returns
		-------
		inputs:		Array
					Inputs with only "rest" inside.
		"""
		pitch		= np.zeros(cv.PITCH_SIZE)
		octave		= np.zeros(cv.OCTAVE_SIZE)
		rhythm		= np.zeros(cv.RHYTHM_SIZE)
		pitch[-1] 	= 1
		note		= np.append(pitch, octave)
		note 		= np.append(note,  rhythm)
		for i in xrange(len(inputs[:, 0 ,0])):
			for j in xrange(len(inputs[0, :, 0])):
				inputs[i, j, :] = note
		return inputs

	def next_batch(self, batch_size=None, for_future=True):
		"""
		Creates a new batch for training.

		Parameters
		----------

		Returns
		-------
		inputs: array-like
				New batch inputs.

		outputs: array-like
				Neww batch outputs.
		"""

		batch_size = self.batch_size if batch_size == None else batch_size
		# Initialiaze inputs and outputs
		inputs 	= np.zeros((batch_size, self.time_size, self.note_size))
		outputs = np.ones((batch_size, self.output_size))
		outputs[:, :] = self.right_value()

		for n in range(batch_size):
			# Choose randomly a new file
			idx		= random.randint(0, len(self.datas) - 1)
			notes 	= self.datas[idx]

			# Choose a note where starts
			try:
				start 	= random.randint(0, len(notes)-1-self.time_size)
			except ValueError:
				print n, len(notes)
			end 	= start + self.time_size

			# Check if there is a wrong note
			"""
			for i in xrange(start, end):
				if i in self.wrongs_idx[idx]:
					outputs[n, :] = np.zeros((self.output_size))
					if (i - start) >= self.past and for_future:
						outputs[n, self._future_index] = 1
					if (i - start) < self.past and not for_future:
						outputs[n, self._past_index] = 1
			"""


			# Check if there is a wrong note without wrongd indexes
			"""
			if n%2==0:
				if for_future:
					rand = random.randint((start+end)/2 + 1, end)
				else:	
					rand = random.randint(start, (start+end)/2)
				notes[rand], _ = rng.random_note(notes[rand], 1.0)
				outputs[n, :] = [1,0]
			"""

			# Every two batch, we take a sequence with some randomized note.
			if n%2==0:
				num = int(math.ceil(self.epsilon))
				# Only in the last five notes will be randomized.
				temp = range((start+end)/2, end)
				tmp_ind = random.sample(temp, num)
				for i in tmp_ind:
					notes[i], _ = rng.random_note(notes[i], 1.0)
					outputs[n, :] = [1, 0]

			# Check if there is a wrong note equiproba
			"""
			changed = True
			if n % 2 == 0:
				# Choose a melody without false ntoes
				while changed:
					# Choose randomly a new file
					idx		= random.randint(0, len(self.datas) - 1)
					notes 	= self.datas[idx]

					# Choose a note where starts
					start 	= random.randint(0, len(notes)-1-self.time_size)
					end 	= start + self.time_size

					changed = False
					for i in range(start, end):
						if i in self.wrongs_idx[idx]:
							changed = True
							break

			else:
				# Choose a melody with at least one false note
				while changed:
					# Choose randomly a new file
					idx		= random.randint(0, len(self.datas) - 1)
					notes 	= self.datas[idx]

					# Choose a note where starts
					start 	= random.randint(0, len(notes)-1-self.time_size)
					end 	= start + self.time_size

					for i in range(start, end):
						if i in self.wrongs_idx[idx]:
							outputs[n, :] = np.zeros((self.output_size))
							# BiRNN Future
							if for_future and (i-start) >= self.past:
								outputs[n, self._future_index] = 1
								changed = False
							# BiRNN Past
							if not for_future and (i-start) < self.past:
								outputs[n, self._past_index] = 1
								changed = False
							#changed = False
			"""

			# Assign extracted melody to inputs at the batch number n
			#print outputs[n, :]
			inputs[n, :, :] = notes[start:end]

		return inputs, outputs

	def eval_batch(self, batch_size=None, for_future=True):

		batch_size = self.batch_size if batch_size == None else batch_size
		# Initialiaze inputs and outputs
		inputs 	= np.zeros((batch_size, self.time_size, self.note_size))
		outputs = np.ones((batch_size, self.output_size))
		outputs[:, :] = self.right_value()

		for n in range(batch_size):
			# Choose randomly a new file
			idx		= random.randint(0, len(self.datas) - 1)
			notes 	= self.datas[idx]

			# Choose a note where starts
			start 	= random.randint(0, len(notes)-1-self.time_size)
			end 	= start + self.time_size

			if n%2==0:
				if for_future:
					rand = random.randint((start+end)/2 + 1, end)
				else:	
					rand = random.randint(start, (start+end)/2)
				notes[rand], _ = rng.random_note(notes[rand], 1.0)
				outputs[n, :] = [1,0]

			inputs[n, :, :] = notes[start:end]

		return inputs, outputs

	def next_transpositions_batch(self, batch_size=None):
		"""
		Creates a new batch for training. In the batch, all sequences will be
		tranposed (12 transpositions).

		Parameters
		----------
		batch_size:	int
					Must be a multiple of 12.
		Returns
		-------
		inputs: array-like
				New batch inputs.

		outputs: array-like
				Neww batch outputs.
		"""

		batch_size = self.batch_size if batch_size == None else batch_size
		# Initialiaze inputs and outputs
		inputs 	= np.zeros((batch_size, self.time_size, self.note_size))
		outputs = np.ones((batch_size, self.output_size))
		outputs[:, :] = self.right_value()

		for n in range(batch_size/12):
			# Choose randomly a new file
			idx		= random.randint(0, len(self.datas) - 1)
			notes 	= self.datas[idx]

			# Choose a note where starts
			start 	= random.randint(0, len(notes)-1-self.time_size)
			end 	= start + self.time_size

			if n%2==0:
				num = int(math.ceil(self.epsilon))
				temp = range((start+end)/2, end)
				tmp_ind = random.sample(temp, num)
				for i in tmp_ind:
					notes[i], _ = rng.random_note(notes[i], 1.0)
					outputs[12*n, :] = [1, 0]


			temp = notes[start:end]
			for i in range(0, 12):
				temp_2 = np.copy(temp)
				#print temp_2
				for j in range(len(temp)):
					temp_2[j][0:12] = np.roll(temp[j][0:12], i)
					temp_2[j][-12:] = np.roll(temp[j][-12:], i)
				#print temp_2
				inputs[12*n+i, :, :] = temp_2
				outputs[12*n+i, :] = outputs[12*n, :]

		return inputs, outputs