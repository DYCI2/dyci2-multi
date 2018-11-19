# Reinforcement learning for automatic music improvisation

This project aims at using neural networks able to detect mistakes (wrong notes) in a musical sequence.

Authors: Rémi Decelle, Ken Déguernel
Supervisors: Ken Déguernel, Nathan Libermann, Emmanuel Vincent

## CONTENTS

1. [SET UP]
2. [OPTIONS LIST]
3. [FOLDERS]
4. [FILES]

### SET UP
#### Step 1 : Requirements

* [Python (version 2.7.+)] (https://www.python.org/downloads/)
* [Tensorflow (version 1.+)] (https://www.tensorflow.org/install/)
    
 
#### Step 2 (optional) 

To create data set, these can be used:

* SHELL (BASH)
* [MIDICSV / CSVMIDI] (http://www.fourmilab.ch/webtools/midicsv/)
* [Musescore 2.+] (https://musescore.org/fr)

#### Step 3 (optional)

To display ROC curve and compute the associated AUC:

* [Sklearn](http://scikit-learn.org/stable/install.html)

#### Step 4

At the project's root, the neural network is trained using the command:

```python
python ./src/dyci2/__main__.py --run
``` 

### OPTIONS LIST

There are several possible commands to call the file **__main__.py**.

**Command call** | **Description** | **Argument(s)** |
:---:| :---: | :---:
**Main commands** | |
--run | builds a neural network | None
--eval | evaluates a neural network | Model number
--debug | code debugging | None
**Optional commands** | |
--len | returns the number of elements in the dataset | file/folder path
--sort | sorts the dataset | file/folder path
--generate | modify an .xml file, randomising some notes | file/folder path
**Old commands** |
--zip | archives a dataset (hexadecimal format). | file/folder path
--unzip | uncompresses an archive | file/folder path

### FOLDERS
* extract_melody/
    > contains the files to extract the melody and harmony of a midi file.
    
* src/
    * data/
        > contains the datasets.
        
    * dyci2/
        > contains the python files.
        
    * logs/
        > contains the save files and other files created when building a model.
        
        * save/
            > contains the models save file.
            
        * train/ valid/ test/
            > contains the Tensorboard visualisation files.
            
        * config/
            > contains the models config files.
            
    * omnibook/
        > contains Charlie Parker's improvisations.
        
    * oracle/
        > contains the automatic improvisation generation python files.
        
    * output/
        > contains the generated improvisation.
        
    * proba_model/
        > contains the .xml files to build the probabilistic models.
        
    * xml_parser/
        > contains the scripts to parse .xml files.
     

### FILES

| **File name** | **Main use** | **Work (mainly) with**
| :---: | :---: | :---:
| **Neural network files** | |
| dyci2.py  | contains the hyperparameters and the training loop. Also contains other functions according to the different commands | model.py, Dataset.py, utils.py
| model.py  | contains the neural network models | 
| utils.py  | contains .xml file parsing and criteria computation (accuracy, ...)  | MusicXML.py, converter.py
| rng.py  | contains the random change functions |
| converter.py  | contains the functions converting musicXml into a vector | MusicXML.py
| Dataset.py    | contains the fuctions converting .xml file into input vectors | converter.py, utils.py, rng.py
| MusicXML.py   | contains the classes representing musical information |
| \_\_main\_\_.py   | contains arguments parsing | dyci2.py
| **Tensorboard visualisation** | |
| show.sh | takes as argument the model to visualise (int)| 
| **Melody/harmony extraction** | |
| getTracks.sh | Iteration of the extraction on a file | extract_melody.sh, removeTracks.py
| removeTracks.py | takes a CSV file and remove a track number given as argument | getTracks.sh
| **Oracle files** | |
| oracle.py | contains the functions generating improvisations | proba.py
| proba.py  | contains the classes for probabilistic models |
| run_oracle.py | creates an improvisation | oracle.py
| config.py | contains the oracle parameters |
| **Old files** | |
| compress.py   | archives vectors in hexadecimal format | utils.py, converter.py, MusicXML.py
| extract.py    | unarchives files archives with the compress file | utils.py, converter.py, MusicXML.py
