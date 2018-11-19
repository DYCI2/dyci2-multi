import utils
import numpy as np
import os
import MusicXML as mxl

PITCH_SIZE = 13

OCTAVE_SIZE = 7
MINIMUM_OCTAVE = 1
MAXIMUM_OCTAVE = 7
HARMONY_SIZE = 12

RHYTHM_SIZE = 24
TOTAL_SIZE = PITCH_SIZE \
			+ OCTAVE_SIZE \
			+ RHYTHM_SIZE 
			#+ HARMONY_SIZE

class Converter():

	"""
	Converter Classe.
	Allows to fix the tatum, convert note into an array, and so on.
	"""
	def __init__(self, size_window=RHYTHM_SIZE, 
			step_size=PITCH_SIZE, 
			octave_size=OCTAVE_SIZE, 
			rhythm_size=RHYTHM_SIZE,
			harmony_size=HARMONY_SIZE):
		"""
		window 		: rhythm array
		index 		: where we are in the current pulse
		threshhold 	: rhythm array size
		kappa 		: value for normalize tatums
		"""
		self.window 		= np.zeros(size_window)
		self.index			= 0
		self.threshhold		= rhythm_size
		self.kappa			= 0
		self.step_size		= step_size
		self.octave_size	= octave_size
		self.rhythm_size	= rhythm_size
		self.harmony_size 	= harmony_size

	def setKappa(self, k):
		self.kappa = float(RHYTHM_SIZE) / float(k)

	def step2array(self, note):
		"""
		Convert note's step to an one-hot vector.

		Parameters
		----------
		note:   XmlNote
		        Note to be converted.

		Returns
		-------
		y:  array
		    One-hot vector embodies note's step.
		"""
		y = np.zeros(self.step_size)
		k = note.toLabel()[0] # toLabel() returns an array !
		y[k] = 1
		# If the note is a rest, k is -1 and y[-1] stands for the last element
		return y

	def harmony2array(self, note):
		"""
		Convert note's step to an one-hot vector for harmony.

		Parameters
		----------
		note:   XmlNote
		        Note to be converted.

		Returns
		-------
		y:  array
		    One-hot vector embodies note's step for harmony.
		"""
		y = np.zeros(self.harmony_size)
		k = note.toLabel()[0] # toLabel() returns an array !
		if k != -1:
			# If the note is not a rest
			y[k] = 1
		return y

	def octave2array(self, note):
		"""
		Return an one-hot vector to embody octave value.
		Rest is an array with only zeros in it.

		Parameters
		----------
		note:   XmlNote
		        Note to be converted.

		Returns
		-------
		y:      array
		        One-hot vector embodies note's octave.
		"""
		y = np.zeros(self.octave_size)
		k = note.octave2Label()
		assert k <= MAXIMUM_OCTAVE, "{}\n{}".format(note, k)
		assert (k >= MINIMUM_OCTAVE or k==-1), "{}\n{}".format(note, k)
		if k != -1:
		    # It is not a rest
		    y[ k - MINIMUM_OCTAVE ] = 1
		return y

	def rhythm2array(self, note):
		"""
		Convert note's duration to a vector for Neural Network.

		Parameters
		----------
		note:	XmlNote
				Note to be converted.

		Returns
		-------
		window: array of int
		        Array embodies note's rhythm in a quarter.
		"""
		self.window = np.zeros(self.window.shape)
		if self.index >= self.threshhold:
		    # It is a new quarter, clear window and update j
		    #self.window 	= np.zeros(self.window.shape)
		    self.index 		= self.index - self.threshhold
		if note.step != mxl.REST:
			# It is not a rest, there's an attack at j
			self.window[self.index] = 1
		# Update j by adding note's duration renormalized
		self.index = self.index + int(note.duration * self.kappa)
		return self.window

	def convert_note(self, note):
		"""
		Create note as an input for the neural network.

		Parameters
		----------
		note:	XmlNote
				Note to be preprocessed. Shape (1,n)

		Returns
		-------
		y:      array
		        Returns an array of inputs (because a note can take more than 1 array to be described).
		"""
		y = []
		temp = self.step2array(note)
		temp = np.append(temp, self.octave2array(note))
		temp = np.append(temp, self.rhythm2array(note))
		y.append(temp.reshape(1, TOTAL_SIZE))
		while self.index > self.threshhold:
			temp = self.step2array(note)
			temp = np.append(temp, self.octave2array(note))
			temp = np.append(temp, np.zeros(self.window.shape))
			self.window = np.zeros(self.window.shape)
			y.append(temp.reshape(1, TOTAL_SIZE))
			self.index -= self.threshhold
		return np.array(y)

	def convert_note_to_harmony(self, note):
		"""
		Create an harmony from a note

		Parameters
		----------
		Note:	XmlNote
				Note to be converted into an harmony. Shape (1,n)

		Returns
		-------
		y:	array
			Returns an array describing an harmony. 
			If an note is longer than a quarter note, an array is required.
		"""	
		y = []
		temp = self.harmony2array(note)
		y.append(temp.reshape(1, self.harmony_size))
		while self.index > self.threshhold:
			temp = self.harmony2array(note)
			self.window = np.zeros(self.window.shape)
			y.append(temp.reshape(1, self.harmony_size))		
			self.index -= self.threshhold	
		return np.array(y)

	def reset(self):
		self.__init__()

	def convert_with_harmony(self, music, datas, num_file):
		"""
		Convert a musical sequence made with melody and chord/harmony.

		Parameters
		----------
		music:	XmlNote[][]
				Matrix score. 
				Assert that the first row stands for the melody.

		datas:	Int[][]
				Data to be filled

		num_file:	int
					Number of the file.

		Returns
		-------
		datas:	
				Converted data.
		"""
		indice 		= [-1] * len(music)
		time_remain = [0] * len(music)
		harmony 	= np.zeros(self.harmony_size)
		#for i in range(1, len(music)):
		#	time_remain[i] = music[i][indice[i]].duration
		# For each note in the melody
		for note in music[0]:
			# Convert the note
			matrix = self.convert_note(note)
			# Create harmony
			harmony 	= np.zeros(self.harmony_size)
			for i in range(1, len(music)):
				if time_remain[i] == 0:
					indice[i] += 1

					# Why do I need to do this ?
					if indice[i] == len(music[i]):
						indice[i] -= 1

					time_remain[i] += music[i][indice[i]].duration
				harmony_i = self.harmony2array(music[i][indice[i]])
				np.logical_or(harmony, harmony_i, out=harmony)
				# Update
				time_remain[i] -= note.duration
				# If there's more than one note in that melody's note
				while time_remain[i] < 0:
					indice[i] += 1

					# Why do I need to do this ?
					if indice[i] == len(music[i]):
						indice[i] -= 1

					time_remain[i] += music[i][indice[i]].duration
					harmony_i = self.harmony2array(music[i][indice[i]])
					np.logical_or(harmony, harmony_i, out=harmony)
			# Finally append harmony to each converted note
			for elem in matrix:
				elem = np.append(elem,harmony)
				datas[num_file].append(elem)
		return datas[num_file]