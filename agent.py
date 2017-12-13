import numpy as np
from keras.models import Sequential, load_model
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

#file_path = "model_learnt_policy.h5"
#model = load_model(file_path)
def save_model(file_path):
	model.save(file_path)


# Hyperparameters
epsilon = 0.7
gamma = 0.99
number_of_games = 10000
mb_size = 3000
c = 0

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
		if (len(game.table) > 0):
			if game.valid(cards[n], game.table[0], game.playerCards[game.startingPlayer]):
				return cards[n]
			else:
				return False
		else:
			return cards[n]
	else:
		return False

def action_space(cards, game):
	out = []
	for c in cards:
		if game.valid(c, playerCards=cards):
			out.append(c)
	return out

def choose_valid_action(Q, game):
	cards = game.playerCards[game.startingPlayer]
	max_n = 0
	max_value = 0
	for i, c in enumerate(cards):
		if game.valid(c, playerCards=cards):
			if max_value < Q[0,i]:
				max_n = i
	return max_n


def play(state, game, epsilon=0.7):
	# Every once in a while take a random action
	if np.random.random() <= epsilon:
		cards = game.playerCards[game.startingPlayer]
		acSpace = action_space(cards, game)
		action = cards.index(np.random.choice(acSpace))
		print(c)
		global c
		c += 1
	else:
		Q = model.predict(state)
		action = choose_valid_action(Q, game)
	game_action = machine_to_action(action, game)
	while not game_action:
		print(c)
		global c
		c+= 1
		# Make sure the game_action is valid
		if np.random.random() <= epsilon:
			action = np.random.randint(2)
		else:
			Q = model.predict(state)
			action = choose_valid_action(Q, game)
		game_action = machine_to_action(action, game)
	return [action, game_action]

# Creating holders for states, actions and rewards
# As well as new_states
def observe(input_cards=None):
	states = {"pl_1": {"points":[],"state":[]}, "pl_2": {"points":[],"state":[]}}
	actions = {"pl_1": [], "pl_2": []}
	rewards = {"pl_1": [], "pl_2": []}
	new_states = {"pl_1": [], "pl_2":[]}
	finished = {"pl_1" : [], "pl_2":[]}

	print("Start Observing ...")
	for t in range(number_of_games):
		print("Game " + str(t) + " started.")
		# Play a whole game with inputs from the model
		game = G()
		if input_cards:
			cards = np.random.choice(input_cards)
			game.playerCards = cards
		if t % 50 == 0:
			print("Initialise Game.")
		# Initialise game
		states["pl_1"]["points"].append(0)
		states["pl_2"]["points"].append(0)
		# First Round
		for _ in range(2):
			state = state_to_machine(game)
			if t % 50 == 0:
				print("player: " + game.startingPlayer)
				print("cards: ")
				print(game.playerCards[game.startingPlayer])
				print("table:")
				print(game.table)
			states[game.startingPlayer]["state"].append(state)
			# Get action from model
			action = play(state, game)
			if t % 50 == 0:
				print("Plays: ")
				print(action[1])
			# Update the actions
			actions[game.startingPlayer].append(action[0])
			# Feed action to the game
			game.startingPlayer = game.nextTurn(action[1], game.startingPlayer)
		# Here starts the second round
		if t % 50 == 0:
			print("table:")
			print(game.table)
		game.startingPlayer = game.nextRound(game.startingPlayer)
		if t % 50 == 0:
			print("Groups:")
			print(game.groups)
		# Update the points of the groups
		states["pl_1"]["points"].append(game.groups[0]['points'])
		states["pl_2"]["points"].append(game.groups[1]['points'])
		# Second Round
		for _ in range(2):
			state = state_to_machine(game)
			if t % 50 == 0:
				print("player: " + game.startingPlayer)
				print("cards: ")
				print(game.playerCards[game.startingPlayer])
				print("table:")
				print(game.table)
			# Update rewards
			points_1 = states[game.startingPlayer]["points"][-2]
			points_2 = states[game.startingPlayer]["points"][-1]
			rewards[game.startingPlayer].append(points_2 - points_1)
			# Update the states holder
			new_states[game.startingPlayer].append(state)
			finished[game.startingPlayer].append(False)
			# Update the 
			states[game.startingPlayer]["state"].append(state)
			# Get action from model
			action = play(state, game)
			if t % 50 == 0:
				print("Plays: ")
				print(action[1])
			# Update the actions
			actions[game.startingPlayer].append(action[0])
			# Feed action to the game
			game.startingPlayer = game.nextTurn(action[1], game.startingPlayer)
		if t % 50 == 0:
			print("table:")
			print(game.table)	
		# Last round
		game.startingPlayer = game.nextRound(game.startingPlayer)
		if t % 50 == 0:
			print("Groups:")
			print(game.groups)
		# Update the points of the groups
		states["pl_1"]["points"].append(game.groups[0]['points'])
		states["pl_2"]["points"].append(game.groups[1]['points'])
		# Update the new State
		state = state_to_machine(game)
		new_states["pl_1"].append(state)
		new_states["pl_2"].append(state)
		finished["pl_1"].append(True)
		finished["pl_2"].append(True)
		# Update rewards
		points_1 = states["pl_1"]["points"][-2]
		points_2 = states["pl_1"]["points"][-1]
		rewards["pl_1"].append(points_2 - points_1)
		points_1 = states["pl_2"]["points"][-2]
		points_2 = states["pl_2"]["points"][-1]
		rewards["pl_2"].append(points_2 - points_1)

		print("Game " + str(t) + " finished.")
	print("Finished observing")
	print("Check Data")
	print(len(states["pl_1"]["state"]))
	print(len(states["pl_2"]["state"]))
	print(len(actions["pl_1"]))
	print(len(actions["pl_2"]))
	print(len(rewards["pl_1"]))
	print(len(rewards["pl_2"]))
	print(len(new_states["pl_1"]))
	print(len(new_states["pl_2"]))
	print(len(finished["pl_1"]))
	print(len(finished["pl_2"]))

	# Create a 5 Tuple with state action reward future_state and finished
	D_1 = list(zip(states["pl_1"]["state"], actions["pl_1"], rewards["pl_1"], new_states["pl_1"], finished["pl_1"]))
	D_2 = list(zip(states["pl_2"]["state"], actions["pl_2"], rewards["pl_2"], new_states["pl_2"], finished["pl_2"]))
	D = D_1 + D_2
	print(len(D))
	rand_D = D
	return rand_D

def learn(rand_D):
	# Learning the game
	print("Start Learning...")
	np.random.shuffle(rand_D)
	minibatch = rand_D[0:mb_size]

	inputs = np.zeros((mb_size, 48))
	targets = np.zeros((mb_size, 2))

	for i in range(mb_size):
		print("Batch no " + str(i))
		state = minibatch[i][0]
		action = minibatch[i][1]
		reward = minibatch[i][2]
		state_new = minibatch[i][3]
		finished = minibatch[i][4]

		inputs[i] = state
		targets[i] = model.predict(state)

		if finished:
			targets[i, action] = reward
		else:
			Q_sa = model.predict(state_new)
			targets[i, action] = reward + gamma*np.max(Q_sa)
		model.train_on_batch(inputs, targets)

	print("Learning Finished.")
	print("model saved")
	save_model("model_2.h5")

t = 0
def evaluate(cards=None):
	# Play a whole game with inputs from the model
	game = G()
	if cards:
		game.playerCards = cards

	if t % 50 == 0:
		print("Initialised Game.")
	# First Round
	for _ in range(2):
		state = state_to_machine(game)
		if t % 50 == 0:
			print("player: " + game.startingPlayer)
			print("cards: ")
			print(game.playerCards[game.startingPlayer])
			print("table:")
			print(game.table)
		# Get action from model
		action = play(state, game, 0.0)
		if t % 50 == 0:
			print("Plays: ")
			print(action[1])
		# Feed action to the game
		game.startingPlayer = game.nextTurn(action[1], game.startingPlayer)
	# Here starts the second round
	if t % 50 == 0:
		print("table:")
		print(game.table)
	game.startingPlayer = game.nextRound(game.startingPlayer)
	if t % 50 == 0:
		print("Groups:")
		print(game.groups)
	# Second Round
	for _ in range(2):
		state = state_to_machine(game)
		if t % 50 == 0:
			print("player: " + game.startingPlayer)
			print("cards: ")
			print(game.playerCards[game.startingPlayer])
			print("table:")
			print(game.table)
		# Get action from model
		action = play(state, game, 0.1)
		if t % 50 == 0:
			print("Plays: ")
			print(action[1])
		# Feed action to the game
		game.startingPlayer = game.nextTurn(action[1], game.startingPlayer)
	if t % 50 == 0:
		print("table:")
		print(game.table)	
	# Last round
	game.startingPlayer = game.nextRound(game.startingPlayer)
	if t % 50 == 0:
		print("Groups:")
		print(game.groups)
	state = state_to_machine(game)
	# Update rewards
	print("Game " + str(t) + " finished.")

#rand_D = observe()
#learn(rand_D)
#print("Let's see what the model can do.")
#evaluate()
# Save the model



