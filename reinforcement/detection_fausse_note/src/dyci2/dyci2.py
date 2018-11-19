import numpy as np
import random
import tensorflow as tf
import tensorflow.contrib.layers as layers
import os
import sys
import time
import math

import utils
import converter as cv
import model
import compress
import extract
import rng
#import datas.datas as dataset
#import datas as sets
from datas.TrainingSet import TrainingSet
from datas.TestingSet import TestingSet
from datas.ValidationSet import ValidationSet

#from sklearn.metrics import roc_curve, auc
#import matplotlib.pyplot as plt
#from itertools import cycle

FLAGS = tf.flags.FLAGS

#-----------------------
#	DIRECTORIES FLAGS
#-----------------------
tf.flags.DEFINE_string("config_dir",
	"logs/config/",
	"Testing Files Directory.")

tf.flags.DEFINE_string("save_dir",
	"logs/save/",
	"Save Directory.")

tf.flags.DEFINE_string("logs_dir",
	"logs/",
	"Logs Directory.")

tf.flags.DEFINE_string("training_dir",
	"data/harmony/training/",
	"dataset.")

tf.flags.DEFINE_string("test_dir",
	"data/harmony/test/",
	"Directory for tests outputs.")

tf.flags.DEFINE_string("validation_dir",
	"data/harmony/valid/",
	"Validation dataset directory.")

#--------------------
#	HYPERPARAMETERS
#--------------------
tf.flags.DEFINE_float("learning_rate",
	0.002,
	"Learning Rate.")

tf.flags.DEFINE_float("momentum",
	0.9,
	"Learning Rate.")

tf.flags.DEFINE_integer("max_step",
	500,
	"Number of epochs/steps.")

tf.flags.DEFINE_integer("max_iter",
	10,
	"Number of iterations")

tf.flags.DEFINE_float("epsilon_max",
	5,
	"Number of maximum false notes in a sequence.")

tf.flags.DEFINE_float("epsilon_min",
	1,
	"Number of minimum false notes in a sequence.")

#--------------------
#	PARAMETERS
#--------------------
tf.flags.DEFINE_integer("output_size",
	2,
	"Output size.")

tf.flags.DEFINE_integer("note_size",
	cv.PITCH_SIZE + cv.OCTAVE_SIZE + cv.RHYTHM_SIZE + cv.HARMONY_SIZE,
	"Note size.")

tf.flags.DEFINE_integer("batch_size",
	240,
	"Batch size.")

tf.flags.DEFINE_integer("n_hidden",
	256,
	"Hidden layer num of features.")

tf.flags.DEFINE_integer("past_size",
	4,
	"Number of notes from past.")

tf.flags.DEFINE_integer("future_size",
	5,
	"Number of notes from future.")

tf.flags.DEFINE_integer("num_layers",
	2,
	"Num of hidden layers")

#--------------------
#	OTHERS FLAGS
#--------------------
tf.flags.DEFINE_string("train_dir",
	"train/",
	"Model name.")

tf.flags.DEFINE_integer("display_time",
	2000,
	"Time to display loss and accuracy.")

tf.flags.DEFINE_string("valid_dir",
	"valid/",
	"Valid dir name.")

tf.flags.DEFINE_string("test_wdir",
	"test/",
	"Test dir name.")

tf.flags.DEFINE_string("save",
	"model",
	"Model save name.")

#------------------
#	Main function
#------------------
def run():
	"""
	Function to run/build the neural network.
	Logs (for tensorboard) are stored in src/logs/
	A config file is created. It consists of how long it took, hyperparameters, and so on. (see end of the function).
	Parameters can be changed, see above.

	Parameters
	----------

	Returns
	-------
	"""

	# Build the model
	network 	= model.Model(
					n_inputs=FLAGS.note_size,
					n_outputs=FLAGS.output_size,
					n_hidden=FLAGS.n_hidden,
					n_step=FLAGS.future_size+FLAGS.past_size+1,
					num_layers=FLAGS.num_layers,
					lr=FLAGS.learning_rate,
					momentum=FLAGS.momentum,
					target_note=FLAGS.past_size-1,
					)

	# Initialize session and Tensorboard
	index = 1
	while os.path.isdir(os.path.join(utils.getPath(FLAGS.logs_dir, FLAGS.train_dir), str(index))):
		index += 1

	session = tf.Session()
	session.run(tf.global_variables_initializer())

	# Training Summary
	tf.summary.scalar("loss", network.ferror)

	tf.summary.scalar("Accuracy", network.faccuracy)
	summary_op 	= tf.summary.merge_all()
	writer_dir 	= os.path.join(utils.getPath(FLAGS.logs_dir, FLAGS.train_dir), str(index))
	os.makedirs(writer_dir)
	writer 		= tf.summary.FileWriter(writer_dir, graph=tf.get_default_graph())

	# Validation Summary
	summary_valid_op = tf.summary.merge_all()
	writer_dir = os.path.join(utils.getPath(FLAGS.logs_dir, FLAGS.valid_dir), str(index))
	os.makedirs(writer_dir)
	writer_valid = tf.summary.FileWriter(writer_dir, graph=tf.get_default_graph())

	# Testing Summary
	summary_test_op = tf.summary.merge_all()
	writer_dir = os.path.join(utils.getPath(FLAGS.logs_dir, FLAGS.test_wdir), str(index))
	os.makedirs(writer_dir)
	writer_test = tf.summary.FileWriter(writer_dir, graph=tf.get_default_graph())

	# Saving 
	writer_dir = os.path.join(utils.getRoot(), FLAGS.save_dir, str(index))
	os.makedirs(writer_dir)

	parameters = {
		"directory"		: FLAGS.validation_dir,
		"batch_size" 	: FLAGS.batch_size,
		"past"			: FLAGS.past_size,
		"future"		: FLAGS.future_size,
		"note_size" 	: FLAGS.note_size,
		"output_size" 	: FLAGS.output_size,
		"epsilon" 		: FLAGS.epsilon_min,
		"meaning" 		: True
	}
	# Pre-processing Dataset for Validation
	#validset = dataset.ValidSet(**parameters)
	validset = ValidationSet(**parameters)
	valid_x, valid_y = validset.next_batch(206)
	#valid_x_p, valid_y_p = validset.next_batch(40*FLAGS.batch_size, for_future=False)
	# Eval batch
	eval_x, eval_y = validset.eval_batch(206, for_future=True)
	tmp_x, tmp_y = validset.eval_batch(FLAGS.batch_size, for_future=False)

	del validset
	print "[INFO] Validation Dataset Created"

	# Pre-processing Dataset for Testing
	parameters["directory"] = FLAGS.test_dir
	#testset = dataset.TestSet(**parameters)
	testset = TestingSet(**parameters)
	test_x, test_y = testset.next_batch(206)
	#test_x_p, test_y_p = testset.next_batch(40*FLAGS.batch_size, for_future=False)
	del testset
	print "[INFO] Test Dataset Created"

	# Pre-processing Dataset for Training
	parameters["directory"] = FLAGS.training_dir
	parameters["epsilon"] = FLAGS.epsilon_max
	#sets = dataset.TrainSet(**parameters)
	trainset = TrainingSet(**parameters)
	print "[INFO] Training Dataset Created"
	batch_x, batch_y = trainset.next_batch()
	#---
	# It's high time we fed our model !
	#---
	start	= time.time()
	for step in xrange(FLAGS.max_step):
		for i in xrange(FLAGS.max_iter):
			# Feed the model
			summary, _ = network.feed(session, summary_op, batch_x, batch_y)

			# Write log
			writer.add_summary(summary, step*FLAGS.max_iter + i)

		batch_x, batch_y = trainset.next_transpositions_batch()

		# Validation
		summary_valid, _ = network.eval(session, summary_valid_op, valid_x, valid_y)

		# Write Log
		writer_valid.add_summary(summary_valid, step*FLAGS.max_iter)

		# Test the model
		summary_test, _ = network.eval(session, summary_test_op, test_x, test_y)

		# Write Log
		writer_test.add_summary(summary_test, step*FLAGS.max_iter)

		# Display accuracy and loss every 200 steps time
		print("Iterations 	: {}".format(step))
		if (step+1) % 10 == 0:
			trainset.epsilon = trainset.epsilon-2 if trainset.epsilon > 1 else 1
			saver = tf.train.Saver()
			#saver.save(session, utils.getPath(writer_dir, FLAGS.save + str(step*FLAGS.max_iter)))

	"""for step in xrange(FLAGS.max_step, 2*FLAGS.max_step):
		# Get next batch
		batch_x, batch_y = trainset.next_batch(for_future=False)

		# Feed the model
		summary, _ = network.feed_past(session, summary_op, batch_x, batch_y)

		# Write log
		writer.add_summary(summary, step)

		# Validation
		summary_valid, _ = network.eval_past(session, summary_valid_op, valid_x_p, valid_y_p)

		# Write Log
		writer_valid.add_summary(summary_valid, step)

		# Test the model
		summary_test, _ = network.eval_past(session, summary_test_op, test_x_p, test_y_p)

		# Write Log
		writer_test.add_summary(summary_test, step)

		# Display accuracy and loss every 200 steps time
		#if step % FLAGS.display_time == 0:
		#	print("Iterations 	: {}".format(step))"""
	# Save the model
	#writer_dir = os.path.join(utils.getRoot(), FLAGS.save_dir, str(index))
	#os.makedirs(writer_dir)
	saver = tf.train.Saver()
	saver.save(session, utils.getPath(writer_dir, FLAGS.save))

	end = time.time()
	predicted, real = network.test(session, eval_x, eval_y)
	dict_acc = utils.metrics(utils.perf_measure(predicted, real))
	print "On evaluation dataset"
	for x in dict_acc:
		print x

	predicted, real = network.test(session, valid_x, valid_y)
	dict_acc = utils.metrics(utils.perf_measure(predicted, real))
	print "On validation dataset"
	for x in dict_acc:
		print x

	# Write parameters and hyper-parameters into a file named output.txt
	with open(os.path.join(utils.getRoot(), FLAGS.config_dir, "".join([str(index),".txt"])), "wb") as config_file:
		config_file.write("Time 		: {}\n".format(end - start))
		config_file.write("Step 		: {}\n".format(FLAGS.max_step))
		config_file.write("LR 		: {}\n".format(FLAGS.learning_rate))
		config_file.write("Momentum 	: {}\n".format(FLAGS.momentum))
		config_file.write("Past Size 	: {}\n".format(FLAGS.past_size))
		config_file.write("Future Size 	: {}\n".format(FLAGS.future_size))
		config_file.write("Batch Size 	: {}\n".format(FLAGS.batch_size))
		config_file.write("Hidden Size 	: {}\n".format(FLAGS.n_hidden))
		config_file.write("M-epsilon	: {}\n".format(FLAGS.epsilon_max))
		config_file.write("m-Epsilon	: {}\n".format(FLAGS.epsilon_min))
		config_file.write("Rhythm Size 	: {}\n".format(cv.TOTAL_SIZE))
		config_file.write("Iter Size 	: {}\n".format(FLAGS.max_iter))
		config_file.write("Step Size 	: {}\n".format(FLAGS.max_step))
		config_file.write("Hasard 		: {}\n".format(0.5))

def debug():
	"""
	Function to debug model and dataset implemention.
	It run only one batch.
	No model or config file are created.

	Parameters
	----------

	Returns
	-------

	"""

	# Build the model
	network 	= model.Model(
					n_inputs=FLAGS.note_size,
					n_outputs=FLAGS.output_size,
					n_hidden=FLAGS.n_hidden,
					n_step=FLAGS.future_size+FLAGS.past_size+1,
					num_layers=FLAGS.num_layers,
					lr=FLAGS.learning_rate,
					momentum=FLAGS.momentum,
					target_note=FLAGS.past_size-1,
					)

	# Initialize session and Tensorboard
	session = tf.Session()
	session.run(tf.global_variables_initializer())

	parameters = {
		"directory"		: FLAGS.validation_dir,
		"batch_size" 	: FLAGS.batch_size,
		"past"			: FLAGS.past_size,
		"future"		: FLAGS.future_size,
		"note_size" 	: FLAGS.note_size,
		"output_size" 	: FLAGS.output_size,
		"epsilon" 		: FLAGS.epsilon_min,
		"meaning" 		: True
	}
	# Pre-processing Dataset for Validation
	#validset = dataset.ValidSet(**parameters)
	validset = ValidationSet(**parameters)
	#for note in validset.datas[0]:
	#	print note[0:14], note[-12:]
	valid_x, valid_y = validset.next_batch(2*FLAGS.batch_size)
	#valid_x_p, valid_y_p = validset.next_batch(FLAGS.batch_size, for_future=False)
	del validset
	print "[INFO] Validation Dataset Created"

	# Pre-processing Dataset for Testing
	parameters["directory"] = FLAGS.test_dir
	#testset = dataset.TestSet(**parameters)
	testset = TestingSet(**parameters)
	test_x, test_y = testset.next_transpositions_batch()
	del testset
	print "[INFO] Test Dataset Created"

	# Pre-processing Dataset for Training
	parameters["directory"] = FLAGS.training_dir
	parameters["epsilon"] = FLAGS.epsilon_max
	#sets = dataset.TrainSet(**parameters)
	trainset = TrainingSet(**parameters)
	print "[INFO] Training Dataset Created"

	# Debug session
	batch_x, batch_y = trainset.next_batch()
	network.debug(session, batch_x, batch_y)
	print "[INFO] Debugging batch done"
	network.debug(session, valid_x, valid_y)
	print "[INFO] Debugging valid done"
	network.debug(session, test_x, test_y)
	print "[INFO] Debugging test done"
	print "[INFO] Feeding Done"

	predicted, real = network.test(session, valid_x, valid_y)
	dict_acc = utils.metrics(utils.perf_measure(predicted, real))
	for x in dict_acc:
		print x

	# Write parameters and hyper-parameters into a file named output.txt
	with open(os.path.join(utils.getRoot(), FLAGS.config_dir, "".join(["debug",".txt"])), "wb") as debug_file:
		#debug_file.write("Time 		: {}\n".format(end - start))
		debug_file.write("Step 		: {}\n".format(FLAGS.max_step))
		debug_file.write("LR 		: {}\n".format(FLAGS.learning_rate))
		debug_file.write("Momentum 	: {}\n".format(FLAGS.momentum))
		debug_file.write("Past Size 	: {}\n".format(FLAGS.past_size))
		debug_file.write("Future Size 	: {}\n".format(FLAGS.future_size))
		debug_file.write("Batch Size 	: {}\n".format(FLAGS.batch_size))
		debug_file.write("Hidden Size 	: {}\n".format(FLAGS.n_hidden))
		debug_file.write("M-epsilon	: {}\n".format(FLAGS.epsilon_max))
		debug_file.write("m-Epsilon	: {}\n".format(FLAGS.epsilon_min))
		debug_file.write("Rhythm Size 	: {}\n\n".format(cv.TOTAL_SIZE))
		debug_file.write("Hasard 		: {}\n".format(0.5))

def evaluate(number, step):
	"""
	Function to evaluate a model.
	It returns (on standard output) precision, recall, ... (see utils module).
	It also gives the ROC and AUC for the model, if sklearn is imported.

	Parameters
	----------
	numbers:	int
			Number of the model. All models are stored in src/logs/save/[number]/

	step:		int
			Step iteration. Example : step=4500, model4500 will be evaluated.

	Returns
	-------		
	"""

	# Build the model
	network 	= model.Model(
					n_inputs=FLAGS.note_size,
					n_outputs=FLAGS.output_size,
					n_hidden=FLAGS.n_hidden,
					n_step=FLAGS.future_size+FLAGS.past_size+1,
					num_layers=FLAGS.num_layers,
					lr=FLAGS.learning_rate,
					momentum=FLAGS.momentum,
					target_note=FLAGS.past_size-1,
					)
	# Create session
	session = tf.Session()
	session.run(tf.global_variables_initializer())
	# Restore the model
	saver = tf.train.Saver()
	print number
	print os.path.join(utils.getRoot(), FLAGS.save_dir, str(number), FLAGS.save + str(step))
	saver.restore(session, os.path.join(utils.getRoot(), FLAGS.save_dir, str(number), FLAGS.save + str(step)))
	# Build dataset
	parameters = {
		"directory"		: FLAGS.validation_dir,
		"batch_size" 	: FLAGS.batch_size,
		"past"			: FLAGS.past_size,
		"future"		: FLAGS.future_size,
		"note_size" 	: FLAGS.note_size,
		"output_size" 	: FLAGS.output_size,
		"epsilon" 		: FLAGS.epsilon_min,
		"meaning" 		: True
	}
	validset = ValidationSet(**parameters)
	test_x, test_y = validset.next_batch(40*FLAGS.batch_size)
	test_x_p, test_y_p = validset.next_batch(40*FLAGS.batch_size, for_future=False)
	del validset
	# Evaluate model
	pred, real = network.test(session, test_x, test_y)
	#pred_tmp, real_tmp = network.test_past(session, test_x, test_y)
	#pred = np.append(pred, pred_tmp, axis=0)
	#real = np.append(real, real_tmp, axis=0)
	# Get metrics and print them
	dict_acc = utils.metrics(utils.perf_measure(pred, real))
	for x in dict_acc:
		print x
	# Get values for ROC
	test, score = network.roc(session, test_x, test_y)
	# Get ROC curves and AUCs
	fpr = dict()
	tpr = dict()
	roc_auc = dict()
	for i in range(FLAGS.output_size):
	    fpr[i], tpr[i], _ = roc_curve(score[:, i], test[:, i])
	    roc_auc[i] = auc(fpr[i], tpr[i])
	# Plot all ROC curves
	plt.figure()
	for i in range(FLAGS.output_size):
	    plt.plot(fpr[i], tpr[i],
	             label='ROC curve of class {0} (area = {1:0.2f})'
	             ''.format(i, roc_auc[i]))
	plt.plot([0, 1], [0, 1], 'k--')
	plt.xlim([0.0, 1.0])
	plt.ylim([0.0, 1.0])
	plt.xlabel('False Positive Rate')
	plt.ylabel('True Positive Rate')
	plt.title('Some extension of Receiver operating characteristic to multi-class')
	plt.legend(loc="lower right")
	plt.show()

def zip(arg, with_txt_file=False):
	"""
	Outdated.

	Compressed xml file to n2c file (hexadecimal file).
	More information is compress module.

	Parameters
	----------
	arg:	string
			File to be compressed.
			If it is a directory, all files will be compressed.

	with_txt_file:	bool
					If it is False, not txt file are required. (see compress.from_xml_to_n2c)
					If it is True, a txt file with wrong note index (coma-separated) is required.
					Txt file must have the same basename than arg's basename. (see compres.from_txt_to_n2c).
	"""
	if os.path.isdir(arg):
		for file in os.listdir(arg):
			temp = utils.getPath(arg, file)
			if os.path.isfile(temp):
				if with_txt_file:
					basename_temp, _ = os.path.splitext(temp)
					temp_txt = "".join([basename_temp, '.txt'])
					compress.from_txt_to_n2c(temp, temp_txt)
				else:
					compress.from_xml_to_n2c(temp)
	elif os.path.isfile(arg):
		if with_txt_file:
			basename_temp, _ = os.path.splitext(temp)
			temp_txt = "".join([basename_temp, '.txt'])
			compress.from_txt_to_n2c(arg, temp_txt)
		else:
			compress.from_xml_to_n2c(arg)
	else:
		print "It is not a file or a directory.", arg
		sys.exit(2)

def random(arg):
	"""
	Outdated. 
	Now, false note are dynamically generated in the batch (see Dataset module)

	Create xml file(s), with some random notes.
	Txt file(s) is/are also created, including all random note index.
	In txt files, all numbers are comma-separated.
	More information in rng module.

	Parameters
	----------
	arg:	string
			File to be note-randomized .
			If it is a directory, all files will be note-randomized.

	Returns
	-------
	"""
	if os.path.isdir(arg):
		for file in os.listdir(arg):
			temp = utils.getPath(arg, file)
			if os.path.isfile(temp):
				rng.randomly_modify_file(temp)
	elif os.path.isfile(arg):
		rng.randomly_modify_file(arg)
	else:
		print "It is not a file or a directory."
		sys.exit(2)

def sort(arg):
	"""
	Outdated.

	Check is xml file is correct :
		- has more then 30 notes;
		- has at least 8 different notes;
		- notes are between the 1st and 7th octave.
	If the file is not correct, it will be deleted.
	More information in utils module.

	Parameters
	----------
	arg:	string
			File to be sorted.
			If it is a directory, all file will be sorted.

	Returns
	-------
	"""
	if os.path.isdir(arg):
		for file in os.listdir(arg):
			temp = utils.getPath(arg, file)
			if os.path.isfile(temp):
				utils.xml_sort(temp)
	elif os.path.isfile(arg):
		utils.xml_sort(arg)
	else:
		print "It is not a file or a directory."
		sys.exit(2)

def unzip(arg):
	"""
	Outdated.

	Transform n2c file to xml file.
	More information in extract module.

	Parameters
	----------
	arg:	string
			File to be uncompressed.
			If it is a directory, all files will be uncompressed.

	Returns
	-------
	"""
	if os.path.isdir(arg):
		for file in os.listdir(arg):
			temp = utils.getPath(arg, file)
			if os.path.isfile(temp):
				extract.from_n2c_to_xml(temp)
	elif os.path.isfile(arg):
		extract.from_n2c_to_xml(arg)
	else:
		print "It is not a file or a directory."
		sys.exit(2)

def melody_len(arg):
	"""
	Count average number of notes in dataset

	Parameters
	----------
	arg:	directory
			Directory with all files to take into account.
	"""
	mean = []
	if os.path.isdir(arg):
		for file in os.listdir(arg):
			temp = utils.getPath(arg, file)
			if os.path.isfile(temp):
				if temp.split('.')[0][-2:] == '_m':
					mean.append(utils.xml_melody_length(temp))
	elif os.path.isfile(arg):
		mean.append(utils.xml_melody_length(arg))
	else:
		print "File or directory not found."
		sys.exit(2)
	print "Mean :", np.mean(mean)
	print "Std :", np.std(mean)
	print 'Sum :', sum(mean)