#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##    ## ##    ## ##    ##
######## ######## ########
###   Ken  Deguernel   ###
######## ######## ########
###   Inria  (Nancy)   ###
###   Ircam  (Paris)   ###
######## ######## ########

import random
import sys

def main():

	rc_l = []
	k =0
	
	file = open('anatole.txt','w')
	while k <2000:
		rc = generate_RC()
		if rc not in rc_l:
			k = k+1
			rc_l.append(rc)

#			chart =rc.split()
#
#			j = 0
#			for i in range(len(chart)):
#				sys.stdout.write(chart[i] + ' ')
#				if i%2==1:
#					j = j+1
#					if j==4:
#						print ''
#						j=0
#					else:
#						sys.stdout.write('| ')
#
#			print ''
#			print '######## ######## ########'
#			print ''

			file.write(rc+' ')
	file.close()

def generate_RC():
	
	res = "__START__ " + generate_A1() + generate_A2() + generate_B() + generate_A() + "__END__"
	return res

def generate_A():
	x = random.random()	
	if x < 0.5:
		return generate_A1()
	else:
		return generate_A2()

def generate_A1():
	tau = ['I I I I II- II- V7 V7 ', 'III- III- bIII7 bIII7 II- II- V7 V7 ', 'III- III- VI7 VI7 II- II- V7 V7 ', 'I I VI7 VI7 II- II- V7 V7 ']

	tau_1 = ['I I I I II- II- V7 V7 ', 'I I VI7 VI7 II- II- V7 V7 ']

	sigma = ['V- V- I7 I7 IV7 IV7 IV7 IV7 ', 'I7 I7 I7 I7 IV IV bVII7 bVII7 ', 'I7 I7 I7 I7 IV IV IV IV ', 'I7 I7 I7 I7 IV IV IV- IV- ', 'I7 I7 I7 I7 IV7 IV7 IV7 IV7 ', 'I7 I7 I7 I7 IV7 IV7 #IVo #IVo ', 'V- V- I7 I7 IV IV IV IV ', 'I I I7 I7 IV IV #IVo #IVo ', 'V- V- I7 I7 IV7 IV7 IV7 IV7 ', 'V- V- I7 I7 IV IV #IVo #IVo ', 'V- V- I7 I7 IV IV bVII7 bVII7 ', 'V- V- I7 I7 IV IV IV- IV- ', 'V- V- I7 I7 IV7 IV7 IV- IV- ']

	return random.choice(tau_1) + random.choice(tau) + random.choice(sigma) + random.choice(tau)

def generate_A2():
	tau = ['I I I I II- II- V7 V7 ', 'III- III- bIII7 bIII7 II- II- V7 V7 ', 'III- III- VI7 VI7 II- II- V7 V7 ', 'I I VI7 VI7 II- II- V7 V7 ']
	
	tau_1 = ['I I I I II- II- V7 V7 ', 'I I VI7 VI7 II- II- V7 V7 ']

	sigma = ['V- V- I7 I7 IV7 IV7 IV7 IV7 ', 'I7 I7 I7 I7 IV IV bVII7 bVII7 ', 'I7 I7 I7 I7 IV IV IV IV ', 'I7 I7 I7 I7 IV IV IV- IV- ', 'I7 I7 I7 I7 IV7 IV7 IV7 IV7 ', 'I7 I7 I7 I7 IV7 IV7 #IVo #IVo ', 'V- V- I7 I7 IV IV IV IV ', 'I I I7 I7 IV IV #IVo #IVo ', 'V- V- I7 I7 IV7 IV7 IV7 IV7 ', 'V- V- I7 I7 IV IV #IVo #IVo ', 'V- V- I7 I7 IV IV bVII7 bVII7 ', 'V- V- I7 I7 IV IV IV- IV- ', 'V- V- I7 I7 IV7 IV7 IV- IV- ']

	omega = ['I I I I I I I I ', 'II- II- V7 V7 I I I I ', 'I I VI7 VI7 II- II- V7 V7 ']

	return random.choice(tau_1) + random.choice(tau) + random.choice(sigma) + random.choice(omega)

def generate_B():
	
	delta_3 = ['III7 III7 III7 III7 III7 III7 III7 III7 ', 'VII- VII- VII- VII- III7 III7 III7 III7 ']
	delta_6 = ['VI7 VI7 VI7 VI7 VI7 VI7 VI7 VI7 ', 'III- III- III- III- VI7 VI7 VI7 VI7 ']
	delta_2 = ['II7 II7 II7 II7 II7 II7 II7 II7 ', 'VI- VI- VI- VI- II7 II7 II7 II7 ']
	delta_5 = ['V7 V7 V7 V7 V7 V7 V7 V7 ', 'II- II- II- II- V7 V7 V7 V7 ']

	return random.choice(delta_3) + random.choice(delta_6) + random.choice(delta_2) + random.choice(delta_5)

######## ######## ########

if __name__ == '__main__': main()
