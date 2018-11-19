Author: Ken Déguernel
Supervisors: Emmanuel Vincent, Gérard Assayag

main.py: generates improvisation given a probabilistic model and factor oracle
oracle.py: classes corresponding to the factor oracle
proba.py: classes corresponding to probabilistic models
training.py: functions to train the probabilistic models
utils.py: parsers to convert xml and openmusic data
improv.txt: output file

xml_parser/: header and footer information for generation of xml files
data_save_classic/: save files for probabilistic models using a classical music corpus
data_save_omni/: save files for probabilistic models using the omnibook corpus
om_gen/: openmusic files to convert improvisation into a midi file.