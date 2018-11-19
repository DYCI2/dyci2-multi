import sys
import getopt
import dyci2

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["debug", "eval=", "generate=", "run", "sort=", "unzip=", "zip=" , "--textfile", "len="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    sys.exit(2)

with_txt_file = False
for opt, arg in opts:
	texting = arg in ("--textfile")
	if texting :
		with_txt_file = True

for opt, arg in opts:
	debugging 	= opt in ("--debug")
	evaluating	= opt in ("--eval")
	generating 	= opt in ("--generate")
	running		= opt in ("--run")
	zipping		= opt in ("--zip")
	unzipping	= opt in ("--unzip")
	sorting 	= opt in ("--sort")	
	lengthing	= opt in ("--len")
	if debugging:
		print "Debugging Mode"
		dyci2.debug()
	elif evaluating:
		print "Evaluation Mode"
		print arg
		dyci2.evaluate(arg.split(" ")[0],arg.split(" ")[1])
	elif generating:
		print "Random Note Generator Activated"
		dyci2.random(arg)
	elif running:
		print "Running Mode"
		dyci2.run()
	elif zipping:
		print "Compressing Mode"
		dyci2.zip(arg, with_txt_file)
	elif unzipping:
		print "Uncompressing Mode"
		dyci2.unzip(arg)
	elif sorting:
		print "Sorting Mode"
		dyci2.sort(arg)
	elif lengthing:
		print "Melody length Mode"
		dyci2.melody_len(arg)
	else:
		string = (
			"Unhandled option {cmd}.\n"
			"Try one of these commands : \n"
			" --run\t:\tBuild a neural network\n"
			" --eval\t:\tEvaluate a neural network\n"
			" --debug:\tDebugging code\n"
			" --zip\t:\tCompress files. From .xml to .n2c format\n"
			" --unzip:\tUncompress files. From .n2c to .xml format\n"
			" --sort\t:\tDelete uninteresting files".format(cmd=opt)
			)
		assert False, string
