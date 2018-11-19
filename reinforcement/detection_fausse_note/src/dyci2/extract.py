import numpy as np 
import MusicXML as mxl
import converter as conv
import utils

def from_hex_to_array(hexa):
	"""
	Convert an hexadecimal to an array.

	Parameters
	----------
	hexa:   hexadecimal (string)
	        Hexadecimal representation of a note

	Returns
	-------
	note:   array of int
	        Array representation of a note

	is_wrong: bool
			If it is a wrong note, it returns 1. Else it returns 0
	"""
	binaries = "{0:016b}".format(int(hexa, 16))
	is_rest     = int(binaries[0:1], 2)
	is_linked   = int(binaries[1:2], 2)
	pitch       = int(binaries[2:6], 2)
	octave      = int(binaries[6:9], 2)
	rhythm      = int(binaries[9:15], 2)
	is_wrong    = int(binaries[15:16], 2)
	note = np.zeros((conv.TOTAL_SIZE))

	assert not (is_rest and is_linked) 
	# Pitch
	if is_rest:
	    assert pitch == conv.PITCH_SIZE-1
	    note[conv.PITCH_SIZE-1] = 1
	else:
	    note[pitch] = 1
	    note[octave + conv.PITCH_SIZE] = 1
	    if not is_linked:
	        note[rhythm + conv.PITCH_SIZE + conv.OCTAVE_SIZE] = 1

	return note.reshape(1, conv.TOTAL_SIZE), is_wrong

def from_hex_to_xmlnote(hexa):
	"""
	Convert an hexadecimal to a XmlNote.

	Parameters
	----------
	hexa:	hexadecimal (string)
			Hexadecimal representation of a note

	Returns
	-------
	note:	XmlNote
			Returns a XmlNote.

	opt:	int
			Indicates if it is a linked note or a rest.
	"""
	array_note, _ = from_hex_to_array(hexa)
	note = mxl.XmlNote('C',0,0,0)
	indices = [i for i, x in enumerate(array_note[0]) if x == 1]

	opt = 0
	if len(indices) == 3:
	    # It is a full note
	    note.step_from_int(indices[0])
	    note.octave_from_int(indices[1])
	    note.duration_from_int(indices[2])
	elif len(indices) == 2:
	    # It is a linked note
	    # Or a new quarter
	    opt = None
	elif len(indices) == 1:
	    # It is a rest
	    opt = -1

	return note, opt

def from_n2c_to_xml(file):
	print '[INFO] Uncompressing : {}'.format(file)
	# Initialize variables
	score_info = mxl.XmlScore(60, 4, 4, 0)
	note = mxl.XmlNote('REST',0,0,60)
	notes = [note]
	# Convert all files retrieved
	with open(file, 'rb') as text:
		hexas = text.read()
		hexas = hexas.split(',')
		for hexa in hexas[:-1]:
			note, opt = from_hex_to_xmlnote(hexa)
			if opt == 0:
				# Still in the same quarter
				notes[-1].duration = note.duration - notes[-1].duration
				notes.append(note)
			elif opt == 60:
				# New quarter and linked note
				notes[-1].duration = 60 - notes[-1].duration
	utils.back2xml(score_info, notes)

def from_n2c_to_array(file):
	with open(file, 'rb') as file:
		hex_notes = map("".join, zip(*[iter(file.read())]*4))
		array_notes, array_wrongs = list(zip(*[from_hex_to_array(hexa) for hexa in hex_notes]))
	return array_notes, array_wrongs