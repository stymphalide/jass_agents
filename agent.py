import numpy as np
from keras.models import Sequential
from keras.layers import Dense

from simplified_games import Level_1 as G


# The input size of the vector
input_size = 4*(2+2+4+4) # I'd prefer 4x(2+2+4+4)
# Make the model
model = Sequential()
model.add(Dense(10, init='uniform', input_shape=[input_size], activation='relu' ))
model.add(Dense(5, init='uniform', activation='relu'))
model.add(Dense(2, init='uniform', activation='linear')) 
model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

# Hyperparameters
epsilon = 0.7
gamma = 0.99


# Returns a vector of length input_size
def game_to_machine(game):
	# Initialise the matrices
	pC = np.zeros([2,4])
	tC = np.zeros([2,4])
	hCa = np.zeros([4,4])
	hCb = np.zeros([4,4])

	# Update the playerCards
	cards = game.playerCards[game.startingPlayer] 
	for i in range(0, 2):
		if(len(cards) > i):
			pC[i] = game.encodeCard(cards[i])

	# Update the table cards
	cards = game.table
	for i in range(2):
		if(len(cards) > i):
			tC[i] = game.encodeCard(cards[i])

	# Update the first groups' history
	cards = game.history[0]
	for i in range(4):
		if(len(cards) > i):
			hCa[i] = game.encodeCard(cards[i])
	
	# Update the first groups' history
	cards = game.history[1]
	for i in range(4):
		if(len(cards) > i):
			hCb[i] = game.encodeCard(cards[i])

	return np.concatenate((pC, tC, hCa, hCb), axis=0).flatten()

# Returns the card that the machine wanted to play,
# Returns False if the machine didn't play a valid card
def machine_to_action(n, game):
	cards = game.playerCards[game.startingPlayer]
	if(n < len(cards)):
		return cards[n]
	else:
		return False
