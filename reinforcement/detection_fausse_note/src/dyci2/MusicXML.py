REST    = "Rest"
FLAT    = "flat"
SHARP   = "sharp"
XML_DIR = "xml_parser"
TARGET_DIR = "output"

import os
from string import Template
import utils
import numpy as np

class XmlAbstractNote():
    """
    XmlAbstractNote share common attributs between XmlHarmony and XmlNote, the basics
    in MusicXML format.
    """

    def __init__(self, step, alter):
        self.step   = step
        self.alter  = alter
        self.type   = "quarter"

    def setTimestamp(self, time):
        self.timestamp = time

    def toInt(self):
        """
        Convert a step to int.

        Parameters
        ----------
        step:   string
                Step/note to convert.
        Returns
        -------
        y:      int
                Integer corresponding to the step/note.
        """
        if self.step == 'C':
        	return 0
        elif self.step =='D':
        	return 2
        elif self.step == 'E':
        	return 4
        elif self.step == 'F':
        	return 5
        elif self.step == 'G':
        	return 7
        elif self.step == 'A':
        	return 9
        elif self.step == 'B':
        	return 11

    def setType(self, timer):
        measure_time = ((60.0 / timer) * 60.0) * 4.0
        x = self.duration / measure_time
        #self.type = utils.toType(x)

    def step_from_int(self, n):
        self.step = 0
        if n==0:
            self.step = 'C'
        elif n==1:
            self.step = 'C'
            self.alter = 1
        elif n==2:
            self.step = 'D'
        elif n==3:
            self.step = 'D'
            self.alter = 1
        elif n==4:
            self.step = 'E'
        elif n==5:
            self.step = 'F'
        elif n==6:
            self.step = 'F'
            self.alter = 1
        elif n==7:
            self.step = 'G'
        elif n==8:
            self.step = 'G'
            self.alter = 1
        elif n==9:
            self.step = 'A'
        elif n==10:
            self.step = 'A'
            self.alter = 1
        elif n==11:
            self.step = 'B'
        else:
            self.step = REST

class XmlHarmony(XmlAbstractNote):
    """
    Define what is a harmony in MusicXML format.
    """

    def __init__(self, step, alter, kind):
        XmlAbstractNote.__init__(self, step, alter)
        self.kind = kind

    def __str__(self):
        path    = utils .getPath(XML_DIR, "xml_harmony.xml")
        self.setType(220.0)
        return Template(open(path, "r").read()).substitue(self.__dict__)

    def toLabel(self):
        return [(self.toInt() + self.alter ) % 12, self.kind]

class XmlNote(XmlAbstractNote):
    """
    Define what is a note in MusicXML format.
    """

    def __init__(self, step, alter, octave, duration, timestamp=None):
        XmlAbstractNote.__init__(self, step, alter)
        self.octave     = octave
        self.duration   = duration

    def __str__(self):
        """
        Display note as define in xml_note.xml
        """
        if self.step == REST:
            xml = "xml_rest.xml"
        else:
            xml = "xml_note.xml"
        path = utils .getPath(XML_DIR, xml)
        accidental = FLAT if self.alter == -1 else SHARP
        _dict = self.__dict__
        _dict['accident'] = accidental
        self.setType(220.0)
        return Template(open(path, "r").read()).substitute(_dict)


    def setDuration(self, duration):
        self.duration   = duration

    def octave_from_int(self, n):
        self.octave = n

    def duration_from_int(self, n, kappa=1):
        self.duration = n * kappa

    def toLabel(self):
        """
        Convert note to label.
        Rest is equal to -1. Others are : 0 for C, 1 for C# and so on.

        Parameters
        ----------
        note:   XmlNote
                Note to be converted.

        Returns
        -------
        y:      list
                (List composed of) Value related to the note.
        """
        if self.step == REST:
            return [-1]
        else:
            return[(self.toInt()+self.alter)%12]

    def octave2Label(self):
        if self.step == REST:
            return -1
        else:
            return self.octave

    def asInput(self, pitch_size, octave_size, kappa, j, threshhold, window):
        """
        Create note as an input for the neural network.

        Parameters
        ----------
        Look at rhythm2Array, octave2Array and step2Array.

        Returns
        -------
        y:      array
                Returns an array of inputs (because a note can take more than 1 array to be described)

        window: array
                Returns array of differents attacks in a quarter note in which the note is.

        j:      int
                Index for the next note's attack.
        """
        y = np.zeros(None)
        temp = np.zeros(None)
        temp = np.append(temp, self.step2Array(pitch_size))
        temp = np.append(temp, self.octave2Array(octave_size))
        window, j = self.rhythm2Array(kappa, j, threshhold, window)
        temp = np.append(temp, window)
        y = np.append(y, temp)
        while j > threshhold:
            temp = np.zeros(None)
            temp = np.append(temp, self.step2Array(pitch_size))
            temp = np.append(temp, self.octave2Array(octave_size))
            temp = np.append(temp, np.zeros(window.shape))
            window = np.zeros(window.shape)
            y = np.append(y, temp)
            j = j - threshhold
        return y, window, j

class XmlMeasure():
    """
    Define what a measure is in MusicXML format
    """

    def __init__(self, number, time):
        self.number         = number
        self.composition    = []
        self.currentTime    = 0
        self.timelast       = time

    def appendNote(self, note):
        """
        Append a note to the measure.

        Parameters
        ----------
        note:   XmlAbstractNote
                Input note

        Returns
        -------
        y:      boolean
                False if could not append the note, True otherwise.
        """
        if isinstance(note, XmlNote):
            if note.step != REST:
                if self.currentTime <= self.timelast :
                    self.composition.append(note)
                    self.currentTime += note.duration
                else:
                    return False
            else:
                self.composition.append(note)
        if isinstance(note, XmlHarmony):
            self.composition.append(note)
        return True

    def __str__(self):
        res = []
        res.append("\t<measure number=\"{number}\">\n".format(number=self.number))
        for note in self.composition:
            res.append(str(note))
        res.append("\t</measure>\n")
        return "".join(res)

class XmlScore():

    def __init__(self, divisions, beats, beat_type, key):
        self.divisions  = divisions # number of division (based on tatum) in a quarter note
        self.beats      = beats     # time signature numerator
        self.beat_type  = beat_type # time signature denominator
        self.key        = key
        self.measures   = []
        self.beat_unit  = "quarter"
        self.per_minute = 180.0

    def setPerMinute(self, minute):
        self.per_minute = minute

    def printFirstMeasure(self, path):
        """
        Print the first measure of the score. This measure includes some additionnal
        attributes like divisions, key, beats, beat_type, or beat_per_minute

        Parameters
        ----------
        path:   string
                The path leading to the template to fill

        Returns
        -------
        y:      string
                The template filled.
        """

        dico    = {
            'divisions' : self.divisions,
            'key'       : self.key,
            'beats'     : self.beats,
            'beat_type' : self.beat_type,
            'per_minute': self.per_minute
        }
        return Template(open(path, 'r').read()).substitute(dico)

    def printPath(self, path):
        """
        Print file given by the path.

        Parameters
        ----------
        path:   string
                Path leading to the file to print.

        Returns
        -------
        y:      string
                The file read
        """
        try:
            my_file = open(path, "r")
            res     = my_file.read()
        finally:
            my_file.close()
        return res

    def __str__(self):
        return ""

def allModulationBigram(bigram_list):
	temp = []
	for bigram in bigram_list:
		for i in range(12):
			if bigram[0][0] == -1:
				ev = [-1]
			else:
				ev = [(bigram[0][0]+i)%12]
			if bigram[1] == -1:
				co = [-1]
			else:
				co = [(bigram[1][0]+i)%12]
			temp.append([ev,co])
	return temp
