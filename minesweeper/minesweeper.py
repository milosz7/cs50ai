import itertools
import random
from copy import deepcopy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)
        self.safes.add(cell)

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        self.add_new_sentence(cell, count)
        self.resolve_sentences()
        self.cleanup_knowledge()
        self.infer_sentences()

    def cleanup_knowledge(self):
        """
        Removes sentences that have no cells in them from knowledge base.
        Should be called after resolving.
        """
        self.knowledge = [sentence for sentence in self.knowledge if len(sentence.cells)]

    def resolve_sentences(self):
        """
        Function for extracting data from sentences in knowledge base.
        """
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            known_safes = sentence.known_safes()
            if known_mines is not None:
                for sentence in self.knowledge:
                    for cell in known_mines.copy():
                        self.mines.add(cell)
                        sentence.mark_mine(cell)
            if known_safes is not None:
                for sentence in self.knowledge:
                    for cell in known_safes.copy():
                        self.safes.add(cell)   
                        sentence.mark_safe(cell)

    def infer_sentences(self):
        """
        Function for infering new sentences based on knowledge base.
        """
        updated_knowledge = deepcopy(self.knowledge)
        knowledge_len = len(self.knowledge)

        for i in range(knowledge_len):
            s1 = self.knowledge[i]

            for j in range(i + 1, knowledge_len):
                s2 = self.knowledge[j]
                
                if s1.cells.issubset(s2.cells):
                    diff = s2.cells.difference(s1.cells)
                    count = abs(s1.count - s2.count)
                    
                    if s1 in updated_knowledge:
                        updated_knowledge.remove(s1)
                    
                    if len(diff):
                        updated_knowledge.append(Sentence(diff, count))

                elif s2.cells.issubset(s1.cells):
                    diff = s1.cells.difference(s2.cells)
                    count = abs(s1.count - s2.count)

                    if s2 in updated_knowledge:
                        updated_knowledge.remove(s2)

                    if len(diff):
                        updated_knowledge.append(Sentence(diff, count))
                
        self.knowledge = updated_knowledge

    def add_new_sentence(self, cell, count):
        """
        Adds a new sentence to the knowledge base based on last clicked cell.
        """
        i, j = cell
        cell_neighbors = {(x, y) for x in range (i - 1, i + 2) \
                                 for y in range(j - 1, j + 2) \
                                 if  self.height > x >= 0 and
                                     self.width > y >= 0
                         }
        
        unknown_neighbors = {x for x in cell_neighbors if x not in self.safes.union(self.mines)}

        #Adjusting the count of the sentence using known mines
        for cell in cell_neighbors:
            if cell in self.mines:
                count -= 1

        new_sentence = Sentence(unknown_neighbors, count)
        if new_sentence not in self.knowledge and len(unknown_neighbors):
            self.knowledge.append(new_sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made.union(self.mines):
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = list({(i, j) for i in range(self.height) \
                                      for j in range(self.width)  \
                                      if (i, j) not in self.moves_made.union(self.mines)})
        if len(possible_moves) == 0:
            return None
        move_idx = random.randrange(len(possible_moves))
        return possible_moves[move_idx]
