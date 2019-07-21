# -*- coding: utf-8 -*-
"""check_char_rnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16KNysNJqbvZAnYekm_vqcryKvf0WxbU6
"""

from graphviz import Digraph
import networkx as nx
from matplotlib import pyplot
import random
import pandas as pd
from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.utils import plot_model
from keras import metrics
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import tensorflow as tf
import numpy as np
import sys
import io
from keras import models 
from keras import layers

# TODO: chnage 256 to a smaller number - check accuracy plots + different epochs
# TODO: hidden state calculation should be faster - can be enabled based on the need 
# or disabled if only properties of Y

#####################################################################
#    Parameters
#####################################################################

# input and output
sizeX = 3
sizeY = sizeX   # next character prediction


# text information
alphabet = ['c', 'a', 't', 'e', ' ']
sizeAlphabet = len(alphabet)

# human words generated by scramble game
human_words = ['cate',  'tace', 'ace',  'act',  'ate',  'cat', 'eat', 'eta', 
               'tae', 'tea', 'ae', 'at', 'et', 'ta']
n_words_in_corpus = 100000


print("Alphabet used: {}".format(alphabet))
print("Human words count : {}".format(len(human_words)))

#####################################################################
#    Create corpus to train a model
#####################################################################
text = ''
for i in range(0, n_words_in_corpus):
    if i % 10000 == 0:
      print("i = {}".format(i))
      
    j = int(random.uniform(0, len(human_words)))
    text = text + ' ' + human_words[j]

file = open('cat_' + str(n_words_in_corpus) + '.txt', 'w')
file.write(text)
file.close()

_ = pd.Series(text.split(' '))
print("Words distribution: {}".format(_.value_counts()))

#####################################################################
#    Train model
#####################################################################
def sentence_to_code(sentence, char_indices, maxlen, sizeAlphabet):
  x = np.zeros((1, maxlen, sizeAlphabet))
  for t, char in enumerate(sentence):
      x[0, t, char_indices[char]] = 1.0
  return x

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, _):
    # Function invoked at end of each epoch. Prints generated text.
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    start_index = random.randint(0, len(text) - maxlen - 1)
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print('----- diversity:', diversity)

        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

        for i in range(400):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        print()

chars = sorted(list(set(text)))
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 3
step = 3
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))

print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

print("Chars to indices encoding: {}".format(char_indices))

# Sequential API
print('Build model...')
model = Sequential()
lstm_hunits = 256  # TODO: tune this parameter
model.add(LSTM(lstm_hunits, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars), activation='softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=[metrics.mae, metrics.categorical_accuracy])
plot_model(model, to_file='multilayer_perceptron_graph.png')

model.summary()

print("x size = {}".format(x.shape))
print("LSTM Layer Parameters: {}".format(4*(lstm_hunits*lstm_hunits + lstm_hunits*sizeAlphabet + lstm_hunits))) # 4*(256*256 + 5*256 + 256*1) 
print("Dense Layer Parameters: {}".format(lstm_hunits*sizeAlphabet + sizeAlphabet))  # dense 5*256 + 5
print("y size = {}".format(x.shape))

print_callback = LambdaCallback(on_epoch_end=on_epoch_end)

# history = funcmodel1.fit(x, [y,0.1*np.ones((128570, len(chars))), 0.1*np.ones((128570, len(chars)))], # [y, np.zeros((128570, len(chars))), np.zeros((128570, len(chars)))],#,np.zeros((128570, len(chars))),np.zeros((128570, len(chars)))],
history = model.fit(x, y,          
          batch_size=128,
          epochs=10,
          callbacks=[print_callback])

for layer in model.layers:
  print(str(layer))
  if "LSTM" in str(layer):
    weightLSTM = layer.get_weights()
    print(weightLSTM)

# plot metrics
pyplot.plot(history.history['categorical_accuracy'])
pyplot.show()

# plot metrics
pyplot.plot(history.history['mean_absolute_error'])
pyplot.show()

#####################################################################
# Validate that models predicts well
#####################################################################
generated = ''
sentence = ' ca'
generated += sentence
print('----- Generating with seed: "' + sentence + '"')

x_pred = np.zeros((1, maxlen, len(chars)))
for t, char in enumerate(sentence):
    x_pred[0, t, char_indices[char]] = 1.

preds = model.predict(x_pred, verbose=0)[0]
print("preds =", preds)
next_index = sample(preds, 0.001)
next_char = indices_char[next_index]

sys.stdout.write("next_char = {} \n".format(next_char))

#####################################################################
#    Save model
#####################################################################
model.save('model_train{}_alphabet{}_x{}.h5'.format(n_words_in_corpus, sizeAlphabet, sizeX))

#####################################################################
#    Create StateTransition System from RNN
#####################################################################

# I. Create Graph Structure (using only metadata of the network)
#------------------------------------------------------------------------------

# G is the graph constructed from RNN Inputs
G = nx.balanced_tree(r=sizeAlphabet, h=sizeX)
f = Digraph('balanced_tree', filename='balanced_'+str(sizeX)+'_'+str(sizeAlphabet)+'.gv')
f.attr(rankdir='LR', size='8,5')

for b_node in G.nodes:
    f.node("S"+str(b_node), H="", Y="")

for i, b_edge in enumerate(G.edges):
    label = alphabet[i%sizeAlphabet]
    f.edge("S"+str(b_edge[0]), "S"+str(b_edge[1]), label)
    
# II. Create Attributes Empty and assign to the nodes
#------------------------------------------------------------------------------

labels = {}
rnn_states = {}

r = sizeAlphabet
h = sizeX

# root:
state_placeholder = np.array([])
rnn_states[0] = state_placeholder  # state will contain rnn H and Y of the model
next_node_id = 1

for level in range(1,h+1):
  print("Tree level:", level)  
  elemnts_count = pow(r,level)
  print("elemnts_count = ", elemnts_count)
  
  print("Nodes btw :", next_node_id, " and ", next_node_id + elemnts_count)
  for node_id in range(next_node_id,  next_node_id + elemnts_count): 
    rnn_states[node_id] = state_placeholder
    labels[node_id] = alphabet[node_id%sizeAlphabet]
  next_node_id = node_id+1
  print("next_node_id = ", next_node_id)

nx.set_node_attributes(G, labels, 'label')
nx.set_node_attributes(G, rnn_states, 'rnn_state')

# III. Get x per node
#------------------------------------------------------------------------------

x_val = {}
above_labels = {}

for node_id in G.nodes:
  node = G.nodes[node_id]
  print("node_id=",node_id, " node = ",node)
  shortest_path = nx.shortest_path(G, source=0, target=node_id)
  above_labels_str = ""
  for j in shortest_path[1:]:
    above_labels_str = above_labels_str + G.nodes[j]['label']
  print("above_labels_str = ", above_labels_str)
  
  
  if 'label' in node.keys():
    label = node['label']
    print("label = ", label)
    above_labels[node_id] = above_labels_str
    
    if len(above_labels_str) <= maxlen:
      x_val[node_id] = sentence_to_code(above_labels_str, char_indices, maxlen, sizeAlphabet)
    else:
      x_val[node_id] =np.array([])
nx.set_node_attributes(G, above_labels, 'above_labels')
nx.set_node_attributes(G, x_val, 'x_val')

# IV. Get y per node
#------------------------------------------------------------------------------
y_val = {}
for node in G.nodes():
  if 'x_val' in  G.nodes[node].keys():
    x_val_node = G.nodes[node]['x_val']
    y_val_node = model.predict(x_val_node, verbose=0)[0]
    y_val[node] = y_val_node
nx.set_node_attributes(G, y_val, 'y_val')

# IV. Calculate hidden states per node
#------------------------------------------------------------------------------
for layer in model.layers:
        if "LSTM" in str(layer):
            weightLSTM = layer.get_weights()
warr,uarr, barr = weightLSTM
warr.shape,uarr.shape,barr.shape


def get_hidden_states_keras(model, xs, sizeX, sizeAlphabet, lstm_hunits):
  batch_size = 1
  len_ts = sizeX
  nfeature = sizeAlphabet
  inp = layers.Input(batch_shape= (batch_size, len_ts, nfeature),
                         name="input")  
  rnn,s,c = layers.LSTM(lstm_hunits, 
                           return_sequences=True,
                           stateful=False,
                           return_state=True,
                           name="RNN")(inp)
  states = models.Model(inputs=[inp],outputs=[s,c, rnn])
  for layer in states.layers:
      for layer1 in model.layers:
          if layer.name == layer1.name:
              layer.set_weights(layer1.get_weights())
  h_t_keras, c_t_keras, rnn = states.predict(xs.reshape(1,len_ts,5))  
  return (h_t_keras, c_t_keras)


# # Example:

# xs = np.array([[[0., 0., 0., 0., 1.],
#         [1., 0., 0., 0., 0.],
#         [0., 0., 0., 0., 0.]]])
# tmp = get_hidden_states_keras(model, xs, sizeX, sizeAlphabet, lstm_hunits)
# print("tmp ={}".format(tmp))



h_val = {}
for node in G.nodes():
  if 'x_val' in  G.nodes[node].keys():
    x_val_node = G.nodes[node]['x_val']
    h_val_node = get_hidden_states_keras(model, x_val_node, sizeX, sizeAlphabet, lstm_hunits)
    h_val[node] = h_val_node
    
nx.set_node_attributes(G, h_val, 'h_val')

#####################################################################
#    Ground truth property satisfaction
#####################################################################
total_combinations = len(G.nodes()) # total nodes
n_satisfy = 0
# calculate Property rate over ground truth Graph
for node in G.nodes():
  if 'y_val' in  G.nodes[node].keys():
    y_val_node = G.nodes[node]['y_val']
    if any(y_val_node>0.8):
      n_satisfy = n_satisfy + 1
gt_satisfy = n_satisfy/total_combinations
print("Ground truth property satisfaction rate:{}".format(gt_satisfy))

####################################################
#  TensorSMC
####################################################
alpha = 1 
beta = 1 

smc_satisfy_rates = []
smc_ro_estimates = []
smc_nu_estimates = []
increasing_samples  = range(1, total_combinations, 5)

for j in increasing_samples:
  n_trajectories = 0   # number trajectories drawn so far
  n_satisfy = 0     # number of trajectories satisfying property so far

  for n_trajectories in range(0,j+1):
    index_rand = random.randrange(total_combinations)
    if 'y_val' in  G.nodes[index_rand].keys():
      y_val_node = G.nodes[index_rand]['y_val']
      if any(y_val_node>0.8):
        n_satisfy = n_satisfy + 1
  print("n_satisfy={}, n_trajectories={}".format(n_satisfy, n_trajectories))
  print("SMC property satisfaction rate:{}".format(n_satisfy/n_trajectories)) 
  ro = (n_satisfy + alpha)/(n_trajectories + alpha + beta)
  nu = np.sqrt(((alpha + n_satisfy)*(n_trajectories - n_satisfy + beta)) / (pow((alpha + n_trajectories + beta),2)*(alpha + n_trajectories + beta + 1)))
  print("Estiamted property satisfaction:{} +/- {}".format(ro, nu)) 
  smc_satisfy_rates.append(n_satisfy/n_trajectories)
  smc_ro_estimates.append(ro)
  smc_nu_estimates.append(nu)

import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
ax = sns.scatterplot(x=increasing_samples, y=smc_ro_estimates)
ax.errorbar(increasing_samples, smc_ro_estimates, yerr=smc_nu_estimates)
sns.scatterplot(x=increasing_samples, y=smc_satisfy_rates, ax = ax)
ax.axhline(gt_satisfy, ls='--', color='r')
ax.legend(labels=['Ground Truth', 'SMC (theory)', 'SMC (experiment)'])

f