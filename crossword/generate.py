import sys
from copy import deepcopy


from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            self.domains[var] = [
                word for word in self.domains[var] if len(word) == var.length]

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return revised

        for word in self.domains[x]:
            if not self.can_overlap(word, self.domains[y], overlap):
                self.domains[x].remove(word)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [k for (k, v) in self.crossword.overlaps.items()
                    if v is not None]

        queue = arcs.copy()

        while len(queue):
            v1, v2 = queue.pop(0)
            if self.revise(v1, v2):
                if len(self.domains[v1]) == 0:
                    return False

                neighbors = [arc for arc in arcs if v1 in arc]
                neighbors = [
                    neighbor for arc in neighbors for neighbor in arc if neighbor != (v1 or v2)]
                neighbors = set(neighbors)

                for var in neighbors:
                    if self.crossword.overlaps[var, v1]:
                        queue.append((var, v1))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment.keys()) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        unique_words = []
        for var in assignment:
            word = assignment[var]
            if len(word) == var.length and word not in unique_words:
                unique_words.append(word)
            else:
                return False

        for v1 in assignment:
            for v2 in assignment:
                if v1 == v2:
                    continue
                overlap = self.crossword.overlaps[v1, v2]
                if overlap is not None:
                    i, j = overlap
                    word1 = assignment[v1]
                    word2 = assignment[v2]
                    if word1[i] != word2[j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        rules_out = {key: 0 for key in self.domains[var]}

        var_arcs = [k for (k, v) in self.crossword.overlaps.items()
                    if v is not None and var in k]

        neighbors = [neighbor for arc in var_arcs for neighbor in arc
                     if neighbor != var and neighbor not in assignment]

        neighbors = set(neighbors)

        for word1 in rules_out:
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap:
                    i, j = overlap
                    for word2 in self.domains[neighbor]:
                        if word1[i] != word2[j]:
                            rules_out[word1] += 1

        least_ruled_out = [pair[0] for pair in sorted(
            rules_out.items(), key=lambda x: x[1])]
        return least_ruled_out

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_domain_vars = []
        min_len = 10e400
        var_to_return = None
        assigned_vars = assignment.keys()
        vars_to_check = [
            var for var in self.crossword.variables if var not in assigned_vars]

        for var in vars_to_check:
            domain_len = len(self.domains[var])
            if domain_len < min_len:
                min_domain_vars = [var]
                min_len = domain_len
            elif domain_len == min_len:
                min_domain_vars.append(var)

        if len(min_domain_vars) > 1:
            highest_degree = 0
            for var in min_domain_vars:
                arcs = [k for (k, v) in self.crossword.overlaps.items()
                        if v is not None and var in k]
                neighbors = [neighbor for arc in arcs for neighbor in arc]
                neighbors = set(neighbors)
                var_degree = len(neighbors)
                if var_degree > highest_degree:
                    var_to_return = var
        else:
            var_to_return = min_domain_vars[0]
        return var_to_return

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                old_domains = deepcopy(self.domains)
                assignment[var] = value
                self.domains[var] = [value]
                inferred = self.infer(assignment, var)
                result = self.backtrack(assignment)

                if result is not None:
                    return result

                self.domains[var] = old_domains[var]
                del assignment[var]
                for inf_var in inferred:
                    self.domains[inf_var] = old_domains[inf_var]

        return None

    def can_overlap(self, word, domain, overlap):
        i, j = overlap
        overlap_y_letters = [d_word[j] for d_word in domain]
        return word[i] in overlap_y_letters

    def infer(self, assignment, var):
        var_arcs = [k for (k, v) in self.crossword.overlaps.items()
                    if v is not None and var in k]

        neighbors = [neighbor for arc in var_arcs for neighbor in arc
                     if neighbor != var and neighbor not in assignment]
        neighbors = set(neighbors)

        var_arcs = [(v1, var) for v1 in neighbors]

        self.ac3(arcs=var_arcs)
        return neighbors


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
