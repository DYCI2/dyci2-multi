import numpy as np
import random
import os
import math

import utils 
import converter as cv

RIGHT_OUTPUT = [1, 0]
WRONG_OUTPUT = [0, 1]

APPRECATION_INDEX = 0
IS_THE_WRONG_NOTE_IN_PAST = 1
IS_THE_WRONG_NOTE_IN_FUTURE = 2

class Dataset(object):

	def __init__(self, **kwargs):
		"""
		Initialize a dataset from datas (already converted)

		Parameters
		----------
		datas:		Datas.
					Datas already converted in format.

		batch_size:	int
					Batch size.

		epsilon:	Float
					Percentage of wrong notes

		meaning: 	Bool
					Does a random note need to have a musical meaning.  
		"""
		self.directory = kwargs["directory"]
		self.datas = []
		self.converter = cv.Converter()
		self.config(**kwargs)
		self.time_size = self.past + self.future

	def config(self, **kwargs):
		for key, value in kwargs.items():
			self.__setattr__(key, value)

	def preprocess(self):
		# Initialize variables
		files = []
		num_file = 0
		converter 	= cv.Converter()
		self.wrongs_idx = [[]]

		# Get all files in the directory
		path = os.path.join(utils.getRoot(), self.directory)
		for file in os.listdir(path):
			files.append(utils.getPath(self.directory, file))

		# Convert all files retrieved
		for data in files:
			converter.reset()
			self.datas.append([])
			(score_info, _, notes) = utils.xml_parser(data)
			converter.setKappa(score_info.divisions)
			num_note = 0
			for note in notes:
				matrix = converter.convert_note(note)
				for elem in matrix:
					new_note, has_changed = self.random_note(elem)
					self.datas[num_file].append(new_note)
					if has_changed:
						self.wrongs_idx[num_file].append(num_note)
					num_note += 1
			self.wrongs_idx.append([])	
			num_file += 1
	
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

	def random_note(self, note):
		"""
		Randomly change a note.

		Parameters
		----------
		note:	Note
				Note to be changed.

		Returns
		-------
		note:	Note
				An altered note.
		"""
		rand = random.random()

		if (note == 1).sum() != 1: # It is not a rest
			if rand < self.epsilon:
				idx_pitch 	= random.randint(0, cv.PITCH_SIZE-2) # We don't want a rest
				idx_octave 	= random.randint(0, cv.OCTAVE_SIZE-1)
				idx_rhythm	= random.randint(0, cv.RHYTHM_SIZE-1)
				temp 		= np.zeros(cv.TOTAL_SIZE)
				temp[idx_pitch] = 1
				temp[cv.PITCH_SIZE + idx_octave] = 1

				# Also change rhythm
				if not self.meaning:
					temp[(cv.PITCH_SIZE + cv.OCTAVE_SIZE)+idx_rhythm] = 1

					#if cv.PITCH_SIZE + cv.OCTAVE_SIZE+idx_rhythm+1 < cv.TOTAL_SIZE:
					#	temp[(cv.PITCH_SIZE + cv.OCTAVE_SIZE)+idx_rhythm+1] = 0.36

					#if cv.PITCH_SIZE + cv.OCTAVE_SIZE+idx_rhythm+2 < cv.TOTAL_SIZE:
					#	temp[(cv.PITCH_SIZE + cv.OCTAVE_SIZE)+idx_rhythm+2] = 0.13
				# Don't change rhythm
				else:
					temp[(cv.PITCH_SIZE + cv.OCTAVE_SIZE):] = note[0][(cv.PITCH_SIZE + cv.OCTAVE_SIZE):]
				return temp.reshape(1, cv.TOTAL_SIZE), True
		return note, False

class ValidSet(Dataset):

	def __init__(self, **kwargs):
		Dataset.__init__(self, **kwargs)
		self.preprocess()
		
	def next_batch(self):
		inputs 	= np.empty((0, self.time_size, self.note_size), float)
		#outputs = np.empty((0, self.time_size, self.output_size), float)
		outputs = np.empty((0, 3, self.output_size), float)

		for n in xrange(0, len(self.datas)):
			notes = self.datas[n]
			x = np.zeros((len(notes), self.time_size, self.note_size), float)

			# Direct after BiRNN
			#y = np.ones((len(notes), self.time_size, self.output_size), float)
			#y[:, :, :] = [1, 0]

			# With a layer after BiRNN
			#y = np.ones((len(notes), self.output_size), float)
			#y[:, :] = [1, 0]

			# With three outputs
			y = np.ones((len(notes), 3, self.output_size), float)
			y[:, :, :] = RIGHT_OUTPUT

			x = self.init_inputs(x)
			buffer_list = []
			for i in xrange(0, len(notes)):
				# Copy the previous time step
				x[i, :, :] = x[i-1, :, :]
				# Alterate and add the next note
				#notes[i], has_changed = self.random_note(notes[i])
				temp = np.append(x[i], notes[i], axis=0)
				# Remove the oldest one
				x[i] = temp[1:]

				# Copy the previous time step
				#y[i, :, :] = y[i-1, :, :]
				# Shift left
				#temp = np.append(y[i], [[1, 0]], axis=0)
				#y[i] = temp[1:]
				buffer_list = [i-1 for i in buffer_list if i-1 >= 0]	
				if i in self.wrongs_idx[n]:
					buffer_list.append(self.time_size)

				for j in buffer_list:
					y[i, APPRECATION_INDEX, :] = WRONG_OUTPUT
					if j < self.past:
						y[i, IS_THE_WRONG_NOTE_IN_PAST, :] = WRONG_OUTPUT
					else:
						y[i, IS_THE_WRONG_NOTE_IN_FUTURE, :] = WRONG_OUTPUT

			inputs	= np.append(inputs, x, axis=0)
			outputs = np.append(outputs, y, axis=0)

		return inputs, outputs

class TestSet(Dataset):

	def __init__(self, **kwargs):
		Dataset.__init__(self, **kwargs)
		self.preprocess()
	
	def preprocess(self):
		# Initialize variables
		files = []
		self.wrongs_idx = [[]]
		i = 0
		converter 	= cv.Converter()

		# Get all files in the directory
		path = os.path.join(utils.getRoot(), self.directory)
		for file in os.listdir(path):
			files.append(utils.getPath(self.directory, file))

		# Convert all files retrieved
		for file in files:
			base = file.split('/')[-1].split('.')[0]
			ext = file.split('/')[-1].split('.')[-1]
			outname = "".join([base, ".txt"]) 
			if ext == "xml":
				converter.reset()
				self.datas.append([])
				(score_info, _, notes) = utils.xml_parser(file)
				converter.setKappa(score_info.divisions)
				for note in notes:
					matrix = converter.convert_note(note)
					for elem in matrix:
						self.datas[i].append(elem)
				with open(utils.getPath(self.directory, outname), 'r') as file:
					for line in file:
						self.wrongs_idx[i].append(int(line.rstrip('\n')))
					self.wrongs_idx.append([])		
				i += 1

	def next_batch(self):
		inputs 	= np.empty((0, self.time_size, self.note_size), float)
		#outputs = np.empty((0, self.time_size, self.output_size), float)
		outputs = np.empty((0, 3, self.output_size), float)

		for n in xrange(0, len(self.datas)):
			notes = self.datas[n]
			x = np.zeros((len(notes), self.time_size, self.note_size), float)
			#y = np.ones((len(notes), self.time_size, self.output_size), float)
			#y[:, :, :] = [1, 0]
			y = np.ones((len(notes), 3, self.output_size), float)
			y[:, :, :] = RIGHT_OUTPUT

			x = self.init_inputs(x)
			buffer_list = []

			for i in xrange(0, len(notes)):
				# Copy the previous time step
				x[i, :, :] = x[i-1, :, :]
				# Alterate and add the next note
				#notes[i], has_changed = self.random_note(notes[i])
				temp = np.append(x[i], notes[i], axis=0)
				# Remove the oldest one
				x[i] = temp[1:]

				# Copy the previous time step
				#y[i, :, :] = y[i-1, :, :]
				# Shift left
				#temp = np.append(y[i], [[1, 0]], axis=0)
				#y[i] = temp[1:]

				buffer_list = [j-1 for j in buffer_list if j-1 >= 0]
				if i in self.wrongs_idx[n]:					
					# The current notes is a wrong one, at the index FLAGS.past_size
					#y[i, -1, :] = [0, 1]
					#y[(i+1), :] = [0, 1]
					buffer_list.append(self.time_size)

				for j in buffer_list:
					y[i, APPRECATION_INDEX, :] = WRONG_OUTPUT
					if j < self.past:
						y[i, IS_THE_WRONG_NOTE_IN_PAST, :] = WRONG_OUTPUT
					else:
						y[i, IS_THE_WRONG_NOTE_IN_FUTURE, :] = WRONG_OUTPUT
									
			inputs	= np.append(inputs, x, axis=0)
			outputs = np.append(outputs, y, axis=0)

		return inputs, outputs

class TrainSet(Dataset):

	def __init__(self, **kwargs):
		Dataset.__init__(self, **kwargs)
		self.preprocess()

	"""def preprocess(self):
		# Initialize variables
		files = []
		i = 0
		converter 	= cv.Converter()
		self.wrongs_idx = [[]]

		# Get all files in the directory
		path = os.path.join(utils.getRoot(), self.directory)
		for file in os.listdir(path):
			files.append(utils.getPath(self.directory, file))

		# Convert all files retrieved
		for data in files:
			converter.reset()
			self.datas.append([])
			(score_info, _, notes) = utils.xml_parser(data)
			converter.setKappa(score_info.divisions)
			for note in notes:
				matrix = converter.convert_note(note)
				for elem in matrix:
					self.datas[i].append(elem)
			i += 1
		# Make wrongs examples
		for _ in range(0,1):	
			for data in files:
				converter.reset()
				self.datas.append([])
				(score_info, _, notes) = utils.xml_parser(data)
				converter.setKappa(score_info.divisions)
				j = 0
				for note in notes:
					matrix = converter.convert_note(note)
					for elem in matrix:
						new_note, has_changed = self.random_note(elem)
						self.datas[i].append(new_note)
						if has_changed:
							self.wrongs_idx[i-len(files)].append(j)
					j += 1
				self.wrongs_idx.append([])				
				i += 1
		"""

	def next_batch(self):
		# Initialiaze inputs and outputs
		inputs 	= np.zeros((self.batch_size, self.time_size, self.note_size))
		# Without merging
		#outputs = np.ones((self.batch_size, self.time_size, self.output_size))
		#outputs[: ,: ,:] = [1, 0]
		# With merging
		#outputs = np.ones((self.batch_size, self.output_size))
		#outputs[:, :] = [1, 0]
		outputs = np.ones((self.batch_size, 3, self.output_size))
		outputs[:, :] = [1, 0]

		for n in range(self.batch_size):
			# Choose randomly a new file
			idx		= random.randint(0, len(self.datas) - 1)
			notes 	= self.datas[idx]

			# Choose a note where starts
			start 	= random.randint(0, len(notes)-1-self.time_size)
			end 	= start + self.time_size
			alteration = random.random()

			#if alteration >= beta: # Then the impro will be modified randomly
			#for i in xrange(start, end):
			#notes[end-1], has_changed = self.random_note(notes[end-1])
			#if has_changed:
				#outputs[n, i-start, :] = [0, 1]
			#	outputs[n, :] = [0, 1]
			#if idx > len(self.datas) / 2 :
			for i in xrange(start, end):
				if i in self.wrongs_idx[idx]:
					outputs[n, APPRECATION_INDEX] = WRONG_OUTPUT
					if i - start < self.past:
						outputs[n, IS_THE_WRONG_NOTE_IN_PAST] = WRONG_OUTPUT
					else:
						outputs[n, IS_THE_WRONG_NOTE_IN_FUTURE] = WRONG_OUTPUT

			#if idx > len(self.datas) / 2:
				#outputs[n, :, :] = [0, 1]
			# Choose randomly Nf+Np successives notes
			inputs[n, :, :] = notes[start:end]

		return inputs, outputs
