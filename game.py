import numpy as np
class Game(object):
	"""docstring for Game
	A Class with the basic behavior of a game
	"""

	def __init__(self):
		self.players = []
		self.colors = []
		self.numbers = []
		self.groups = []
		self.table
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

	# Gives the order of the cards, so that we acquire a sorted set of cards
	def order(self, card):
		l = len(self.numbers)
		multiplier = self.colors.index(card["color"])
		num = self.numbers.index(card["number"])

		return multiplier*l + num + 1

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
		self.table.append(card)
		self.playerCards[player].remove(card)
		self.turn += 1
		l = len(self.players)
		idx_pl = self.players.index(player)
		return self.players[(idx_pl + 1) % l]

	# Determines the next round
	# Moves cards around and distributes points
	# Returns the next player on Turn
	def nextRound(self, startingPlayer):
		