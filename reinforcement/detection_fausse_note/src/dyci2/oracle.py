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
import random
import os 
from collections import deque, namedtuple

import tensorflow as tf
import numpy as np

from rl.Environnement import Environnement
from rl.QNetwork import QNetwork

import model 
import converter
import dyci2
import utils

import matplotlib.pyplot as plt

Memory = namedtuple("Memory", ["state", "action", "reward", "next_state"])
######## CLASSES ########

######## OracleState
# def __init__(self)
# def addEnteringTransition(self, transition)
# def addExitingTransition(self, transition)
# def addEnteringFactorLink(self, factor_link)
# def addExitingFactorLink(self, factor_link)
# def addSuffixLink(self, suffix_link)
# def addReverseSuffixLink(self, reverse_suffix_link)
# def labelGoesTo(self, label)
# def attainableTransition(self, context_length_min)
# def sameContextLength(self, other_state)
########
class OracleState:
	def __init__(self):
		self.entering_transition = None		# Linear entering transition
		self.exiting_transition = None		# Linear exiting transtion
		self.entering_factor_links = []		# List of all entering factor links
		self.exiting_factor_links = []		# List of all existing factor links
		self.suffix_link = None				# Suffix link of the state
		self.reverse_suffix_links = []		# List of reverse suffix links

	def addEnteringTransition(self, transition):
		self.entering_transition = transition

	def addExitingTransition(self, transition):
		self.exiting_transition = transition

	def addEnteringFactorLink(self, factor_link):
		self.entering_factor_links.append(factor_link)

	def addExitingFactorLink(self, factor_link):
		self.exiting_factor_links.append(factor_link)

	def addSuffixLink(self, suffix_link):
		self.suffix_link = suffix_link
	
	def addReverseSuffixLink(self, reverse_suffix_link):
		self.reverse_suffix_links.append(reverse_suffix_link)
	
	def labelGoesTo(self, label):		# Return state reach for current state reading the letter (None is return if there is no exiting transion or factor link labelled with the letter)
		result = None
		if self.exiting_transition.label == label:
			result = self.exiting_transition.end
		else:
			for link in self.exiting_factor_links:
				if link.label == label:
					result = link.end
		return result

	def attainableTransition(self, context_length_min):
		att = []
		# Attainables transition from this state are :
		if self.exiting_transition != None:
			att.append(self.exiting_transition)	# - the linear exiting transition (if we're not in the last state)
		
		if self.suffix_link.end != None and self.sameContextLength(self.suffix_link.end) >= context_length_min:
			att.append(self.suffix_link.end.exiting_transition)	# - the suffix link leaving the editing point if the context is sufficiently similar

		for rs_link in self.reverse_suffix_links:
			if rs_link.end.exiting_transition != None and self.sameContextLength(rs_link.end) >= context_length_min:
				att.append(rs_link.end.exiting_transition)	# - the reverse suffix link if the context is sufficiently similar

		# - the suffix link leaving the target of the suffix link and the reverse suffix links leaving it (if context sufficiently similar)
		if self.suffix_link.end != None:
			temp_state = self.suffix_link.end
			while temp_state.entering_transition != None:
				if self.sameContextLength(temp_state.suffix_link.end) >= context_length_min:
					att.append(temp_state.suffix_link.end.exiting_transition)
				for rs_link in temp_state.reverse_suffix_links:
					if rs_link.end.exiting_transition != None and self.sameContextLength(rs_link.end) >= context_length_min:
						att.append(rs_link.end.exiting_transition)
				temp_state = temp_state.suffix_link.end

		att = list(set(att))	# Remove duplicate entries
		return att			



	def sameContextLength(self, other_state):
		length = 0
		s1 = self
		s2 = other_state
		while s1.entering_transition != None and s2.entering_transition != None and s1.entering_transition.label == s2.entering_transition.label:
			length = length+1
			s1 = s1.entering_transition.start
			s2 = s2.entering_transition.start
		return length


######## Transition
# def __init__(self, start, letter, content, end):
########
class Transition:
	def __init__(self, start, label, content, end):
		self.start = start			# Starting state of the transition
		self.label = label		# Label of the transition
		self.content = content		# Full musical content of the transition
		self.end = end				# Ending state of the transition



######## SuffixLink
# def __init__(self, start, end):
########
class SuffixLink:
	def __init__(self, start, end):
		self.start = start			# Starting state of the suffix link
		self.end = end				# Ending state of the suffix link



######## FactorOracle
# def __init__(self, word)
# def createOracle(self, word)
# def addState(self, letter)
# def classicPath(self, improv_length, continuity_factor_min, taboo_list_length, context_length_min)
# def randomTransition(self, transitions)
# def informedPath(self, improv_length, continuity_factor_min, taboo_list_length, context_length_min, proba_model, scenario)
# def printOracle(self)
########
class FactorOracle:
	def __init__(self, label_list, content_list):
		self.states = []			# List of states of the oracle
		self.start = None			# Initial state
		if len(label_list) == len(content_list):
			self.createOracle(label_list, content_list)		# Oracle creation with the labels and contents
		else:
			print "Error : Can't construct oracle. Label and content lists are not the same size"

	def createOracle(self, label_list, content_list):
		init_state = OracleState()		# Construction of the initial state
		init_suffix_link = SuffixLink(init_state, None)
		init_state.addSuffixLink(init_suffix_link)		# The initial state's suffix link goes nowhere (special case)
		self.states.append(init_state)
		self.start = init_state
		for i in range(len(label_list)):
			self.addState(label_list[i], content_list[i])

	def addState(self, label, content):
		new_state = OracleState()			# Creation of a new state
		new_transition = Transition(self.states[-1], label, content, new_state) 	# Creation of a transition between new state and previous state labelled by the letter
		self.states[-1].addExitingTransition(new_transition)	# Adding transition as an exiting transtion of previous state
		new_state.addEnteringTransition(new_transition)			# Adding transition as an entering transition of new state
	
		k = new_state.entering_transition.start.suffix_link.end		# k is the state linked to the previous state with a suffix link
		while k is not None and k.labelGoesTo(label) is None:
			new_factor_link = Transition(k, label, content, new_state)		# We add the factor link if we can't find an arrow with the correct label
			k.addExitingFactorLink(new_factor_link)
			new_state.addEnteringFactorLink(new_factor_link)
			k = k.suffix_link.end	# We iterate over the suffix links
		if k is None:
			s = self.states[0]	
		else:
			s = k.labelGoesTo(label)	# s is the state we are linking to our new state with a suffix link
		new_suffix_link = SuffixLink(new_state, s)
		new_state.addSuffixLink(new_suffix_link)
		new_reverse_suffix_link = SuffixLink(s, new_state)
		s.addReverseSuffixLink(new_reverse_suffix_link)

		self.states.append(new_state)	# We had the new state to the oracle

	def classicPath(self, improv_length, continuity_factor_min, taboo_list_length, context_length_min):
		improv = []
		current_state = self.start
		n = 0		#Current length of improv
		cf = 0		#Current continuity
		taboo_list =[]
		while n < improv_length:
			if cf < continuity_factor_min and current_state.exiting_transition != None:     #if not enough continuity, follow the linear path
				selected_trans = current_state.exiting_transition
				cf =cf+1
			else:
				attainable_trans = current_state.attainableTransition(context_length_min)       #get list of attainable transition
				attainable_sans_taboo = []
				for trans in attainable_trans:          #remove attainable transition that are in the taboo list
					if not(trans.end in taboo_list):
						attainable_sans_taboo.append(trans)
					if attainable_sans_taboo != []:
						selected_trans = self.randomTransition(attainable_sans_taboo)   #choose random transition from attainable transition
					else:
						selected_trans = self.randomTransition(attainable_trans)        #in case taboo removed all possibilities
					if selected_trans == current_state.exiting_transition:
						cf = cf+1
					else:
						cf = 0
			taboo_list.append(current_state)        #update taboo list
			if len(taboo_list) > taboo_list_length:
				taboo_list.pop(0)
			improv.append(selected_trans.content)
			current_state = selected_trans.end      #update current state
			n = n+1
		return improv

	def randomTransition(self, transition_list):
		n = len(transition_list)
		rand = random.randint(0, n-1)
		return transition_list[rand]


	def informedPath(self, improv_length, continuity_factor_min, taboo_list_length, context_length_min, proba_model, scenario):
		improv = []
		current_state = self.start
		n = 0	# current improv length
		cf = 0	# current continuity
		taboo_list = []
		clock = 0
		ind_scenario = 0


		while n < improv_length:
			if cf < continuity_factor_min and current_state.exiting_transition != None and (clock+current_state.exiting_transition.content.duration)<scenario[ind_scenario+1][1] or n==0:
				selected_trans = current_state.exiting_transition
				cf = cf+1
			else:
				attainable_trans = current_state.attainableTransition(context_length_min)
				attainable_sans_taboo = []

				for trans in attainable_trans:
					if not(trans.end in taboo_list):
						attainable_sans_taboo.append(trans)
					if attainable_sans_taboo != []:
						selected_trans = self.transitionChoice(
							current_state, 
							attainable_sans_taboo, 
							proba_model, 
							scenario, 
							ind_scenario,
							action)
					else:
						selected_trans = self.transitionChoice(
							current_state, 
							attainable_trans, 
							proba_model, 
							scenario, 
							ind_scenario,
							action)
					if selected_trans == current_state.exiting_transition:
						cf = cf+1
					else:
						cf = 0

			taboo_list.append(current_state)
			if len(taboo_list)> taboo_list_length:
				taboo_list.pop(0)

			improv.append(selected_trans.content)

			clock = clock + selected_trans.content.duration
			while clock > scenario[(ind_scenario+1)%len(scenario)][1]:
				ind_scenario = (ind_scenario+1)%len(scenario)
			current_state = selected_trans.end
			n = n+1

		return improv

	def transitionChoice(self, current_state, transition_list, proba_model, scenario, ind_scenario, action):
		prev_note = current_state.entering_transition.label
		chord = scenario[ind_scenario]
		
		bigram = proba_model.submodels[0]
		melody_chord = proba_model.submodels[1]

		transition_proba = [0]*len(transition_list)

		prev_note_count = sum([x.count for x in bigram.counts if x.condition==prev_note])
		chord_count = sum([x .count for x in melody_chord.counts if x.condition==chord])

		for t in range(len(transition_list)):
			note = transition_list[t].label

			bigram_count = 0
			for idx, bc in enumerate(bigram.counts):
				if bc.event == note and bc.condition == prev_note:
					bigram_count = action[idx] * bc.count # RL UP
					break
			if prev_note_count == 0:
				bigram_proba = 0.1
			else:
				bigram_proba = 0.1+0.9*(bigram_count / (1.0*prev_note_count))

			melody_chord_count = 0
			for idx, mcc in enumerate(melody_chord.counts):
				if mcc.event == note and mcc.condition == chord[0]:
					melody_chord_count = action[168+idx] * mcc.count  # RL UP
					break
			if chord_count == 0:
				melody_chord_proba = 0.1
			else:
				melody_chord_proba = 0.1+0.9*(melody_chord_count / (1.0*chord_count))

			transition_proba[t] = 0.526*bigram_proba + 0.474*melody_chord_proba

		transition_sum = sum(transition_proba)
		transition_proba = [proba / transition_sum for proba in transition_proba]

		rand = random.random()
		i = 0
		choice = True
		temp_sum = 0

		while rand < temp_sum + transition_proba[i] and i<len(transition_proba)-1:
			temp_sum = temp_sum + transition_proba[i]
			i = i+1

		return transition_list[i]


	def printOracle(self):
		i=0
		for state in self.states:
			print "STATE : ",state
			if state.entering_transition != None:
				print "    entering transition : ", (state.entering_transition.start, state.entering_transition.label, state.entering_transition.end)
			if state.exiting_transition != None:
				print "    exiting transition : ", (state.exiting_transition.start, state.exiting_transition.label, state.exiting_transition.end)
			if state.entering_factor_links != []:
				for link in state.entering_factor_links:
					print "    entering factor link : ", (link.start, link.label, link.end)

			if state.exiting_factor_links != []:
				for link in state.exiting_factor_links:
					print "    exiting factor link : ", (link.start, link.label, link.end)

			print "    suffix link : ", (state.suffix_link.start, state.suffix_link.end)

			if state.reverse_suffix_links != []:
				for link in state.reverse_suffix_links:
					print "    reverse suffix link : ", (link.start, link.end)

			print "######## ######## ########"




















