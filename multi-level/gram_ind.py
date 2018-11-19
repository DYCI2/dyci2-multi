#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import math
import itertools

def main():

	with open("chart.txt") as corpus:
		chord_list = [chord for line in corpus for chord in line.split()]
	
	grammar = open("grammar.txt","w")

	N = 50

	chord_list = groupDups(chord_list)
	dups = [elem for elem in sorted(list(set(chord_list))) if elem.count("_") > 0]
	dups.remove("__START__")
	dups.remove("__END__")
	for symb in dups:
		same_len = [elem for elem in sorted(list(set(chord_list))) if elem.count("_") == symb.count("_") and elem != symb]
		if same_len != []:
			voc, voc_count = getVoc(chord_list)
			bigram_list, bigram_count = getBigrams(chord_list, voc)
			T = len(chord_list) - chord_list.count("__START__") - chord_list.count("__END__")
			J = getMutualInfo(bigram_list, bigram_count, voc, voc_count, T)
			eq_symb = searchSimSymb(symb, same_len, bigram_list, J, voc)
			if eq_symb != None:
				rule = eq_symb + " <=> " + symb + "\n"
				grammar.write(rule)
				chord_list = replaceSymb(chord_list, symb, eq_symb)

	for i in range(N):
		voc, voc_count = getVoc(chord_list)
		bigram_list, bigram_count = getBigrams(chord_list, voc)
		T = len(chord_list) - chord_list.count("__START__") - chord_list.count("__END__")
		Jmax_ind = getMutualInfoMax(bigram_list, bigram_count, voc, voc_count, T)

		beg = bigram_list[Jmax_ind][0]
		end = bigram_list[Jmax_ind][1]
		rule = beg + "_" + end + " ==> " + beg + " + " + end + "\n"
		grammar.write(rule)
		
		chord_list = groupSymb(chord_list, beg, end)
		
		new_symb = beg + "_" + end
		same_len = [elem for elem in voc if elem.count("_") == new_symb.count("_")]

		if same_len != []:
			voc, voc_count = getVoc(chord_list)
			bigram_list, bigram_count = getBigrams(chord_list, voc)
			T = len(chord_list) - chord_list.count("__START__") - chord_list.count("__END__")
			J = getMutualInfo(bigram_list, bigram_count, voc, voc_count, T)
			
			eq_symb = searchSimSymb(new_symb, same_len, bigram_list, J, voc)
			if eq_symb != None:
				rule = eq_symb + " <=> " + new_symb + "\n"
				grammar.write(rule)
				chord_list = replaceSymb(chord_list, new_symb, eq_symb)

	grammar.close()

def groupDups(chord_list):
	chord_len = [len(list(y)) for x,y in itertools.groupby(chord_list)]
	chord_list = [x for x,y in itertools.groupby(chord_list)]
	for i in range(len(chord_list)):
		if chord_len[i] > 1:
			for j in range(chord_len[i]-1):
				chord_list[i] = chord_list[i] + '_'
	return chord_list

def getVoc(chord_list):
	voc = sorted(list(set(chord_list)))
	voc.remove("__START__")
	voc.remove("__END__")
	voc_count = [chord_list.count(symb) for symb in voc]
	return voc, voc_count

def getBigrams(chord_list, voc):
	bigram_list = [pair for pair in itertools.product(voc, voc)]
	bigram_count = [0]*len(bigram_list)
	for i in range(len(chord_list)-1):
		if chord_list[i] != "__START__" and chord_list[i] != "__END__" and chord_list[i+1] != "__START__" and chord_list[i+1] != "__END__":
			temp = (chord_list[i], chord_list[i+1])
			k = bigram_list.index(temp)
			bigram_count[k] = bigram_count[k]+1
	return bigram_list, bigram_count

def getMutualInfoMax(bigram_list, bigram_count, voc, voc_count, T):
	J = [0]*len(bigram_list)
	for k in range(len(bigram_list)):
		Nij = bigram_count[k]
		Ni = voc_count[voc.index(bigram_list[k][0])]
		Nj = voc_count[voc.index(bigram_list[k][1])]
		if Nij == 0:
			J[k] = -1000
		else:
			Z = bigram_list[k][0].count("_") + bigram_list[k][1].count("_") +2
			J[k] = math.log((Nij*T)/(1.*(Ni*Nj))) /((1.*Z)**2)
	return J.index(max(J))

def getMutualInfo(bigram_list, bigram_count, voc, voc_count, T):
	J = [0]*len(bigram_list)
	for k in range(len(bigram_list)):
		Nij = bigram_count[k]
		Ni = voc_count[voc.index(bigram_list[k][0])]
		Nj = voc_count[voc.index(bigram_list[k][1])]
		if Nij == 0:
			J[k] = 0
		else:
			J[k] = math.log((Nij*T)/(1.*(Ni*Nj)))
	return J

def groupSymb(chord_list, beg, end):
	to_remove = []
	i = 0
	while i < len(chord_list)-1:
		if chord_list[i] == beg and chord_list[i+1] == end:
			chord_list[i] = beg + "_" + end
			to_remove.insert(0,i+1)
			i = i+2
		else:
			i = i+1
	for elem in to_remove:
		chord_list.pop(elem)
	return chord_list

def replaceSymb(chord_list, symb, eq_symb):
	for i in range(len(chord_list)):
		if chord_list[i] == symb:
			chord_list[i] = eq_symb
	return chord_list

def searchSimSymb(new_symb, same_len, bigram_list, J, voc):
	eq_symb = None
	for symb in same_len:
		if eq_symb == None:
			sim = 0
			for elem in voc:
				Jua = J[bigram_list.index((elem, new_symb))]
				Jub = J[bigram_list.index((elem, symb))]
				Jav = J[bigram_list.index((new_symb, elem))]
				Jbv = J[bigram_list.index((symb, elem))]
				sim = sim + ((Jua - Jub)**2) + ((Jav - Jbv)**2)
			sim = sim/(1.*len(voc))
			if sim < 0.3:
				eq_symb = symb
	return eq_symb

if __name__ == '__main__': main()
