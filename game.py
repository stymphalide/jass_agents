import numpy as np
class Game(object):
	"""docstring for Game
	A Class with the basic behavior of a game
	"""

	def __init__(self):
		self.players = []
		self.colors = []
		self.numbers = []
		self.groups = [{}, {}]
		self.history = [[], []]
		self.table = []
		self.gameType = ""
		self.round = 0
		self.turn = 0
		self.roundPlayer = ""
		self.playerCards = []

	# Returns a n+k row vector with the first n places encodng the color,
	# the second k places the number
	def encodeCard(self, card):
		l_col = len(self.colors)
		length = l_col + len(self.numbers)
		enc = np.zeros(length)
		idx_col = self.colors.index(card["color"])
		idx_num = self.numbers.index(card["number"])
		enc[idx_col] = 1
		enc[l_col + idx_num] = 1
		return enc 

	# Generate a deck of cards based on the colors and numbers given
	def generateCards(self):
		cards = []
		for c in self.colors:
			for n in self.numbers:
				cards.append(self.generateCard(c, n))
		return cards

	# Generate a single card
	def generateCard(self, color, number):
		return {"color": color, "number": number}

	# Validate whether a card can be played
	def valid(self, playCard, firstCard=None, playerCards=None):
		if playerCards == None:
			playerCards = self.playerCards[self.startingPlayer]
		if firstCard == None:
			if len(self.table) > 0:
				firstCard = self.table[0]
			else:
				return True
		if playCard["color"] == firstCard["color"]:
			return True
		else:
			req_color = firstCard["color"]
			for c in playerCards:
				if c["color"] == req_color:
					return False
			return True

	# Gives the order of the cards, so that we acquire a sorted set of cards
	def order(self, card):
		l = len(self.numbers)
		multiplier = self.colors.index(card["color"])
		num = self.numbers.index(card["number"])

		return multiplier*l + num + 1

	# Returns points of a specific card
	def points(self, card):
		points = {"10" : 10, "jack":2, "queen":3, "king":4, "ace":11}
		if(card["number"] in points):
			return points[card["number"]]
		else:
			return 0
	# Map several cards on the point function and add up
	def sum_points(self, cards):
		points = 0
		for c in cards:
			points += self.points(c)
		return points

	# Distributes Cards to the players equally
	# Returns a map with keys encoded as the player names
	def distributeCards(self, players, cards):
		if len(cards) % len(players) != 0:
			print("Error: The cards can't be distributed evenly")
		else:
			n_cards = len(cards) / len(players)
			rand_cards = cards
			np.random.shuffle(rand_cards)
			out_cards = {}
			for i, pl in enumerate(players):
				adder = i*n_cards
				start = adder
				end = adder + n_cards
				pl_cards = rand_cards[int(start):int(end)]
				out_cards[pl] = sorted(pl_cards, key=self.order)
			return out_cards

	# Returns the next player on turn and moves the cards around
	def nextTurn(self, card, player):
		# Check whether card is valid

		if len(self.table) != 0:
			valid = self.valid(card, self.table[0], self.playerCards[player])
			if not valid:
				return player
		self.table.append(card)
		self.playerCards[player].remove(card)
		self.turn += 1
		l = len(self.players)
		idx_pl = self.players.index(player)
		return self.players[(idx_pl + 1) % l]

	# Handles the next round
	# Moves cards around and distributes points
	# Returns the next player on Turn
	def nextRound(self, startingPlayer):
		add = self.determineWinnerCard(self.table)
		idx = self.players.index(startingPlayer)
		l = len(self.players)
		new_idx = (idx + add) % l
		new_player = self.players[new_idx]  

		for i, g in enumerate(self.groups):
			if new_player in g["players"]:
				g["points"] += self.sum_points(self.table)
				self.history[i].append(self.table)
				# Add five points if the game is over
				if len(self.playerCards[new_player]) == 0:
					g["points"] += 5
					# Add 100 points when a match happens
					l = len(self.cards) / len(self.players)
					if len(self.history[i]) == l:
						g["points"] += 100

		self.table = []
		self.turn = 0
		self.round += 1
		return new_player

	# Returns a value between 0 and len(cards)
	# Corresponding to the index of the card
	def determineWinnerCard(self, cards):
		req_color = cards[0]["color"]
		highest_card = cards[0]
		highest_score = self.numbers.index(cards[0]["number"])
		for c in cards[1:]:
			if c["color"] == req_color:
				score = self.numbers.index(c["number"])
				if  score > highest_score :
					highest_score = score
					highest_card = c
		return cards.index(highest_card)

