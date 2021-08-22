import sys

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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for key in self.domains:
            toRemove = []
            for value in self.domains[key]:
                if key.length!=len(value):
                    toRemove.append(value)
            for value in toRemove:
                self.domains[key].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x,y]
        if overlap is None:
            return False
        revised = False
        toRemove = []

        for valuex in self.domains[x]:
            consistent = False
            letter =  valuex[overlap[0]]
            for valuey in self.domains[y]:
                if valuey[overlap[1]] == letter:
                    consistent = True
                    break
            if not consistent:
                toRemove.append(valuex)
        
        for value in toRemove:
            self.domains[x].remove(value)
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
        if arcs is None: # if no initial list of arcs is given
            queue = []
            for variable in self.domains:
                for neighbour in self.crossword.neighbors(variable):
                    queue.append((variable,neighbour))
                    queue.append((neighbour,variable)) # get all arcs in the problem
        else:
            queue = arcs

        changes = 0 # keep track if changes are made to self.domains
        
        while queue:
            arc = queue.pop()
            if self.revise(arc[0],arc[1]): # enforce arc consistency on current arc
                changes+=1
                if len(self.domains[arc[0]]) == 0: # if one variable has an empty domain, return False
                    return False
                for neighbour in self.crossword.neighbors(arc[0]):
                    queue.append((neighbour,arc[0]))
                    queue.append((arc[0],neighbour))
        
        if changes: # if changes were made and all domains are not empty, return True
            return True
        return False # otherwise, return False
        
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # an assignment is complete only if each variable has exactly one value
        if len(assignment)!= len(self.crossword.variables): # check if number of variables is consistent
            return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        vals = set()
        for key in assignment:
            if assignment[key] in vals: # if a value is already used by another variable
                return False
            elif not key.length == len(assignment[key]): # if a value's length does not match that of its variable
                return False
            vals.add(assignment[key]) # add to a set of used variables
            for neighbour in self.crossword.neighbors(key):
                if neighbour in assignment:
                    i,j = self.crossword.overlaps[key,neighbour]
                    if assignment[key][i] != assignment[neighbour][j]: # overlapped cells must contain the same letter
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = list(self.domains[var])
        counts = []
        neighbours = self.crossword.neighbors(var)
        for val in values:
            counts.append([0,val])
            for neighbour in neighbours - set(assignment.keys()):
                if val in self.domains[neighbour]: # if a value is in both var and a neighbour
                    counts[-1][0]+=1
        
        counts.sort(key = lambda x:x[0]) # sort values based on the number of values they restrict

        return [count[1] for count in counts] # return values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        minCount = -1 # the minimum number of values remaining in any variable's domain
        listOfVars = []
        for var in self.crossword.variables:
            if var not in assignment.keys():
                if minCount < 0:
                    minCount = len(self.domains[var])
                    listOfVars.append(var)
                else:
                    if len(self.domains[var])<minCount:
                        minCount = len(self.domains[var])
                        listOfVars.append(var)

        return listOfVars[-1] # the last element is the optimal element based on the heuristic

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # check for completeness
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var,assignment):
            assignment[var] = value # try assigning current optimal value to var
            if self.consistent(assignment): # check for consistency
                result = self.backtrack(assignment)
                if not result is None: # if a non-None result in returned, aka if an assignment is complete
                    return result
                del assignment[var] # if current optimal value results in failure, remove it from assignment
        return None 

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
