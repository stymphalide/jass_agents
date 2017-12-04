import unittest

import game as g

class MyTest(unittest.TestCase):
	def test(self):
		# Can the game create valid games?
		card = g.generateCard("hearts", "ace")
		self.assertEqual(card, {"color":"hearts", "number", "10"})
		# Does it assign it the right points
		self.assertEqual(g.points(card), 11)
		