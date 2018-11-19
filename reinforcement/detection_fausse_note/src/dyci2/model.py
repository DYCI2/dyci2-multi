import tensorflow as tf
import tensorflow.contrib.layers as layers

class Model():

	def __init__(self, n_inputs, n_outputs, n_hidden, n_step, num_layers, lr, momentum, target_note):
		"""
		Create a BLSTM-model to detect false note in a music improvisiation.

		Parameters
		----------
		n_inputs:	int
					Size of a note.

		n_ouputs:	int
					Size of output.

		n_hidden:	int
					Size of hiddenn lstm output.

		n_step:		int
					Number of lstm cells (also number of notes)

		num_layers: int
					Number of a layer (Not used).

		lr:			float
					Learning rate.

		momentum:	float
					Momentum.

		target_note: int
					Number of the cell to get the output for accuracy (Not used).

		Raise
		-----
		Exeception:	if a parameter doesn't match with its type.
		"""
		self.lr 			= lr
		self.size_output 	= n_outputs
		_past_index 		= 1
		_future_index 		= 1
		# Bidirectionnal RNN

		# Inputs Layer
		self.inputs 	= tf.placeholder(
			dtype=tf.float32,
			shape=(None, n_step, n_inputs), #batch, time, in
			name="Dataset"
			)
		batch_size = tf.shape(self.inputs)[0]

		self.outputs = tf.placeholder(
			dtype = tf.float32,
			shape = (None, self.size_output), # Batch, out
			name="Labels"
		)
		with tf.variable_scope("Model"):
			# Variables
			with tf.variable_scope("Variables"):
				#BiRNN
				with tf.variable_scope("BiRNN"):
					# Define LSTM cell
					self.cell_fw = tf.contrib.rnn.LSTMCell(
						num_units=n_hidden)

					self.cell_bw = tf.contrib.rnn.LSTMCell(
						num_units=n_hidden)
					# Add PAST and FUTURE
					#with tf.variable_scope("MultiLayer"):
					#	self.cell_fw = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.LSTMCell(num_units=n_hidden) for _ in range(num_layers)])

					self.initial_state_fw = self.cell_fw.zero_state(batch_size, tf.float32)
					#self.initial_state = self.cell_fw.zero_state(batch_size, tf.float32)
					self.initial_state_bw = self.cell_bw.zero_state(batch_size, tf.float32)

					self.rnn_outputs, self.rnn_states = tf.nn.bidirectional_dynamic_rnn(
						cell_fw=self.cell_fw,
						cell_bw=self.cell_bw,
						initial_state_bw= self.initial_state_bw,
						initial_state_fw= self.initial_state_fw,
						inputs=self.inputs,
						dtype=tf.float32)

					#print self.rnn_outputs
					#print self.rnn_states
					#self.x_vec = tf.reshape(self.concat, shape=(-1, 2*n_hidden*n_step))
					#self.dense = tf.layers.dense(
					#	inputs = self.x_vec,
					#	units  = n_hidden*n_step,
					#	activation = tf.sigmoid
					#	)
				with tf.variable_scope("FeedForward"):
					self.feed_forward = tf.layers.dense(
						inputs=self.inputs,
						units=n_hidden,
						activation=tf.nn.sigmoid)

				with tf.variable_scope("Sigmoid"):
					#self.fc_future = tf.layers.dense(
					#	inputs=concat,
					#	units= 64,
					#	activation=tf.nn.sigmoid
					#)
					concat = tf.stack([self.rnn_outputs[0],self.rnn_outputs[-1], self.feed_forward], axis=3)
					print concat.shape
					flat_fc_future = tf.reshape(concat, shape=(-1, 3*n_hidden*n_step))
					#flat_bw = tf.reshape(self.rnn_outputs[-1], shape=(-1, n_step*n_hidden))
					self.dense_future = tf.layers.dense(
						inputs= flat_fc_future,
						units=self.size_output,
						activation=tf.nn.sigmoid)
					print self.dense_future.shape
					#self.weights_future = tf.Variable(tf.truncated_normal([2*n_step*n_hidden, self.size_output], stddev=0.1))
					#self.biases_future  = tf.Variable(tf.random_uniform([self.size_output]))
					#self.x_vec_future = tf.reshape(self.dropout_future, shape=(-1, 2*n_step*n_hidden))

				"""
				with tf.variable_scope("Past"):
					#self.fc_past = tf.layers.dense(
					#	inputs=concat,
					#	units=64,
					#	activation=tf.nn.sigmoid)
					flat_fc_past = tf.reshape(concat, shape=(-1, 2*n_hidden*n_step))
					self.dense_past = tf.layers.dense(
						inputs=flat_fc_past,
						units=self.size_output,
						activation=None)
					print self.dense_past.shape
					#self.weights_past = tf.Variable(tf.truncated_normal([n_step*n_hidden, self.size_output], stddev=0.1))
					#self.biases_past  = tf.Variable(tf.random_uniform([self.size_output]))
					#self.x_vec_past = tf.reshape(self.dropout_past, shape=(-1, n_step*n_hidden))
				"""

			# Predictions for Training, Validation and Test datas.
			with tf.variable_scope("Training"):
				with tf.variable_scope("Logits"):
					#self.predicted	= tf.nn.relu(tf.reshape(tf.matmul(self.x_vec_past, self.weights_past), shape=(-1, self.size_output)) + self.biases_past)
					#self.fredicted 	= tf.nn.relu(tf.reshape(tf.matmul(self.x_vec_future, self.weights_future), shape=(-1, self.size_output)) + self.biases_future)
					#self.predicted = tf.nn.softmax(self.dense_past)
					self.fredicted = tf.nn.softmax(self.dense_future)
				with tf.variable_scope("Loss"):
					#self.error	= tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=self.predicted, labels=self.outputs))
					#self.ferror	= tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=self.fredicted, labels=self.outputs))
					#self.error		= tf.losses.softmax_cross_entropy(self.outputs, self.predicted)
					self.ferror		= tf.losses.softmax_cross_entropy(self.outputs, self.fredicted)
				with tf.variable_scope("Optimizer"):
					#self.train	= tf.train.MomentumOptimizer(learning_rate=self.lr, momentum=momentum).minimize(self.error, name="Model_Optimizer")
					#self.train	= tf.train.GradientDescentOptimizer(learning_rate=self.lr).minimize(self.error, name="Model_Optimizer")
					self.ftrain	= tf.train.GradientDescentOptimizer(learning_rate=self.lr).minimize(self.ferror, name="Model_Optimizer")
					#self.train	= tf.train.MomentumOptimizer(learning_rate=self.lr, momentum=0.9).minimize(self.error, name="Model_Optimizer")
					#self.ftrain	= tf.train.MomentumOptimizer(learning_rate=self.lr, momentum=0.9).minimize(self.ferror, name="Model_Optimizer")
			#self.note_outputs 	= self.outputs[:, target_note, :]

			with tf.variable_scope("Outputs"):
				with tf.variable_scope("Output"):
					#self.correct	= tf.equal(tf.argmax(self.predicted, 1), tf.argmax(self.outputs, 1))
					#self.accuracy 	= tf.reduce_mean(tf.cast(self.correct, dtype=tf.float32))

					self.forrect	= tf.equal(tf.argmax(self.fredicted, 1), tf.argmax(self.outputs, 1))
					self.faccuracy 	= tf.reduce_mean(tf.cast(self.forrect, dtype=tf.float32))

	# Future FEED and EVAL
	def feed(self, sess, summary, x, y):
		return sess.run([summary, self.ftrain], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	def eval(self, sess, summary, x, y):
		return sess.run([summary, self.ferror], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	def test(self, sess, x, y):
		return sess.run([tf.argmax(self.fredicted, 1), tf.argmax(self.outputs, 1)], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	# Past FEED and EVAL
	def feed_past(self, sess, summary, x, y):
		return sess.run([summary, self.train], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	def eval_past(self, sess, summary, x, y):
		return sess.run([summary, self.error], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	def test_past(self, sess, x, y):
		return sess.run([tf.argmax(self.predicted, 1), tf.argmax(self.outputs, 1)], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	# ESTIMATOR
	def estimate(self, sess, x):
		return sess.run([tf.argmax(self.fredicted, 1), tf.argmax(self.fredicted, 1)], feed_dict= {
			self.inputs : x
			})

	def restore(self, sess, saver):
		saver.restore(sess, tf.train.latest_checkpoint("./"))

	def save(self, sess, saver):
		saver.save(sess, "model_v2.0")

	def roc(self, sess, x, y):
		return sess.run([self.fredicted, self.outputs], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})

	def debug(self, sess, x, y):
		return sess.run([self.ftrain, self.ferror, self.fredicted, self.outputs], feed_dict={
			self.inputs 	: x,
			self.outputs 	: y
			})
