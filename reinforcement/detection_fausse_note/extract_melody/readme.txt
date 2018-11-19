Use:
extract_melody.sh -input <midi file or folder> -output <output folder> [-poly2mono] [-suffix <output suffix>] [-skip <input suffix>] [-tagged]

where the optional parameters mean:
-poly2mono Transform in monophonic
-suffix Suffix to be added to the output file, it also filters the input files, any file with <input suffix> is not processed
-skip Skip files with this suffix
-tagged Try to retrieve the track named as melody (see Dictionary in FLAIRS'06 paper)

