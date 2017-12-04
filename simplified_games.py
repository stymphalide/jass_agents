# This module provides several simulations of jass games
# Each with different degree of complexity
import numpy as np
import game 


class Level_1(game.Game):
	"""docstring for Level_1
		This level consists of two colors and 
		two cards per color (ace and 6)
		The game is played with two players (ergo no unknowns)
	"""
	def __init__(self):
		self.players = ["pl_1", "pl_2"]
		self.colors = ["hearts", "spades"]
		self.numbers = ["ace", "6"]
		self.gameType = "up"
		self.cardsTable = []
		self.groups = [{"points":0,"players":"pl_1"}, {"points":0,"players":"pl_2"}]
		self.history = []
		self.cards = self.generateCards()
		self.playerCards = self.distributeCards(self.players, self.cards)


	