import xml.etree.ElementTree as ET
import os
import sys
import random
import numpy as np

import MusicXML as Mxl
import converter as cv

XML_DIR = "xml_parser"
TARGET_DIR = "output"

ATTACK = 61
SILENCE = 60
NO_OCTAVE = 6

def getDirectory():
    return os.path.dirname(__file__)

def getRoot():
    """
    Get project's path.

    Returns
    -------
    y:      string
            Path of the project.
    """
    return os.path.dirname(os.path.dirname(__file__))

def getPath(_dir, _file):
    """
    Return the path of a file in a certain directory.

    Parameters
    ----------
    _dir:   string
            Directory where the file is. (The Directory is a children
            of this project directory)

    _file:  string
            File's name.

    Returns
    -------
    y:      string
            Path leading to the file.
    """
    return os.path.join(getRoot(), _dir, _file)

def xml_harmony_parser(file_name):
    """
    Parsing a file, in MusicXML format.

    Parameters
    ----------
    file_name:  string
                The file to be parsed.

    Returns
    -------
    notes_list:  XmlNote[][]
                List of notes of each part which make up the score.
    """

    #print "PARSING FILE : ", file_name
    try:
        tree = ET.parse(file_name)
    except ET.ParseError as err:
        print(err)
        print "This file must be deleted : {}".format(file_name)
        sys.exit(2)
    root = tree.getroot()

    # Notes attributes
    note_step      = None
    note_alter     = None
    note_octave    = None
    note_duration  = None
    note_timestamp = None

    # List of chords and notes
    chord_list = []
    notes_list  = []

    global_clock   = 0	# initialise clock to 0
    global_tied    = 0	# boolean to create only one note when there are tied notes

    parts = []
    for child in root:
        if child.tag == "part":
            parts.append(child)

    for part in parts:
        global_clock = 0
        global_tied = 0
        note_list = []
        measures = part.getchildren()		# returns list of measures (bars)
        for measure in measures:
            for event in measure:		# each event can correspond to a score, note, or chord attribute

            	# getting note attributes
                if event.tag == "note":
                    if event.find("pitch") != None:		
                    # if there's a pitch, it's a note
                        note_step = event.find("pitch").findtext("step")
                        note_alter = event.find("pitch").findtext("alter")
                        if note_alter == None:		# if alter in not indicated, there's no alteration and we consider the value 0
                        	note_alter = 0
                        note_alter = int(note_alter)
                        note_octave = int(event.find("pitch").findtext("octave"))
                        note_duration = int(event.findtext("duration"))

                        # Unification with the previous note if they are tied
                        if event.find("notations") != None:
                        	global_tied = global_tied + len(event.find("notations").findall("tied"))
                        if global_tied >= 2:	#if this note is tied to the previous one, we don't create a new note but add its duration to the previous one
                        	global_tied = global_tied - 2
                        	note_list[-1].setDuration(note_list[-1].duration + note_duration)
                        else:	#if the note isn't tied we add it to the list
                        	new_note = Mxl.XmlNote(note_step, note_alter, note_octave, note_duration)
                        	new_note.setTimestamp(global_clock)
                        	note_list.append(new_note)
                    else:
                    # if there's no pitch, it's a rest
                        note_step = "Rest"
                        note_alter = None
                        note_octave = None
                        note_duration = int(event.findtext("duration"))

                        # Unification with the previous rest if previous note was also a rest
                        #if note_list !=[] and note_list[-1].step == "Rest":
                        #	note_list[-1].setDuration(note_list[-1].duration + note_duration)
                        #else :
                        new_note = Mxl.XmlNote(note_step, note_alter, note_octave, note_duration)
                        new_note.setTimestamp(global_clock)
                        note_list.append(new_note)

                	global_clock = global_clock + note_duration

        notes_list.append(note_list)
    #print len(notes_list)
    return notes_list

def xml_parser(file_name):
    """
    Parsing a file, in MusicXML format.

    Parameters
    ----------
    file_name:  string
                The file to be parsed.

    Returns
    -------
    score_info: XmlScore
                Main score's attributes.

    chord_list: XmlHarmony[]
                List of the score's harmony (chord).

    note_list:  XmlNote[]
                List of notes which make up the score.
    """

    #print "PARSING FILE : ", file_name
    try:
        tree = ET.parse(file_name)
    except ET.ParseError as err:
        print(err)
        print "This file must be deleted : {}".format(file_name)
        sys.exit(2)
    root = tree.getroot()

    # Score attributes
    divisions  = None
    beats      = None
    beat_type  = None
    key        = None

    # Chords attributes
    chord_root_step    = None
    chord_root_alter   = None
    chord_kind         = None
    chord_duration     = None
    chord_timestamp    = None

    # Notes attributes
    note_step      = None
    note_alter     = None
    note_octave    = None
    note_duration  = None
    note_timestamp = None

    # List of chords and notes
    chord_list = []
    note_list  = []

    global_clock   = 0  # initialise clock to 0
    global_tied    = 0  # boolean to create only one note when there are tied notes

    measures = root.find("part").getchildren()      # returns list of measures (bars)

    for measure in measures:
        for event in measure:       # each event can correspond to a score, note, or chord attribute
            # getting score attributes
            if event.tag == "attributes":
                if event.find("divisions") != None:
                    divisions = int(event.findtext("divisions"))
                if event.find("time") != None:
                    beats = int(event.find("time").findtext("beats"))
                    beat_type = int(event.find("time").findtext("beat-type"))
                if event.find("key") != None:
                    key = int(event.find("key").findtext("fifths"))
                score_info = Mxl.XmlScore(divisions, beats, beat_type, key)

            # getting chord attributes
            if event.tag == "harmony":
                if event.find("root") != None:
                    chord_root_step = event.find("root").findtext("root-step")
                    chord_root_alter = event.find("root").findtext("root-alter")
                    if chord_root_alter == None:    # if alter is not indicated, there's no alteration and we consider the value 0
                        chord_root_alter = 0
                    chord_root_alter = int(chord_root_alter)
                    chord_kind = event.findtext("kind")

                    new_chord = Mxl.XmlHarmony(chord_root_step, chord_root_alter, chord_kind)
                    new_chord.setTimestamp(global_clock)
                    chord_list.append(new_chord)    # adding the chord to the list of chords

            # getting note attributes
            if event.tag == "note":
                if event.find("pitch") != None:     # if there's a pitch, it's a note
                    note_step = event.find("pitch").findtext("step")
                    note_alter = event.find("pitch").findtext("alter")
                    if note_alter == None:      # if alter in not indicated, there's no alteration and we consider the value 0
                        note_alter = 0
                    note_alter = int(note_alter)
                    note_octave = int(event.find("pitch").findtext("octave"))
                    note_duration = int(event.findtext("duration"))

                    # Unification with the previous note if they are tied
                    if event.find("notations") != None:
                        global_tied = global_tied + len(event.find("notations").findall("tied"))
                    if global_tied >= 2:    #if this note is tied to the previous one, we don't create a new note but add its duration to the previous one
                        global_tied = global_tied - 2
                        note_list[-1].setDuration(note_list[-1].duration + note_duration)
                    else:   #if the note isn't tied we add it to the list
                        new_note = Mxl.XmlNote(note_step, note_alter, note_octave, note_duration)
                        new_note.setTimestamp(global_clock)
                        note_list.append(new_note)
                else:   # if there's no pitch, it's a rest
                    note_step = "Rest"
                    note_alter = None
                    note_octave = None
                    note_duration = int(event.findtext("duration"))

                    # Unification with the previous rest if previous note was also a rest
                    #if note_list !=[] and note_list[-1].step == "Rest":
                    #   note_list[-1].setDuration(note_list[-1].duration + note_duration)
                    #else :
                    new_note = Mxl.XmlNote(note_step, note_alter, note_octave, note_duration)
                    new_note.setTimestamp(global_clock)
                    note_list.append(new_note)

                global_clock = global_clock + note_duration

    return (score_info, chord_list, note_list)

def back2xml(score_info, note_list):
    """
    Create a MusicXML file for the improvisation.

    Parameters
    ----------
    score_info: XmlScore
                Main score's attributes to generate header.

    note_list:  XmlNote[]
                List of the notes which make up the score.

    Returns
    -------
    y:  int
        0 and the file is correctly set up.
    """
    impro_file  = getPath(TARGET_DIR, "impro.xml")
    n = 0
    while os.path.isfile(impro_file):
    	impro_file = getPath(TARGET_DIR, "impro%i.xml"%n)
    	n += 1
    with open(impro_file, "wb") as my_file:
        # Header
        path_header = getPath(XML_DIR, "xml_header_light.xml")
        my_file.write(score_info.printPath(path_header))

        # First measures with attributes
        path_fm     = getPath(XML_DIR, "xml_attributes.xml")
        my_file.write(score_info.printFirstMeasure(path_fm))

        # Notes
        i = 2
        global_time     = (60.0 / float(score_info.per_minute)) * 60
        temp_measure    = Mxl.XmlMeasure(i, global_time)
        measures        = []
        for note in note_list:
            possible = temp_measure.appendNote(note)
            if not possible:
                my_file.write(str(temp_measure))
                i+=1
                temp_measure = Mxl.XmlMeasure(i, global_time)
                temp_measure.appendNote(note)
        my_file.write(str(temp_measure))

        # Footer
        footer = getPath(XML_DIR, "xml_footer.xml")
        my_file.write(score_info.printPath(footer))

        my_file.close()
    return 0

def improv2OM(score_info, improv):
    pitches_list = []
    onsets_list = []
    durations_list = []

    divisions = score_info.divisions
    clock = 0

    for note in improv:
    	duration = int(round((note.duration/(1.0*divisions))*1000))	# Convert musicXML duration into milliseconds

    	if(note.step != 'Rest'):
    		pitch = (note.toInt() + note.alter + (note.octave+1)*12)*100	# Convert musicXML data into midi pitch (*100 for OM)
    		pitches_list.append(pitch)
    		onsets_list.append(clock)
    		durations_list.append(duration)

    	clock = clock + duration

    # Text file editing. Creates 3 lists between parenthesis : list of pitches, list of onsets and list of durations
    txt_path = getPath(TARGET_DIR, "improv.txt")
    txt_file = open(txt_path, 'w')
    txt_file.write('( ')
    for pitch in pitches_list:
    	txt_file.write(str(pitch)+' ')
    txt_file.write(')\n( ')
    for onset in onsets_list:
    	txt_file.write(str(onset)+' ')
    txt_file.write(')\n( ')
    for duration in durations_list:
    	txt_file.write(str(duration)+' ')
    txt_file.write(')')
    txt_file.close()

    return 0

def xml_sort(file):
    #print "[INFO] CHECKING FILE : {}".format(file)
    basename = os.path.basename(file)
    if basename.split('.')[0][-2:] == "_h":
        return 0
    harmony_file = file
    try:
        tree = ET.parse(file)
    except:
        print "[WARNING] DELETE FILE :{}".format(file)
        print "[INFO] Reason : Misformed"
        os.remove(file)
        try:
            os.remove(harmony_file.replace("_m", "_h"))
        finally:
            return 0
    root = tree.getroot()

    try:
        measures = root.find("part").getchildren()      # returns list of measures (bars)
    except:
        print "[WARNING] DELETE FILE :{}".format(file)
        print "[INFO] Reason : No Part"
        os.remove(file)
        try:
            os.remove(harmony_file.replace("_m", "_h"))
        finally:
            return 0

    n_notes = 0
    tab_pitch = []
    for measure in measures:
        for event in measure:

            # There are two portee
            if event.tag == "attributes":
                if event.find("clef") != None:
                    if event.find("clef").get("number") >= '2':
                        print "[WARNING] File Deleted :{}".format(file)
                        print "[INFO] Reason : There are 2 keys"
                        os.remove(file)
                        try:
                            os.remove(harmony_file.replace("_m", "_h"))
                        finally:
                            return 0

            if event.tag == "note":
                n_notes += 1
                if event.find("pitch") != None:
                    pitch = str(event.find("pitch").findtext("step"))
                    alter = "None"
                    if event.find("pitch").find("alter") != None:
                        alter = str(event.find("pitch").findtext("alter"))
                    octave = str(event.find('pitch').findtext('octave'))
                    tab_pitch.append("".join([str(pitch), str(alter)]))
                    # There an note below the first octave or above the seventh one
                    if int(octave) < 1 or int(octave) > 7:
                        print "[WARNING] DELETE FILE :{}".format(file)
                        print "[INFO] Reason : Octave {}".format(int(octave))
                        os.remove(file)
                        try:
                            os.remove(harmony_file.replace("_m", "_h"))
                        finally:
                            return 0

    if n_notes > 30 and len(set(tab_pitch)) >= 6:
        return 0
    else:
        print "[WARNING] DELETE FILE :{}".format(file)
        print "[INFO] Reason : Notes numbers {} or Differents notes {}".format(n_notes, len(set(tab_pitch)))
        os.remove(file)
        try:
            os.remove(harmony_file.replace("_m", "_h"))
        finally:
            return 0

def perf_measure(pred, real, num_labels=2):
    """
    Calculate Confusion Matrix.

    Parameters
    ----------
    pred:   Array of int
            Range 0..num_labems. Predicted values

    real:   Array of int (0 or 1)
            Range 0..num_labels. Real values

    Returns
    -------
    matrix: dictionary
            Confusion matrix for multi-class.
    """
    #assert len(real) == len(pred), "Dimension does not match between Real and Predicted!"
    matrix = np.zeros((num_labels, num_labels))
    for i in range(num_labels):
        for j in range(num_labels):
            matrix[i][j] = sum((real == i) & (pred == j))
        #assert matrix == sum((real==i))
    print matrix
    return matrix

def metrics(dico, num_labels=2):
    """
    Get metrics from a confused matrix.

    Parameters
    ----------
    dico:   dictionary
            Dict with TP, FP, TN and FN

    Returns
    -------
    accuracy:   float
                Accuracy

    precision:  dict
                Precision for each class.

    recall: dict
            Recall for each class.

    specificity:    dict
                    Specificity for each class.

    npv:    dict
            Negativ predicted value for each class.
    """
    FN = np.zeros((num_labels))
    TP = np.zeros((num_labels))
    TN = np.zeros((num_labels))
    FP = np.zeros((num_labels))
    Total = dico.sum()
    rows = dico.sum(axis=1)
    columns = dico.sum(axis=0)
    for i in range(num_labels):
        FP[i] = columns[i] - dico[i][i]
        FN[i] = rows[i] - dico[i][i]
        TP[i] = dico[i][i]
        TN[i] = Total - TP[i] - FN[i] - FP[i]

    precision   = dict()
    recall      = dict()
    specificity = dict()
    npv         = dict()
    #accuracy   = dict()
    for i in range(num_labels):
        precision[i]    = float(TP[i]) / (columns[i])
        recall[i]       = float(TP[i]) / (rows[i])
        specificity[i]  = float(TN[i]) / (TN[i] + FP[i])
        npv[i]          = float(TN[i]) / (TN[i] + FN[i])
    accuracy = float(sum(TP)) / Total

    # Precision
    #prec = float(dico['TP']) / (float(dico['FP']) + float(dico['TP']))
    # Recall
    #recall = float(dico['TP']) / (float(dico['TP']) + float(dico['FN']))
    # Accuracy
    #acc = float(dico['TP']+dico['TN']) / float(dico['TP']+dico['TN']+dico['FN']+dico['FP'])

    return accuracy, precision, recall, specificity, npv


def xml_melody_length(file_name):
    """
    Parsing a file, in MusicXML format.

    Parameters
    ----------
    file_name:  string
                The file to be parsed.

    Returns
    -------
    notes_list:  XmlNote[][]
                List of notes of each part which make up the score.
    """

    #print "PARSING FILE : ", file_name
    try:
        tree = ET.parse(file_name)
    except ET.ParseError as err:
        print(err)
        print "This file must be deleted : {}".format(file_name)
        sys.exit(2)
    root = tree.getroot()

    note = 0
    parts = []
    for child in root:
        if child.tag == "part":
            parts.append(child)
    for part in parts:
        measures = part.getchildren()       # returns list of measures (bars)
        for measure in measures:
            for event in measure:       # each event can correspond to a score, note, or chord attribute
                # getting note attributes
                if event.tag == "note":
                    note += 1

    note = float(note) / float(len(parts))
    print file_name, "has : ", note, " notes."
    return note