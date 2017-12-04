import numpy as np
from keras.models import Sequential
from keras.layers import Dense

import pickle

from simplified_games import Level_1 as G


# The input size of the vector
input_size = 4*(2+2+4+4) # I'd prefer 4x(2+2+4+4)
# Make the model
model = Sequential()
model.add(Dense(10, kernel_initializer='uniform', input_shape=(input_size,), activation='relu' ))
model.add(Dense(5, kernel_initializer='uniform', activation='relu'))
model.add(Dense(2, kernel_initializer='uniform', activation='linear')) 
model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

# Hyperparameters
epsilon = 0.7
gamma = 0.99
number_of_games = 100
mb_size = 30

# Returns a vector of length input_size
def state_to_machine(game):
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
	for i in range(2):
		if(len(cards) > i):
			for j in range(2):
				hCa[2*i+j] = game.encodeCard(cards[i][j])
	
	# Update the first groups' history
	cards = game.history[0]
	for i in range(2):
		if(len(cards) > i):
			for j in range(2):
				hCb[2*i+j] = game.encodeCard(cards[i][j])
	
	return np.concatenate((pC, tC, hCa, hCb), axis=0).reshape([1,48])

# Returns the card that the machine wanted to play,
# Returns False if the machine didn't play a valid card
def machine_to_action(n, game):
	cards = game.playerCards[game.startingPlayer]
	if(n < len(cards)):
		return cards[n]
	else:
		return False

# Returns a vector with the action
def action_to_action_vector(action):
	vec = np.zeros(4)
	vec[action] = 1
	return vec

def play(state, game):
	# Every once in a while take a random action
	if np.random.random() <= epsilon:
		action = np.random.randint(2)
	else:
		Q = model.predict(state)
		action = np.argmax(Q)
	machine_action = action_to_action_vector(action)
	game_action = machine_to_action(action, game)
	while not game_action:
		# Make sure the game_action is valid
		if np.random.random() <= epsilon:
			action = np.random.randint(2)
		else:
			Q = model.predict(state)
			action = np.argmax(Q)
		game_action = machine_to_action(action, game)
		machine_action = action_to_action_vector(action)
	return [machine_action, game_action]


# Creating holders for states, actions and rewards
# As well as new_states
states = {"pl_1": {"points":[],"state":[]}, "pl_2": {"points":[],"state":[]}}
actions = {"pl_1": [], "pl_2": []}
rewards = {"pl_1": [], "pl_2": []}
new_states = {"pl_1": [], "pl_2":[]}


print("Start Observing ...")
c = 0
for t in range(number_of_games):
	print("Game " + str(t) + " started.")
	# Play a whole game with inputs from the model
	game = G()
	# Initialise game
	states["pl_1"]["points"].append(0)
	states["pl_2"]["points"].append(0)
	# First Round
	for _ in range(2):
		state = state_to_machine(game)
		states[game.startingPlayer]["state"].append(state)
		# Get action from model
		action = play(state, game)
		# Update the actions
		actions[game.startingPlayer].append(action[0])
		# Feed action to the game
		game.startingPlayer = game.nextTurn(action[1], game.startingPlayer)
	# Here starts the second round
	game.startingPlayer = game.nextRound(game.startingPlayer)
	# Update the points of the groups
	states["pl_1"]["points"].append(game.groups[0]['points'])
	states["pl_2"]["points"].append(game.groups[1]['points'])
	# Second Round
	for _ in range(2):
		state = state_to_machine(game)
		# Update rewards
		points_1 = states[game.startingPlayer]["points"][-2]
		points_2 = states[game.startingPlayer]["points"][-1]
		rewards[game.startingPlayer].append(points_2 - points_1)
		# Update the states holder
		new_states[game.startingPlayer].append(state)
		# Update the 
		states[game.startingPlayer]["state"].append(state)
		# Get action from model
		action = play(state, game)
		# Update the actions
		actions[game.startingPlayer].append(action[0])
		# Feed action to the game
		game.startingPlayer = game.nextTurn(action[1], game.startingPlayer)

	# Last round
	game.startingPlayer = game.nextRound(game.startingPlayer)
	# Update the points of the groups
	states["pl_1"]["points"].append(game.groups[0]['points'])
	states["pl_2"]["points"].append(game.groups[1]['points'])
	# Update the new State
	state = state_to_machine(game)
	new_states["pl_1"].append(state)
	new_states["pl_2"].append(state)
	# Update rewards
	points_1 = states[game.startingPlayer]["points"][-2]
	points_2 = states[game.startingPlayer]["points"][-1]
	rewards[game.startingPlayer].append(points_2 - points_1)
	print("Game " + str(t) + " finished.")

print("Finished observing")
print(len(states["pl_1"]["state"]))
print(len(states["pl_2"]["state"]))
print(len(actions["pl_1"]))
print(len(actions["pl_2"]))
print(len(rewards["pl_1"]))
print(len(rewards["pl_2"]))
print(len(new_states["pl_1"]))
print(len(new_states["pl_2"]))
# Learning the game
print("Start Learning...")

minibatch = np.random.randint(mb_size)