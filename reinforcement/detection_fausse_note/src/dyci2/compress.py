import MusicXML as mxl
import numpy as np 
import converter as conv
import utils
import os
import extract 

def from_xml_to_n2c(file):
	"""
	Convert a .xml file to .n2c extension file.
	Note are encoding with 16 bits (or 4 hex)

	Parameters
	----------
	file:	XML file
			File to be compressed.

	Returns
	-------
	_	:	int
			0 if success, else 1.
	
	Raise
	-----
	AssertionError
	"""
	# Initialize Variables
	compressed_notes = []
	basename, ext = os.path.splitext(file)
	if ext == ".n2c" or ext == ".txt":
		return 1
	# Convert all files retrieved
	converter = conv.Converter()
	converter.reset()
	(score_info, _, notes) = utils.xml_parser(file)
	converter.setKappa(score_info.divisions)
	for note in notes:
		try:
			matrix = converter.convert_note(note)
			for elem in matrix:
				temp = from_array_to_hex(elem)
				compressed_notes.append(temp)

				temp_note, _ = extract.from_hex_to_array(temp)
				np.testing.assert_array_equal(elem, temp_note)
		except AssertionError:
			print file
			return 1
	# Assertions evaluation		
	for x in compressed_notes:
		assert len(x) == 4, "{}, {}".format(file, x)
	assert len("".join(compressed_notes)) % 4 == 0, compressed_notes

	with open("".join([basename, ".n2c"]), 'wb') as compressed_file:
		compressed_file.write("".join(compressed_notes))

	return 0

def from_txt_to_n2c(xml, txt):
	"""
	Convert a .xml file with a .txt to .n2c extension file.
	Note are encoding with 16 bits. Txt file consists of wrong notes indexes.
	Xml and txt files must have the same basename (only extension is different).

	Parameters
	----------
	xml:	XML file
			File to be compressed.

	txt:	TXT file
			File with wrongs notes indexes. Numbers are comma-separated.
	"""

	# Initialize variables
	with open(txt, 'rb') as text_file:
		wrongs = [int(line) for line in text_file.read().split(',')]
	compressed_notes = []
	basename, ext = os.path.splitext(xml)
	if ext == ".n2c" or ext == ".txt":
		return 1
	# Convert all files retrieved
	converter = conv.Converter()
	converter.reset()
	(score_info, _, notes) = utils.xml_parser(xml)
	converter.setKappa(score_info.divisions)
	for idx, note in enumerate(notes):
		try:
			matrix = converter.convert_note(note)
			for elem in matrix:
				is_wrong = idx in wrongs
				temp = from_array_to_hex(elem, is_wrong)
				compressed_notes.append(temp)

				temp_note, _ = extract.from_hex_to_array(temp)
				np.testing.assert_array_equal(elem, temp_note)
		except AssertionError:
			print file
			return 1
	# Assertions evaluation
	for x in compressed_notes:
		assert len(x) == 4, "Error in file {file}: Hexa converted equals to {hexa}".format(file=file, hexa=x)
	joined_compressed_notes = "".join(compressed_notes)
	assert len(joined_compressed_notes) % 4 == 0, "Compressed file length is not a multiple of 4 : {length}".format(length=len(joined_compressed_notes))

	with open("".join([basename, '.n2c']), 'wb') as compressed_file:
		compressed_file.write(joined_compressed_notes)

	return 0

def from_array_to_hex(narray, wrong=False):
	"""
	Compressed an array (stands for xmlnote) to a hex.
	Hex/bin format :
		1 bit : rest or not
		1 bit : linked note or not
		4 bits: pitch
		3 bits: octave
		6 bits: rhythm
		1 bit : wrong note or not

	Parameters
	----------
	narray:	array of int
			Array to be compressed

	wrong:	bool
			True if note (narray) is a wrong one, else False.
	"""
	is_linked   = 0
	is_rest     = 0
	indices     = [i for i, x in enumerate(narray[0]) if x == 1]

	if len(indices) == 3:
	    indices[1] -= conv.PITCH_SIZE
	    indices[2] -= (conv.PITCH_SIZE + conv.OCTAVE_SIZE)
	elif len(indices) == 2:
	    # It's a note without attack
	    is_linked = 1
	    indices.append(0)
	    indices[1] -= conv.PITCH_SIZE
	else:
	    is_rest = 1
	    assert indices[0] == 12, narray[0]
	    indices.append(conv.OCTAVE_SIZE)
	    indices.append(conv.RHYTHM_SIZE)
	assert indices[2] <= conv.RHYTHM_SIZE
	assert indices[1] <= conv.OCTAVE_SIZE
	assert indices[0] <= conv.PITCH_SIZE-1
	temp = []
	# Rest note
	temp.append('{0:01b}'.format(is_rest))
	# Linked note
	temp.append('{0:01b}'.format(is_linked))
	# Pitch
	temp.append('{0:04b}'.format(indices[0]))
	# Octave
	temp.append('{0:03b}'.format(indices[1]))
	# Rhythm
	temp.append('{0:06b}'.format(indices[2]))
	# Wrong note
	if wrong:
	    temp.append('{0:01b}'.format(1))
	else:
	    temp.append('{0:01b}'.format(0))

	assert len("".join(temp)) == 16, temp

	return '{0:04x}'.format(int("".join(temp), 2))	

