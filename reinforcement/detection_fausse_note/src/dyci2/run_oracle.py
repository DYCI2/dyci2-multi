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
import random

import MusicXML as Mxl
import proba
import oracle
import utils
import config

OMNIBOOK = "omnibook"
PROBA_DIR  = "proba_model"
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
	bigram_path	= utils.getPath(PROBA_DIR, config.model['bigram'])
	bigram		= proba.SubModel("bigram", bigram_path)

	melody_path		= utils.getPath(PROBA_DIR, config.model['melody'])
	melody_chord	= proba.SubModel("melody_chord", melody_path)

	proba_model		= proba.Model([bigram, melody_chord],[0.2, 0.8])

	# Oracle construction
	file_input = config.oracle['oracle']
	if len(sys.argv) >= 3:
		file_input = str(sys.argv[1])
	file_path = utils.getPath(OMNIBOOK, file_input)
	(score_info, chord_list, note_list) = utils.xml_parser(file_path)
	# CHANGEMENT DUREE
	#for note in note_list:
	#	note.duration = score_info.divisions/2

	note_labels = []
	for note in note_list:	# We choose integer representing pitch relative to octave as labels.
		note_labels.append(note.toLabel())
	pythie = oracle.FactorOracle(note_labels, note_list)

	# Improvisation parameters
	improv_length			= config.improvisation['length']
	continuity_factor_min	= config.improvisation['continuity_factor']
	taboo_list_length		= config.improvisation['taboo_length']
	context_length_min		= config.improvisation['context_length']

	# Scenario
	#scenario_file = raw_input("Fichier du scenario	: ")
	scenario_file = config.oracle['scenario']
	if len(sys.argv) >= 3:
		scenario_file = str(sys.argv[2])
	scenario_name = utils.getPath(OMNIBOOK, scenario_file)
	(_,chord_list,_) = utils.xml_parser(scenario_name)
	for chord in chord_list:
		#chord.duration = chord.duration*score_info.divisions
		chord.timestamp = chord.timestamp*score_info.divisions
	scenario = [[chord.toLabel(), chord.timestamp] for chord in chord_list]

	# Improvisation
#	improv = pythie.classicPath(improv_length, continuity_factor_min, taboo_list_length, context_length_min)
	improv = pythie.informedPath(improv_length, continuity_factor_min, taboo_list_length, context_length_min, proba_model, scenario)
	#for i in range(len(improv)):
	#	print str(improv[i])
	# OpenMusic output
	utils.back2xml(score_info, improv)
	utils.improv2OM(score_info, improv)


######## ######## ########

if __name__ == '__main__': main()
