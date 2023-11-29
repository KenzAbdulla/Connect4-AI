#!/usr/bin/env python3
from FourConnect import * # See the FourConnect.py file
import csv
import copy
import math
import time

class GameTreePlayer:

    recursive_count = 0

    def EvaluateGameOne(self,State):
        Table = [[3, 4, 5, 7, 5, 4, 3],
                [4, 6, 8, 10, 8, 6, 4],
                [5, 8, 11, 13, 11, 8, 5],
                [5, 8, 11, 13, 11, 8, 5],
                [4, 6, 8, 10, 8, 6, 4],
                [3, 4, 5, 7, 5, 4, 3]]

        util = 128
        sum = 0
        for i in range(6):
            for j in range(7):
                if (State[i][j] == 0):
                    sum += Table[i][j]
                elif (State[i][j] == 1):
                    sum -= Table[i][j]
        return util + sum

    def count_consecutive_occurrences(self, State, player, consecutive_count):
        
        count = 0
        for i in range(6):
            for j in range(7 - consecutive_count + 1):
                if all(State[i][j + k] == player for k in range(consecutive_count)):
                    count += 1

        for i in range(6 - consecutive_count + 1):
            for j in range(7):
                if all(State[i + k][j] == player for k in range(consecutive_count)):
                    count += 1

        for i in range(6 - consecutive_count + 1):
            for j in range(7 - consecutive_count + 1):
                if all(State[i + k][j + k] == player for k in range(consecutive_count)):
                    count += 1
                if all(State[i + k][j + consecutive_count - 1 - k] == player for k in range(consecutive_count)):
                    count += 1

        return count

    def EvaluateGameTwo(self,State,player):
        score = 0
        countFour = self.count_consecutive_occurrences(State,player,4)
        countThree = self.count_consecutive_occurrences(State, player, 3)
        countTwo = self.count_consecutive_occurrences(State, player, 2)
        countThree = countThree - 2*countFour
        countTwo = countTwo - 3*countFour - 2*countThree
        score = 100*countFour + 7*countThree + 3*countTwo
        return score


    def EvaluateGame(self,State,player):
        score = 0
        center_column = [row[7 // 2] for row in State]
        center_count = center_column.count(player)
        score += center_count * 3
        
        # Horizontal
        for r in range(6):
            row = [int(i) for i in list(State[r])]
            for c in range(7-3):
                window = row[c:c+4]
                
                if window.count(player) == 4:
                    score += 100
                elif window.count(player) == 3 and window.count(0) == 1:
                    score += 7
                elif window.count(player) == 2 and window.count(0) == 2:
                    score += 3

        # Vertical
        for c in range(7):
            col = [int(i) for i in list([row[c] for row in State])]
            for r in range(6-3):
                window = col[r:r+4]
                
                if window.count(player) == 4:
                    score += 100   
                elif window.count(player) == 3 and window.count(0) == 1:
                    score += 7
                elif window.count(player) == 2 and window.count(0) == 2:
                    score += 3

        # Positive sloped diagonal
        for r in range(6-3):
            for c in range(7-3):
                window = [State[r+i][c+i] for i in range(4)]
                
                if window.count(player) == 4:
                    score += 100
                elif window.count(player) == 3 and window.count(0) == 1:
                    score += 7
                elif window.count(player) == 2 and window.count(0) == 2:
                    score += 3

        # Negative sloped diagonal
        for r in range(6-3):
            for c in range(7-3):
                window = [State[r+3-i][c+i] for i in range(4)]
                
                if window.count(player) == 4:
                    score += 100
                elif window.count(player) == 3 and window.count(0) == 1:
                    score += 7
                elif window.count(player) == 2 and window.count(0) == 2:
                    score += 3
                    
        return score

    def _ContainValidCell(self,State,col):
        cRow = -1
        c=col
        for r in range(5,-1,-1):
            if State[r][c]==0:
                cRow=r
                break
        return cRow

    def _get_valid_columns(self,State):
        valid_columns = []
        for col in range(7):
            if self._ContainValidCell(State,col) != -1:
                valid_columns.append(col)
        return valid_columns

    def move_order(self,columns): #move_ordering
        order_list = [3,2,4,1,5,0,6]
        ordered_columns = []
        for i in order_list:
            if i in columns:
                ordered_columns.append(i)
        return ordered_columns


    def check_four_positions(self,State, player, positions):
        return all(State[row][col] == player for row, col in positions)

    def winning_move(self,State, player):
        # Check for a win in horizontal positions
        for c in range(len(State[0]) - 3):
            for r in range(len(State)):
                if self.check_four_positions(State, player, [(r, c + i) for i in range(4)]):
                    return True

        # Check for a win in vertical positions
        for c in range(len(State[0])):
            for r in range(len(State) - 3):
                if self.check_four_positions(State, player, [(r + i, c) for i in range(4)]):
                    return True

        # Check for a win in positively sloped diagonals
        for c in range(len(State[0]) - 3):
            for r in range(len(State) - 3):
                if self.check_four_positions(State, player, [(r + i, c + i) for i in range(4)]):
                    return True

        # Check for a win in negatively sloped diagonals
        for c in range(len(State[0]) - 3):
            for r in range(3, len(State)):
                if self.check_four_positions(State, player, [(r - i, c + i) for i in range(4)]):
                    return True

        return False
        
    def is_terminal(self,State):
        return self.winning_move(State, 1) or self.winning_move(State, 2) or len(self._get_valid_columns(State)) == 0
        

    def minimax(self,State,depth,alpha,beta,maximizingPlayer):
        GameTreePlayer.recursive_count += 1
        valid_columns = self._get_valid_columns(State)
        ordered_columns = self.move_order(valid_columns)

        if depth == 0 or self.is_terminal(State):
            if self.is_terminal(State):
                if self.winning_move(State, 2):
                    return (10000000000,None)
                elif self.winning_move(State, 1):
                    return (-1000000000,None)
                else:
                    return (0,None)
                    
            else:
                return ((self.EvaluateGame(State,2) - self.EvaluateGame(State,1)),None)

        if maximizingPlayer:
            value = -100000000000
            column = 0
            for col in ordered_columns:
                row = self._ContainValidCell(State,col)
                StateCopy = copy.deepcopy(State)
                StateCopy[row][col] = 2
                Score = self.minimax(StateCopy,depth-1,alpha,beta,False)[0]
                if Score > value:
                    value = Score
                    column = col
                    
                alpha = max(alpha,value) 
                if alpha >= beta:
                    break
                
            return value,column

        else:
            value = 100000000000
            column = 0
            for col in ordered_columns:
                row = self._ContainValidCell(State,col)
                StateCopy = copy.deepcopy(State)
                StateCopy[row][col] = 1
                Score = self.minimax(StateCopy,depth-1,alpha,beta,True)[0]
                if Score < value:
                    value = Score
                    column = col
                    
                beta = min(beta,value)
                if alpha >= beta:
                    break
                
            return value,column



    def FindBestAction(self,currentState):
        bestAction = self.minimax(currentState,5,-math.inf,math.inf,True)[1]
        return bestAction

        """
        Modify this function to search the GameTree instead of getting input from the keyState.
        The currentState of the game is passed to the function.
        currentState[0][0] refers to the top-left corner position.
        currentState[5][6] refers to the bottom-right corner position.
        Action refers to the column in which you decide to put your coin. The actions (and columns) are numbered from left to right.
        Action 0 is refers to the left-most column and action 6 refers to the right-most column.
        """
        """
        bestAction = input("Take action (0-6) : ")
        bestAction = int(bestAction)
        return bestAction
        """


def LoadTestcaseStateFromCSVfile():
    testcaseState=list()

    with open('testcase.csv', 'r') as read_obj: 
        csvReader = csv.reader(read_obj)
        for csvRow in csvReader:
            row = [int(r) for r in csvRow]
            testcaseState.append(row)
        return testcaseState


def PlayGame():
    fourConnect = FourConnect()
    fourConnect.PrintGameState()
    gameTree = GameTreePlayer()
    
    move=0
    while move<42: #At most 42 moves are possible
        if move%2 == 0: #Myopic player always moves first
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
            
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner!=None:
            break
    
    """
    You can add your code here to count the number of wins average number of moves etc.
    You can modify the PlayGame() function to play multiple games if required.
    """
    if fourConnect.winner==None:
        print("Game is drawn.")
    else:
        print("Winner : Player {0}\n".format(fourConnect.winner))
    print("Moves : {0}".format(move))
    return fourConnect.winner,move,gameTree.recursive_count

def RunTestCase():
    """
    This procedure reads the state in testcase.csv file and start the game.
    Player 2 moves first. Player 2 must win in 5 moves to pass the testcase; Otherwise, the program fails to pass the testcase.
    """
    
    fourConnect = FourConnect()
    gameTree = GameTreePlayer()
    testcaseState = LoadTestcaseStateFromCSVfile()
    fourConnect.SetCurrentState(testcaseState)
    fourConnect.PrintGameState()

    move=0
    while move<5: #Player 2 must win in 5 moves
        if move%2 == 1: 
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner!=None:
            break
    
    print("Roll no : 2021A7PS2664G") #Put your roll number here
    
    if fourConnect.winner==2:
        print("Player 2 has won. Testcase passed.")
    else:
        print("Player 2 could not win in 5 moves. Testcase failed.")
    print("Moves : {0}".format(move))
    
    

def main():
    
    
    wincount = 0
    avg_moves = 0
    time_taken = 0
    for i in range(50):
        start = time.time()
        winner,move,count  = PlayGame()
        end = time.time()
        avg_moves += move
        time_taken += end - start
        if winner == 2:
            wincount += 1

    #print(wincount,avg_moves/50,time_taken/50,count/50)
    
    """
    You can modify PlayGame function for writing the report
    Modify the FindBestAction in GameTreePlayer class to implement Game tree search.
    You can add functions to GameTreePlayer class as required.
    """

    """
        The above code (PlayGame()) must be COMMENTED while submitting this program.
        The below code (RunTestCase()) must be UNCOMMENTED while submitting this program.
        Output should be your rollnumber and the bestAction.
        See the code for RunTestCase() to understand what is expected.
    """
    
    #RunTestCase()


if __name__=='__main__':
    main()
