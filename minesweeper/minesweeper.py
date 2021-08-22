
import itertools
import random

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
        if self.count == len(self.cells):
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
    
        self.cells.remove(cell)
        self.count-=1
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)
        return

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

    def all_neighbours(self,cell):
        """
        Returns an array of all neighbouring cells of a specific cell
        Will not include cells that are outside the board
        """
        neighbours = []
        for i in range(cell[0]-1,cell[0]+2):
            for j in range(cell[1]-1,cell[1]+2):
                if i == cell[0] and j == cell[1]:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbours.append((i,j))
        return neighbours

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        """1"""
        self.moves_made.add(cell)

        """2"""
        self.safes.add(cell)

        """3"""
        newInfo = Sentence(self.all_neighbours(cell),count)

        """4"""
        for safe in self.safes:
            newInfo.mark_safe(safe)

        if count==0:    #all safes
            for nei in self.all_neighbours(cell):
                self.mark_safe(nei)
                newInfo.mark_safe(nei)
        elif count == len(self.all_neighbours(cell)): #all mines
            for nei in self.all_neighbours(cell):
                self.mark_mine(nei)
                newInfo.mark_mine(nei)

        self.knowledge.append(newInfo) #update knowledge
        
        # figure out which cells can be determined as new safes, new mines
        newmines = set()
        newsafes = set()

        # if the newly-appended newInfo results in any known new safes or new mines
        for sentence in self.knowledge:
            for safe in sentence.known_safes():
                newsafes.add(safe)
            for mine in sentence.known_mines():
                newmines.add(mine)
        
        # update rest of self.knowledge with already known safes and mines
        self.safes.update(newsafes)
        self.mines.update(newmines)
        for safe in self.safes:
            self.mark_safe(safe)
        for mine in self.mines:
            self.mark_mine(mine)

        """5"""
        while True:
            changes = 0
            newSentences = []
            toDelete = []
            
            for sentence in self.knowledge:
                new_safes = sentence.known_safes() - self.safes
                new_mines = sentence.known_mines() - self.mines

                changes+=len(new_safes) + len(new_mines)

                for safe in new_safes:
                    self.mark_safe(safe)
                for mine in new_mines:
                    self.mark_mine(mine)

            

            for info1 in self.knowledge:
                if info1.cells == set():
                    continue
                for info2 in self.knowledge:
                    if info2 == info1 or info2.cells == set():
                        continue
                    if info1.cells.issubset(info2.cells):
                        changes+=1
                        newSentences.append(Sentence(info2.cells.difference(info1.cells), info2.count-info1.count))
                        toDelete.append(info2.cells)

            self.knowledge = [item for item in self.knowledge if item.cells not in toDelete]
            for sentence in newSentences:
                self.knowledge.append(sentence)
            
            if changes == 0:
                break
        self.knowledge = [item for item in self.knowledge if item.cells != set()]
        print(self.safes-self.moves_made)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None
        

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves_left = set(itertools.product(range(0, self.height), range(0, self.width)))
        moves_left = moves_left - self.mines - self.moves_made

        if moves_left:
            return random.choice(tuple(moves_left))
        else:
            return None
