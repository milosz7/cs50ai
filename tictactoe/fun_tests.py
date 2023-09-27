from tictactoe import player, actions, result, winner, terminal, utility
import unittest

boards = [[["X", None, None],
           [None, None, "O"],
           ["X", None, None]],

          [[None, None, None],
           [None, None, None],
           [None, None, None]],

          [["X", None, "O"],
           [None, None, "O"],
           ["X", None, None]],

          [["X", None, "O"],
           [None, "X", "O"],
           ["X", None, "O"]],

          [["X", None, "O"],
           [None, "O", "O"],
           ["X", "X", "X"]],

          [["X", "X", "O"],
           ["X", "O", "O"],
           ["O", "X", "X"]],

          [["O", "X", "O"],
           ["X", "X", "O"],
           ["X", "O", "X"]]]


class TicTacToeTests(unittest.TestCase):

    def test_player(self):
        self.assertEqual(player(boards[0]), "O")
        self.assertEqual(player(boards[1]), "X")
        self.assertEqual(player(boards[2]), "X")

    def test_actions(self):
        self.assertEqual(actions(boards[0]), {
                         (0, 1), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2)})
        self.assertEqual(actions(boards[1]), {
                         (x, y) for x in range(3) for y in range(3)})
        self.assertEqual(result(boards[0], (0, 2)), [["X", None, "O"],
                                                     [None, None, "O"],
                                                     ["X", None, None]])
        self.assertEqual(result(boards[1], (0, 2)), [[None, None, "X"],
                                                     [None, None, None],
                                                     [None, None, None]])

    def test_winner(self):
        self.assertEqual(winner(boards[0]), None)
        self.assertEqual(winner(boards[3]), "O")
        self.assertEqual(winner(boards[4]), "X")
        self.assertEqual(winner(boards[5]), "O")

    def test_terminal(self):
        self.assertEqual(terminal(boards[0]), False)
        self.assertEqual(terminal(boards[4]), True)
        self.assertEqual(terminal(boards[5]), True)
        self.assertEqual(terminal(boards[6]), True)

    def test_utility(self):
        self.assertEqual(utility(boards[4]), 1)
        self.assertEqual(utility(boards[5]), -1)
        self.assertEqual(utility(boards[6]), 0)


if __name__ == '__main__':
    unittest.main()
