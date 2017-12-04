import unittest

import game as g

class MyTest(unittest.TestCase):
	def test(self):
		# Can the game create valid games?
		game = g.Game()
		card = game.generateCard("hearts", "ace")
		self.assertEqual(card, {"color":"hearts", "number": "ace"})
		# Does it assign it the right points
		self.assertEqual(game.points(card), 11)
test = MyTest()
test.test()