import converter as cv
import random
import numpy as np
import xml.etree.ElementTree as ET
import os 

def randomly_modify_file(file, rate=0.128):
	"""
	Randomly modify notes in a xml file.
	It creates two files : .xml file and .txt file.
	.xml file is for musicxml. And .txt file consists of wrongs notes indexes.

	Paramters
	---------
	file:	file
			File to be randomly modified

	rate:	float
			Percent of notes to be modified
	"""
	def random_pitch():
		p = random.randint(0,6)
		if p == 0: return 'A'
		elif p == 1: return 'B'
		elif p == 2: return 'C'
		elif p == 3: return 'D'
		elif p == 4: return 'E'
		elif p == 5: return 'F'
		else: return 'G'

	def random_alter():
		return random.randint(-1,1)

	tree = ET.parse(file)
	root = tree.getroot()
	measures = root.find("part").getchildren()		# returns list of measures (bars)

	i = 0
	indexes = []
	path, ext = os.path.splitext(file)
	print "MODIFYING FILE : {}".format("".join([path, ext]))

	for measure in measures:
		for event in measure:
			if event.tag == "note":
				i += 1
				if event.find("pitch") != None:
					rand = random.random()
					if rand < rate:
						step = event.find("pitch").find("step")
						step.text = random_pitch()
						if event.find("pitch").find("alter") != None:
							alter = event.find("pitch").find("alter")
							alter.text = str(random_alter())
						octave = event.find("pitch").find("octave")
						octave.text = str(random.randint(3,5))
						indexes.append("{index}".format(index=i))

	with open("".join([path, ".txt"]), 'wb') as new_txt_file:
		new_txt_file.write(",".join(indexes))
	tree.write(file)

def random_note(note, rate):
	"""
	Randomly change a note.

	Parameters
	----------
	note:   Note (array of int)
	        Note to be changed.

	rate:	float
			Probability to change the note.

	Returns
	-------
	note:   Note
	        An altered note.
	"""
	rand = random.random()

	if (note == 1).sum() != 1: # It is not a rest
		"""
		if rand < rate:
		    idx_pitch   = random.randint(0, cv.PITCH_SIZE-2) # We don't want a rest
		    idx_octave  = random.randint(0, cv.OCTAVE_SIZE-1)
		    idx_rhythm  = random.randint(0, cv.RHYTHM_SIZE-1)

		    temp        = np.zeros(cv.TOTAL_SIZE)
		    temp[idx_pitch] = 1
		    temp[cv.PITCH_SIZE + idx_octave] = 1
		    temp[(cv.PITCH_SIZE + cv.OCTAVE_SIZE):] = note[0][(cv.PITCH_SIZE + cv.OCTAVE_SIZE):]

		    return temp.reshape(1, cv.TOTAL_SIZE), True
		"""
		new_pitch = random.randint(0, cv.PITCH_SIZE-2) # -2 we want no rest
		new_octave = cv.PITCH_SIZE + random.randint(0, cv.OCTAVE_SIZE-1)
		new_rhythm = cv.PITCH_SIZE + cv.OCTAVE_SIZE + random.randint(0, cv.RHYTHM_SIZE-1)

		octave_start	= cv.PITCH_SIZE
		rhythm_start 	= cv.PITCH_SIZE + cv.OCTAVE_SIZE
		harmony_start 	= cv.PITCH_SIZE + cv.OCTAVE_SIZE + cv.RHYTHM_SIZE
		note[0:octave_start] = 0
		note[new_pitch] = 1
		note[octave_start:rhythm_start] = 0
		note[new_octave] = 1
		#note[rhythm_start:harmony_start] = 0
		#note[new_rhythm] = 1
		#note[harmony_start:] = 0
		#for i in range(1,3):
		#	new_harmony = harmony_start + random.randint(0, cv.HARMONY_SIZE-1)
		#	note[new_harmony] = 1
		return note, True
	return note, False
