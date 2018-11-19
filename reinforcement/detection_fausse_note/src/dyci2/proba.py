#!/usr/bin/env python2
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
import math
import random
import xml.etree.ElementTree as ET


######## COND PROB ########
# def __init(self, event, condition, count)
# def increment(self)
########

class CondProb:
 #### Conditional probabily are defined by the event, the condition, and the count of occurences in the corpus
	def __init__(self, event, condition, count):
		self.event = event
		self.condition = condition
		self.count = count

 #### Increment the count of appearence by one
	def increment(self):
		self.count = self.count+1

######## ######## ########


######## SUB MODEL ########
# def __init__(self, name, training_list)
# def train(self, training_list)
# def readSaveFile(self, data)
# def writeSaveFile(self)
# def printSubModel(self)
########

class SubModel:
 #### A SubModel is defined by its name and a list containing the counts of all its events.
	def __init__(self, name, data):
		self.name = name
		if isinstance(data,str): 				#if the data are a str indicating a file, we read the datafile
			self.counts = self.readSaveFile(data)
		else:									#otherwise we construct the submodel on raw data
			self.counts = self.train(data)
		temp = 0
		for count in self.counts:
			temp = temp + count.count	
		self.nb_event = temp
		self.smooth_coef = 1
		self.add_smooth = 0
		self.back_off_smooth = 0
	
 #### Train the SubModel from the raw data
	def train(self, training_list):
		counts = []					#the training is simply based on a counting function.
		for elem in training_list:
			i=0
			cond_prob_found = False
			
			while cond_prob_found == False and i < len(counts):
				if elem[0] == counts[i].event and elem[1] == counts[i].condition:
					counts[i].increment()
					cond_prob_found = True
				else:
					i=i+1
			if cond_prob_found == False:
				counts.append(CondProb(elem[0],elem[1],1))

		return counts

 #### Load the SubModel from a xml save file
	def readSaveFile(self, path):
		counts = []
		tree = ET.parse(path)
		root = tree.getroot()
		cond_probs = root.getchildren()

		for cond_prob in cond_probs:
			for elem in cond_prob:
				if elem.tag == "event":
					event = []
					for event_content in elem:
						content = event_content.findtext("content")
						e_type = event_content.findtext("type")
						if e_type == 'str':
							event.append(content)
						elif e_type == 'int':
							event.append(int(content))
						else:
							print "error during loading, type unknown, improve code to include this type. Sorry."
			
				if elem.tag == "cond":
					cond = []
					for cond_content in elem:
						content = cond_content.findtext("content")
						c_type = cond_content.findtext("type")
						if c_type == 'str':
							cond.append(content)
						elif c_type == 'int':
							cond.append(int(content))
						else:
							print "error during loading, type unknown, improve code to include this type. Sorry."
						
			count = int(cond_prob.findtext("count")) 		
			counts.append(CondProb(event,cond,count))

		return counts

 #### Save the SubModel in a xml save file
	def writeSaveFile(self):
		filename = self.name + '_save.xml'
		file = open(filename, 'w')
		file.write('<?xml version="1.0" encoding="UTF-8"?>\n<!--SubModel : '+self.name+'-->\n<submodel>\n')
		for cond_prob in self.counts:
			file.write('  <condprob>\n    <event>\n')
			for content in cond_prob.event:
				t = str(type(content))[7:-2]	# get a string describing the type of content (ex : int, float, str)
				file.write('      <event_content>\n        <content>'+str(content)+'</content>\n        <type>'+t+'</type>\n      </event_content>\n')
			file.write('    </event>\n    <cond>\n')
			
			for content in cond_prob.condition:
				t = str(type(content))[7:-2]
				file.write('      <cond_content>\n        <content>'+str(content)+'</content>\n        <type>'+t+'</type>\n      </cond_content>\n')
			file.write('    </cond>\n    <count>'+str(cond_prob.count)+'</count>\n  </condprob>\n')

		file.write('</submodel>')
		file.close()

 #### Print function
	def printSubModel(self):
		print "SUBMODEL : ", self.name
		print "########"
		for cond_prob in self.counts:
			print cond_prob.event, cond_prob.condition, " : ", cond_prob.count
		print self.nb_event 
######## ######## ########


######## MODEL ########
# def __init__(self, submodels_list, validation_data)
######## ##### ########
class Model:
	def __init__(self,submodels_list, coef_list):
		self.submodels = submodels_list
		self.coefficients = coef_list
