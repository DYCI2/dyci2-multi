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
import re
import math

def main():

######## VOCABULARY REDUCING ########
#
#	print "######## FILE PARSING #########"
#	with open("chord_sentences.txt") as realbook:
#		chord_list = [chord for line in realbook for chord in line.split()]		#creates a list of all the chords in the file
#
#	# We remove extensions, foreign basses, and other weird stuff (step by step, probably a more clever way but hey...)
#	chord_list = [re.sub('\(.*?\)','',chord) for chord in chord_list]
#	chord_list = [re.sub('\/*','',chord) for chord in chord_list]
#	chord_list = [re.sub('7[0-9]','7',chord) for chord in chord_list]	
#	chord_list = [re.sub('6[0-9]','6',chord) for chord in chord_list]
#	chord_list = [re.sub('9[0-9]','7',chord) for chord in chord_list]
#	chord_list = [re.sub('4[0-9]','4',chord) for chord in chord_list]
#	chord_list = [re.sub('b[2-3]','',chord) for chord in chord_list]
#	chord_list = [re.sub('aug[0-9]','aug',chord) for chord in chord_list]
#	chord_list = [re.sub('augb[0-9]','aug',chord) for chord in chord_list]
#	chord_list = [re.sub('hdim','min7b5',chord) for chord in chord_list]
#	chord_list = [re.sub('b5b5','b5',chord) for chord in chord_list]
#	chord_list = [re.sub(':$',':maj',chord) for chord in chord_list]
#	chord_list = [re.sub(':[2-6]',':maj',chord) for chord in chord_list]
#	chord_list = [re.sub(':9',':7',chord) for chord in chord_list]
#	chord_list = [re.sub(':7b[5-7]',':7',chord) for chord in chord_list]
#	chord_list = [re.sub('dim[0-9]','dim',chord) for chord in chord_list]
#	chord_list = [re.sub('maj[0-6]','maj',chord) for chord in chord_list]
#	chord_list = [re.sub('majb7','7',chord) for chord in chord_list]
#	chord_list = [re.sub('maj7b[5-6]','maj7',chord) for chord in chord_list]
#	chord_list = [re.sub('majb[5-6]','maj',chord) for chord in chord_list]
#	chord_list = [re.sub('maj9','maj7',chord) for chord in chord_list]
#	chord_list = [re.sub('min[0-6]','min',chord) for chord in chord_list]
#	chord_list = [re.sub('min9','min7',chord) for chord in chord_list]
#	chord_list = [re.sub('minb7','min7',chord) for chord in chord_list]
#	chord_list = [re.sub('minb6','min',chord) for chord in chord_list]
#	chord_list = [re.sub('min7b[6-7]','min7',chord) for chord in chord_list]
#	chord_list = [re.sub('sus4b[5-7]','sus4',chord) for chord in chord_list]
#	chord_list = [re.sub('7b5b7','7b5',chord) for chord in chord_list]
#	chord_list = [re.sub('dimb7','dim',chord) for chord in chord_list]
#	chord_list = [re.sub('7b5[3-4]','7b5',chord) for chord in chord_list]
#	chord_list = [re.sub('dimb[5-6]','dim',chord) for chord in chord_list]
#	chord_list = [re.sub('minb5','dim',chord) for chord in chord_list]
#	chord_list = [re.sub(':b5',':dim',chord) for chord in chord_list]
#
#	# Writing the result in a new file
#	rb_format = open('realbook.txt', 'w')
#	for chord in chord_list:
#		rb_format.write(chord+' ')
#	rb_format.close()
#
######## ######## ########

#	print "######## FILE PARSING ########"
	for i in range(100):
		with open("temp.txt") as realbook:
			chord_list = [chord for line in realbook for chord in line.split()]		#creates a list of all (formatted) chords in the file

#		print "######## PROCESS ########"
		if i ==0:
			T = len(chord_list)	#size of the corpus

		print "### Vocabulary count"
		voc = sorted(list(set(chord_list))) #remove duplicates, therefore creates the vocabulary
		voc_count = [chord_list.count(chord) for chord in voc]

		print "### Bigram count"
		bigram_list = []
		for i in range(len(chord_list)-1):
			bigram_list.append((chord_list[i],chord_list[i+1]))
		bigram_list = list(set(bigram_list))
	
		bi_count = [0]*len(bigram_list)
	
		perc = 10

		for i in range(len(chord_list)-1):
#			if (100*i)/len(chord_list) >= perc:
#				print str(perc)+"% completed"
#				perc = perc+10

			temp = (chord_list[i],chord_list[i+1])
			k = bigram_list.index(temp)
			bi_count[k] = bi_count[k]+1

		print "### Mutual information"
		J = [0]*len(bigram_list)
		for k in range(len(bigram_list)):
			Nij = bi_count[k]
			Ni = voc_count[voc.index(bigram_list[k][0])]
			Nj = voc_count[voc.index(bigram_list[k][1])]
	
			J[k] = math.log((Nij*T)/1.*(Ni*Nj))
			
		print "### Select candidates"		
		Jmax = max(J)
		p = 0.99
		candidates = []
		for k in range(len(J)):
			if J[k] >= p*Jmax:
				candidates.append((J[k],bigram_list[k]))
		candidates = sorted(candidates)[::-1]
		for i in range(len(candidates)):
			candidates[i] = candidates[i][1]

#		print candidates

		print "### Merge symbols"
		tree = open('treee.txt','r')
		last = tree.readlines()[-1]
		tree_list = last.split()
		tree.close()
		for cand in candidates:
			temp_f = open('temp.txt','w')
			i = 0
			while i < len(chord_list)-1:
				temp = (chord_list[i],chord_list[i+1])
				if temp == cand:
					temp_f.write(chord_list[i]+'_'+chord_list[i+1]+' ')
					i = i+2
				else:
					temp_f.write(chord_list[i]+' ')
					i = i+1
			if temp != cand: 
				temp_f.write(chord_list[-1])
			temp_f.close()
			
			with open("temp.txt") as realbook:
				chord_list = [chord for line in realbook for chord in line.split()]		#creates a list of all (formatted) chords in the file

			temp_t = open('temptree.txt','w')
			i = 0
			while i < len(tree_list)-1:
				temp = (tree_list[i],tree_list[i+1])
				if temp == cand:
					temp_t.write(tree_list[i]+"_"+tree_list[i+1]+' ')
					i = i+2
				else:
					temp_t.write(tree_list[i]+' ')
					i = i+1
			if (temp != cand) or (temp == cand and i==len(tree_list)-1):
				temp_t.write(tree_list[-1])
			temp_t.close()

			with open("temptree.txt") as tree:
				tree_list = [chord for line in tree for chord in line.split()]

		tree = open("treee.txt",'a')
		temptree = open('temptree.txt','r')
		last = temptree.readlines()[-1]
		tree.write('\n'+last)

#	print "######## RESULT ########"


######## ######## ########
if __name__ == '__main__': main()
