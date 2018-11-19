#!/usr/local/bin/python
# -*- coding: utf-8 -*-

##    ## ##    ## ##    ##
######## ######## ########
###   Ken  Deguernel   ###
######## ######## ########
###   Inria  (Nancy)   ###
###   Ircam  (Paris)   ###
######## ######## ########



######## ####### ########
######## IMPORTS ########
######## ####### ########

import sys
import os
import xml.etree.ElementTree as ET
import math

######## #### ########
######## MAIN ########
######## #### ########

def main():
	
	########						     ########
	# SUB-MODELS 	:					 	    #
	# CHORD BIGRAM 	: P1 = P(Chord_t|Chord_t-1) #
	# MELODY 		: P2 = P(Chord_t|Melody_t)  #
	# SMOOOTHIN	 	: P3 = P(Chord_t)		   	#
	########							 ########

	major_kind = ['major', 'major-seventh', 'major-sixth']
	minor_kind = ['minor', 'minor-seventh', 'minor-sixth']
	dominant_kind = ['dominant', 'suspended-fourth']
	diminished_kind = ['diminished', 'half-diminished', 'diminished-seventh']

	chord_class_list = [major_kind, minor_kind, dominant_kind, diminished_kind]
	L = len(chord_class_list)
	N = 12

	all_chords = []
	for i in range(N):
		for type in chord_class_list:
			all_chords.append((i,type[0]))

	######## ######## ########
	######## TRAINING ########
	######## ######## ########

	melody_bigram_list = []
	melody_chord_list = []
	melody_prev_chord_list = []
	melody_prior_list = []
	XXZ = 0
	for file in os.listdir('./training_set'):
		file_name = './training_set/'+file
		score = parser(file_name)				#FORMAT : [score_info, chord_list, note_list]
												#FORMAT	: score_info = [divisions, beats, beat_type, key]
		divisions = score[0][0]
		chord_list = score[1]					#FORMAT : chord = [time_stamp, [chord_step, chord_alter, chord_kind]]
		note_list = score[2]					#FORMAT : note = [time_stamp, [note_step, note_alter, note_octave, note_duration]]

		score_length = note_list[-1][0] + note_list[-1][1][-1]	#Score length = timestamp of the last note + its duration (notes can be rests)

#		(chord_list, melody_list) = chord_note_list_adp(chord_list, note_list)
		chord_list = chord_list_adp(chord_list, divisions, score_length)
		melody_list = melody_list_adp(note_list, divisions, score_length)
	
		XXZ= XXZ + len(chord_list)
		
		for chord in chord_list:
			for type in chord_class_list:
				if chord[1] in type:
					chord[1] = type[0]

#		for k in range(len(chord_list)):
#			print chord_list[k], melody_list[k]

		# MELODY BIGRAM #
		for i in range(len(melody_list)-1):
			melody_bigram_list.append((melody_list[i],melody_list[i+1]))		
		# CHORD MODEL#
		for i in range(len(melody_list)):
			melody_chord_list.append((melody_list[i],(chord_list[i][0],chord_list[i][1])))
		# PREV CHORD MODEL#
		for i in range(len(melody_list)-1):
			melody_prev_chord_list.append((melody_list[i+1],(chord_list[i][0], chord_list[i][1])))
		# PRIOR #
		for i in range(len(melody_list)):
			melody_prior_list.append(melody_list[i])

	all_melody = []
	for elem in melody_chord_list:
		all_melody.append(elem[0])
	all_melody = remove_dup(all_melody)
	temp = []
	for melody in all_melody:
		for k in range(N):
			temp.append([(x+k)%12 for x in melody])
	temp[:] = [set(melody) for melody in temp]
	all_melody = remove_dup(temp)
	
	# MELODY BIGRAM #
	all_previous = all_melody
	melody_bigram_prob = [[0 for j in range(len(all_melody))] for i in range(len(all_previous))]
	for bigram in melody_bigram_list:
		for k in range(N):
			prev_temp = set([(x+k)%12 for x in bigram[0]])
			mel_temp = set([(x+k)%12 for x in bigram[1]])
			i = all_previous.index(prev_temp)
			j = all_melody.index(mel_temp)
			melody_bigram_prob[i][j] += 1

	for elem in melody_bigram_prob:
		temp = sum(elem)
		elem[:] = [1.*x/temp for x in elem]

	# CHORD MODEL #
	melody_chord_prob = [[0 for j in range(len(all_melody))] for i in range(len(all_chords))]
	for elem in melody_chord_list:
		i = all_chords.index(elem[1])
		for k in range(N):
			mel_temp = set([(x+k)%12 for x in elem[0]])
			j = all_melody.index(mel_temp)
			melody_chord_prob[(k*L+i)%(N*L)][j] += 1	
	
	for elem in melody_chord_prob:
		temp = sum(elem)
		elem[:] = [1.*x/temp for x in elem]	
		
	# PREV CHORD MODEL #
	melody_prev_chord_prob = [[0 for j in range(len(all_melody))] for i in range(len(all_chords))]
	for elem in melody_prev_chord_list:
		i = all_chords.index(elem[1])
		for k in range(N):
			mel_temp = set([(x+k)%12 for x in elem[0]])
			j = all_melody.index(mel_temp)
			melody_prev_chord_prob[(k*L+i)%(N*L)][j] += 1

	for elem in melody_prev_chord_prob:
		temp = sum(elem)
		elem[:] = [1.*x/temp for x in elem]

	# PRIOR #
	melody_prior_prob = [0 for i in range(len(all_melody))]
	for elem in melody_prior_list:
		for k in range(N):
			mel_temp = set([(x+k)%12 for x in elem])
			i = all_melody.index(mel_temp)
			melody_prior_prob[i] += 1
	temp = sum(melody_prior_prob)
	melody_prior_prob[:] = [1.*x/temp for x in melody_prior_prob]
	
	######## ########## ########
	######## VALIDATION ########
	######## ########## ########

	# Smoothing coefficient #
	alpha = 0.0
	beta = 0.0
	# Interpolation coefficient #
	bigram_coef = 0.2
	melody_coef = 0.2

	melody_bigram_list = []
	melody_chord_list = []
	melody_prev_chord_list = []
	melody_prior_list = []

	for file in os.listdir('./test_set'):
		file_name = './test_set/'+file
		score = parser(file_name)
		divisions = score[0][0]
		chord_list = score[1]
		note_list = score[2]
		
		score_length = note_list[-1][0] + note_list[-1][1][-1]	#Score length = timestamp of the last note + its duration (notes can be rests)
		
#		(chord_list, melody_list) = chord_note_list_adp(chord_list, note_list)
		chord_list = chord_list_adp(chord_list, divisions, score_length)
		melody_list = melody_list_adp(note_list, divisions, score_length)
		XXZ = XXZ + 2*len(melody_list)	
			
		for chord in chord_list:
			for type in chord_class_list:
				if chord[1] in type:
					chord[1] = type[0]
		
		
		# MELODY BIGRAM #
		for i in range(len(melody_list)-1):
			melody_bigram_list.append((melody_list[i],melody_list[i+1]))		
		# CHORD MODEL#
		for i in range(1,len(melody_list)):
			melody_chord_list.append((melody_list[i],(chord_list[i][0],chord_list[i][1])))
		# PREV CHORD MODEL#
		for i in range(len(melody_list)-1):
			melody_prev_chord_list.append((melody_list[i+1],(chord_list[i][0],chord_list[i][1])))
		# PRIOR #
		for i in range(len(melody_list)):
			melody_prior_list.append(melody_list[i])

	

	print len(melody_bigram_list), len(melody_chord_list), len(melody_prev_chord_list)
	T = len(melody_bigram_list)

	# MELODY BIGRAM #
	P1= []
	for bigram in melody_bigram_list:
		found = 0
		if set(bigram[0]) in all_previous:
			i = all_previous.index(set(bigram[0]))
			found += 1
		if set(bigram[1]) in all_melody:
			j = all_melody.index(set(bigram[1]))
			found += 1		
		if found == 2:
			P1.append(melody_bigram_prob[i][j])
		else:
			P1.append(0.0)
	
	# CHORD MODEL #
	P2 = []
	for mel_ch in melody_chord_list:
		found = 0
		if set(mel_ch[0]) in all_melody:
			j = all_melody.index(set(mel_ch[0]))
			found += 1
		if mel_ch[1] in all_chords:
			i = all_chords.index(mel_ch[1])
			found += 1
		if found == 2:
			P2.append(melody_chord_prob[i][j])
		else:
			P2.append(0.0)
	
	# PREV CHORD MODEL #
	P4 = []
	for prev_ch in melody_prev_chord_list:
		found = 0
		if set(prev_ch[0]) in all_melody:
			j = all_melody.index(set(prev_ch[0]))
			found += 1
		if prev_ch[1] in all_chords:
			i = all_chords.index(prev_ch[1])
			found += 1
		if found == 2:
			P4.append(melody_prev_chord_prob[i][j])
		else:
			P4.append(0.0)

	# SMOOTHING #
	P3 = []
	for prior in melody_prior_list:
		if set(prior) in all_melody:
			i = all_melody.index(set(prior))
			P3.append(melody_prior_prob[i])
		else:
			P3.append(0.0)		

	######## #################### ########
	######## LINEAR INTERPOLATION ########
	######## #################### ########

#	######## Full training ########
	min_entropyy = 10000
	best_bigram_coef = 0
	best_melody_coef = 0
	best_alpha = 0
	best_beta = 0
	for bigram_coef in frange(0.0, 0.001, 0.001):
		for melody_coef in frange(0.0, 0.001, 0.001):
			for alpha in frange(0.81, 0.831, 0.001):
				for beta in frange(0.17, 0.191, 0.001):
					if (bigram_coef + melody_coef + alpha + beta < 1.001) and (bigram_coef + melody_coef + alpha + beta > 0.999):
						Probs = [0 for i in range(len(P1))]
						for k in range(len(P1)):
							Probs[k] = alpha*P3[k] + beta/len(all_melody) + bigram_coef*P1[k] + melody_coef*P2[k]
						Probs_log = [0 for i in range(len(P1))]
						Probs_log[:] = [math.log(x)/math.log(2) for x in Probs]
						entropy = -1./T * sum(Probs_log)
						#print bigram_coef, melody_coef, alpha, beta, "\t\t", entropy
						if entropy < min_entropyy:
							min_entropyy = entropy
							best_bigram_coef = bigram_coef
							best_melody_coef = melody_coef
							best_alpha = alpha
							best_beta = beta
	print "ENTROPY = ", min_entropyy, "( alpha = ", best_alpha, " ; beta = ", best_beta, " ; bigram_coef = ", best_bigram_coef, " ; melody_coef = ", best_melody_coef, ")"

#	######## Full training ########
#	min_entropyy = 10000
#	best_bigram_coef = 0
#	best_melody_coef = 0
#	best_prev_coef = 0
#	best_alpha = 0
#	best_beta = 0
#	for bigram_coef in frange(0.0, 0.001, 0.1):
#		for melody_coef in frange(0.0, 0.001, 0.1):
#			for prev_coef in frange(0.36, 0.381, 0.001):
#				for alpha in frange(0.56, 0.581, 0.001):
#					for beta in frange(0.05, 0.071, 0.001):
#						if (bigram_coef + melody_coef + prev_coef + alpha + beta < 1.001) and (bigram_coef + melody_coef + prev_coef + alpha + beta > 0.999):
#							Probs = [0 for i in range(len(P1))]
#							for k in range(len(P1)):
#								Probs[k] = alpha*P3[k] + beta/len(all_melody) + bigram_coef*P1[k] + melody_coef*P2[k] + prev_coef*P4[k]
#							Probs_log = [0 for i in range(len(P1))]
#							Probs_log[:] = [math.log(x)/math.log(2) for x in Probs]
#							entropy = -1./T * sum(Probs_log)
#							if entropy < min_entropyy:
#								min_entropyy = entropy
#								best_bigram_coef = bigram_coef
#								best_melody_coef = melody_coef
#								best_prev_coef = prev_coef
#								best_alpha = alpha
#								best_beta = beta
#	print "ENTROPY = ", min_entropyy, "( alpha = ", best_alpha, " ; beta = ", best_beta, " ; bigram_coef = ", best_bigram_coef, " ; melody_coef = ", best_melody_coef, " ; prev_coef = ", best_prev_coef, ")"



#	######## ######################## ########
#	######## LOG-LINEAR INTERPOLATION ########
#	######## ######################## ########
#	min_entropy = 10000
#	best_bigram_coef = 0
#	best_melody_coef = 0
#	for bigram_coef in frange(0.0, 1.001, 0.1):
#		for melody_coef in frange(0.0, 1.001, 0.1):
#			gamma_bi = 1.0
#			delta_bi = 0.0
#			epsi_bi = 0.0
#			gamma_me = 1.0
#			delta_me = 0.0
#			epsi_me = 0.0
#			Probs = [0 for i in range(len(P1))]
#			for k in range(len(P1)):
#				Z = 0
#				prev = melody_bigram_list[k][0]
#				i = all_previous.index(prev)
#				for j in range(len(all_melody)):
#					Z = Z +(gamma_bi*melody_bigram_prob[i][j] + delta_bi*melody_prior_prob[j] + epsi_bi/len(all_melody))**bigram_coef + (gamma_me*melody_chord_prob[i][j] + delta_me*melody_prior_prob[j] +epsi_me/len(all_melody))**melody_coef 
#				
#				Probs[k] = 1./Z * (gamma_bi*P1[k] + delta_bi*P3[k] * epsi_bi/len(all_melody))**bigram_coef * (gamma_me*P2[k] + delta_me*P3[k] * epsi_me/len(all_melody))**melody_coef
#			Probs_log = [0 for i in range(len(P1))]
#			Probs_log[:] = [math.log(x)/math.log(2) for x in Probs]
#			entropy = -1./T * sum(Probs_log)
#			print entropy
#			if entropy < min_entropy:
#				min_entropy = entropy
#				best_bigram_coef = bigram_coef
#				best_melody_coef = melody_coef
#
#	print "H = ", min_entropy, "( bigram_coef = ", best_bigram_coef, " ; melody_coef = ", best_melody_coef, " )"			
#
#	for elem in melody_chord_prob:
#		print elem, sum(elem)


######## ######### ########
######## FUNCTIONS ########
######## ######### ########

def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step

########				   ########
# FUNCTION : DUPLICATES REMOVER : #
# REMOVE DUPLICATES IN A LIST	  #
########				   ########
def remove_dup(list):
	no_dup = []
	for elem in list:
		if elem not in no_dup:
			no_dup.append(elem)
	return no_dup
########

def chord_note_list_adp(chord_list, note_list):
	new_chord_list = []
	new_note_list = []
	j=0
	for i in range(len(note_list)):
		while j < len(chord_list) and chord_list[j][0] <= note_list[i][0]:
			j=j+1
		if note_list[i][1][0] != 'Rest':
			new_chord_list.append([note2int([chord_list[j-1][1][0], chord_list[j-1][1][1]]), chord_list[j-1][1][2]])
			new_note_list.append(note2int([note_list[i][1][0], note_list[i][1][1]]))
	return new_chord_list, new_note_list

########																															  ########
# FUNCTION : CHORD LIST ADAPTER :																											 #
# CREATE THE APPROPRIATE LIST OF CHORDS FROM THE RAW LIST OF CHORDS IE. A CHORD FOR EVERY HALF-BAR. (FORMAT : [[note(int),chord_kind], ...]) #
########																															  ########
def chord_list_adp(chord_list, divisions, score_length):
	new_chord_list = []
	divisions = divisions*4
	clock_times = [x*divisions for x in range(int(score_length/divisions))]
	j = 0 
	for i in clock_times:
		if j < len(chord_list)-1 and chord_list[j+1][0] <= i:	
			j = j+1
		new_chord_list.append([note2int([chord_list[j][1][0], chord_list[j][1][1]]), chord_list[j][1][2]])

	return new_chord_list
########

########																																 ########
# FUNCTION : MELODY LIST ADAPTER :																												#
# CREATE THE APPROPRIATE LIST OF MELODY FROM THE RAW LIST OF NOTES IE. A SET OF NOTES FOR EVERY HALF-BAR. (FORMAT : [set([note(int),...]),...]) #
########																																 ########
def melody_list_adp(note_list, divisions, score_length):
	melody_list = []
	divisions = divisions*4
	clock_times = [x*divisions for x in range(int(score_length/divisions))]

	c_len = len(clock_times)
	n_len = len(note_list)
	i = 0
	j = 0

	while i < c_len and j < n_len :
		if clock_times[i]<= note_list[j][0] :
			melody_list.append([])
			i = i+1
		else :
			if len(note_list[j]) > 0 :
				temp = [note_list[j][1][0],note_list[j][1][1]]
				if temp[0] != 'Rest':
					melody_list[i-1].append(note2int(temp))
			j = j+1
	if i < c_len :
		while i < c_len :
			melody_list.append([])
			i = i+1
#	if j < n_len :
#		while j < n_len :
#			melody_list[i-1].append(note_list[j])
#			j = j+1

	return melody_list
########

########																				########
# FUNCTION : NOTE TO INTEGER :																   #
# REPLACE A NOTE BY AN INTEGER VALUE BETWEEN 0 AND 11 (G# or Ab = 0, A = 1, A# or Bb = 2, ...) #
########																				########
def note2int(note):		#note here is [note_step, note_alter]
	n = note[0]
	i = 0
	if n == 'A':
		i = 1
	elif n == 'B':
		i = 3
	elif n == 'C':
		i = 4
	elif n == 'D':
		i = 6
	elif n == 'E':
		i = 8
	elif n == 'F':
		i = 9
	elif n == 'G':
		i = 11
	i = (i + note[1])%12
	return i
########

########														 ########
# FUNCTION : MUSICXML PARSER											#
# PARSE A MUSICXML FILE TO RECOVER SCORE, CHORDS AND NOTES INFORMATIONS #
########														 ########
def parser(file_name):
	print "PARSING FILE : ", file_name
	tree = ET.parse(file_name)
	root = tree.getroot()
	
	# Song attributes
	divisions = None
	beats = None
	beat_type = None
	key = None

	# Chords attributes
	chord_root_step = None	
	chord_root_alter = None
	chord_kind = None

	chord_list = []

	# Notes attributes
	note_step = None
	note_alter = None
	note_octave = None
	note_duration = None

	note_list = []
	test = []

	global_clock = 0
	global_tied = 0

	measures = root.find("part").getchildren()

	for measure in measures:
		for event in measure:
			if event.tag == "attributes":	#Getting song attributesi
				if event.find("divisions") != None:
					divisions = int(event.findtext("divisions"))
				if event.find("time") != None:
					beats = int(event.find("time").findtext("beats"))
					beat_type = int(event.find("time").findtext("beat-type"))
				if event.find("key") != None:
					key = int(event.find("key").findtext("fifths"))
	
			if event.tag == "harmony":		#Getting a chord attributes
				chord_root_step = event.find("root").findtext("root-step")
				chord_root_alter = event.find("root").findtext("root-alter")
				if chord_root_alter == None:
					chord_root_alter = 0
				chord_root_alter = int(chord_root_alter)
				chord_kind = event.findtext("kind")

				chord = [chord_root_step, chord_root_alter, chord_kind]
				chord_list.append([global_clock,chord])	#Adding the chord to the list of chords

			if event.tag == "note":			#Getting a note attributes
				if event.find("pitch") != None:		#If it is a note, it has a pitch
					note_step = event.find("pitch").findtext("step")
					note_alter = event.find("pitch").findtext("alter")
					if note_alter == None:
						note_alter = 0
					note_alter = int(note_alter)
					note_octave = int(event.find("pitch").findtext("octave"))
					note_duration = int(event.findtext("duration"))
								
					#Unification with the previous note, if they are tied
					if event.find("notations") != None:
						global_tied = global_tied + len(event.find("notations").findall("tied"))
					if global_tied >= 2:
						global_tied = global_tied - 2
						note_list[-1][-1][-1] = note_list[-1][-1][-1] + note_duration 					
					else:
						note = [note_step, note_alter, note_octave, note_duration]
						note_list.append([global_clock,note])
						test.append((note_step,note_alter))
			
				else:	#if the note doesn't have a pitch, it's a rest
					note_step = 'Rest'
					note_alter = 0
					note_octave = 0
					note_duration = int(event.findtext("duration"))

					#Unification with the previous rest, if there is one
					if note_list != [] and note_list[-1][-1][0] == 'Rest':
						note_list[-1][-1][-1] = note_list[-1][-1][-1] + note_duration
					else:
						note = [note_step, note_alter, note_octave, note_duration]
						note_list.append([global_clock,note])

				global_clock = global_clock + int(note_duration)

	score_info = [divisions, beats, beat_type, key]

	return [score_info, chord_list, note_list]
########

	
if __name__ == '__main__': main()
