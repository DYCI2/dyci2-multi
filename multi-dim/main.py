#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##    ## ##    ## ##    ##
######## ######## ########
###   Ken  Deguernel   ###
######## ######## ########
###   Inria  (Nancy)   ###
###   Ircam  (Paris)   ###
######## ######## ########



######## IMPORTS ########
import sys
import os
import math

from utils import *
from proba import *
from oracle import *


######## MAIN ########
def main():

#	# Probabilistic model training
#	# Note bigram
#	note_bigram_list = []
#	for file in os.listdir('./training_set'):
#		file_name = './training_set/'+file
#		(_, _, note_list) = xml_parser(file_name)
#		note_list = [note2Label(note) for note in note_list]
#		note_bigram_file = [[note_list[i+1], note_list[i]] for i in range(len(note_list)-1)]
#		note_bigram_list = note_bigram_list + note_bigram_file
#	
#	note_bigram_list = allModulationBigram(note_bigram_list)
#
#	bigram = SubModel("bigram", note_bigram_list)
#	bigram.printSubModel()
#	bigram.writeSaveFile()



	# Probabilistic model construction with data save
	bigram = SubModel("bigram", "./data_save_omni/bigram_save.xml")
	melody_chord = SubModel("melody_chord","./data_save_omni/melody_chord_save.xml")
	proba_model = Model([bigram, melody_chord],[0.3, 0.6], 0.1)

	# Oracle construction
	file_name = "./cp_improv/Anthropology.xml"
	(score_info, chord_list, note_list) = xml_parser(file_name)

	# CHANGEMENT DUREE
	for note in note_list:
		note.duration = score_info.divisions/2

	note_labels = []
	for note in note_list:	# We choose integer representing pitch relative to octave as labels.
		note_labels.append(note2Label(note))
	pythie = FactorOracle(note_labels, note_list)

	# Improvisation parameters
	improv_length = 300
	continuity_factor_min = 5
	taboo_list_length = 16
	context_length_min = 3

	# Scenario
	scenario = [[chord2Label(chord), chord.timestamp] for chord in chord_list]

# Improvisation
#	improv = pythie.classicPath(improv_length, continuity_factor_min, taboo_list_length, context_length_min)
	improv = pythie.informedPath(improv_length, continuity_factor_min, taboo_list_length, context_length_min, proba_model, scenario)	

	# OpenMusic output
	improv2OM(score_info, improv)


######## ######## ########

if __name__ == '__main__': main()
