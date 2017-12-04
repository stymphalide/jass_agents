import numpy as np
class Game(object):
	"""docstring for Game
	A Class with the basic behavior of a game
	"""

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
		return {"color": color, "number", number}

	# Distributes Cards to the players equally
	# Returns a map with keys encoded as the player names
	def distributeCards(self, players cards):
		if len(cards) % len(players) != 0:
			print("Error: The cards can't be distributed evenly")
		else:
			n_cards = len(cards) / len(players)
			rand_cards = np.random.shuffle(cards)
			out_cards = {}
			for i, pl in enumerate(players):
				adder = i*n_cards
				start = adder
				end = adder + n_cards
				out_cards[pl] = rand_cards[start:end]
			return out_cards

	# next 