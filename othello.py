#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  Othello
#  othello.py
#  
#  Created by Brian Mason on 3.3.08.
#  Copyright (c) 2008 Brian Mason. All rights reserved.
#
#  Wood graphic from http://www.time2photoshop.com/create-a-wood-texture.
#  All other graphics created by myself in Adobe Photoshop CS3.
#  Button class adapted from Button class that was included with the textbook with some methods removed, added, or changed.
#
#  NOTE: This file uses a slightly edited version of the graphics module that allows an image's undraw method to be called when it has not yet been drawn without crashing the program.
#  It will not work with the normal version of the graphics module, so use the one provided.

import graphics
from time import sleep

#  These are declared here because I got sick of putting quotation marks around white and black, among other things.
white = 0
black = 1
textColor = graphics.color_rgb(229, 229, 229)
whitePath = 'othello_graphics/white.gif'
blackPath = 'othello_graphics/black.gif'
boardPath = 'othello_graphics/board.gif'
bottomPath = 'othello_graphics/bottomBar.gif'
movePath = 'othello_graphics/move.gif'
blackTokenPath = 'othello_graphics/blackToken.gif'
whiteTokenPath = 'othello_graphics/whiteToken.gif'
choosePlayerPath = 'othello_graphics/playerWindow.gif'
playAgainPath = 'othello_graphics/playAgain.gif'
quitPath = 'othello_graphics/quitButton.gif'
reallyQuitPath = 'othello_graphics/reallyQuit.gif'
winMessagePath = 'othello_graphics/winMessage.gif'
difficultyPath = 'othello_graphics/difficultyWindow.gif'

#  These are various board weight schemes.
#  They can't be changed in the game, but deleting one line of code and moving it somehwere else lets you do so.
#  Just assign one of them to the global variable 'boardWeights'
#  It will change what happens.

#  http://norvig.com/paip/othello.lisp
#  Note: I got this from there, I didn't get any of the AI from there.
[[120, -20, 20,  5,  5, 20, -20, 120], \
                [-20, -40, -5, -5, -5, -5, -40, -20], \
                [ 20,  -5, 15,  3,  3, 15,  -5,  20], \
                [  5,  -5,  3,  3,  3,  3,  -5,   5], \
                [  5,  -5,  3,  3,  3,  3,  -5,   5], \
                [ 20,  -5, 15,  3,  3, 15,  -5,  20], \
                [-20, -40, -5, -5, -5, -5, -40, -20], \
                [120, -20, 20,  5,  5, 20, -20, 120]]

#  http://www.generation5.org/content/2002/game02.asp
boardWeights = [[50, -1, 5, 2, 2, 5, -1, 50], \
                [-1,-10, 1, 1, 1, 1,-10, -1], \
                [ 5,  1, 1, 1, 1, 1,  1,  5], \
                [ 2,  1, 1, 0, 0, 1,  1,  2], \
                [ 2,  1, 1, 0, 0, 1,  1,  2], \
                [ 5,  1, 1, 1, 1, 1,  1,  5], \
                [-1,-10, 1, 1, 1, 1,-10, -1], \
                [50, -1, 5, 2, 2, 5, -1, 50]]

#  http://vying.org/blog/2007/04/othello-bots
[[50, -9, -6, -6, -6, -6, -9, 50], \
                [-9, -9, -5, -5, -5, -5, -9, -9], \
                [-6, -5, -4, -2, -2, -4, -5, -6], \
                [-6, -5, -2, -1, -1, -2, -5, -6], \
                [-6, -5, -2, -1, -1, -2, -5, -6], \
                [-6, -5, -4, -2, -2, -4, -5, -6], \
                [-9, -9, -5, -5, -5, -5, -9, -9], \
                [50, -9, -6, -6, -6, -6, -9, 50]]


#  The game class performs functions related to starting the game, displaying info, advancing turns, delegating finding out whether any players can move, and ending the game.
#  Objects from all the other classes are contained within the game object.
class Game:
    def __init__(self):
        self.gameBegun = False   # Used for creating the board to tell if graphics need to be undrawn.
        self.displaySet = False  # Used by the infoDisplayUpdate to see if it needs to create the variables or can reuse them.

        self.board = Board(self, 8, 8)
        
        #  This button allows people to quit during play.
        self.constantQuitButtonGraphic = graphics.Image(graphics.Point(565, 665), quitPath)
        self.constantQuitButton = Button(self.board.canvas, graphics.Point(541, 652), graphics.Point(625, 681))
        
        self.restartGame()
        
        self.gameBegun = True
        
    #  Continues the game until it is over. With messages about players, continuing, etc.
    def playController(self):
        play = True
        #  Creates the graphics that will be used between each game for input.
        continueButton = Button(self.board.canvas, graphics.Point(318, 654), graphics.Point(385, 678))
        quitButton = Button(self.board.canvas, graphics.Point(407, 654), graphics.Point(474, 678))
        continueButton.deactivate()
        quitButton.deactivate()
        playAgain = graphics.Image(graphics.Point(320, 665), playAgainPath)

        while play:
            #  Update score display.
            self.infoDisplayUpdate()
            #  This while loop will run till the end of the game.
            while not self.gameOver():
                self.turn()
            self.findWinner()
            #  Asks to continue from here on, and if yes will go back to the while play loop.
            play = None
            playAgain.draw(self.board.canvas)
            while play == None:
                continueButton.activate()
                quitButton.activate()
                click = waitForClick(self.board.canvas)
                if quitButton.clicked(click):
                    play = False
                elif continueButton.clicked(click):
                    play = True
                    continueButton.deactivate()
                    quitButton.deactivate()
                    playAgain.undraw()
                    self.restartGame()
                else:
                    play = None
        
    #  Keeps the original game and board objects but resets players, pieces, buttons, and score.
    def restartGame(self):
        #  Resets all the info.
        self.board.resetBoard(self)
        #  And updates the display.
        self.infoDisplayUpdate()
        
    #  We'll have a list that will have 2 elements for the 2 players.
    #  This determines what kind of player they should be (AI, human) and adds them.
    def createPlayers(self):
        numPlayers = None
        
        #  Dialog with 3 buttons for types of game.
        playerDialog = graphics.Image(graphics.Point(320, 320), choosePlayerPath)
        playerDialog.draw(self.board.canvas)
        #  Redraws it if it was undrawn for a computer/computer game.
        if self.displaySet:
            if self.activePlayer.getDrawn():
                self.activePlayer.undraw()
        if not self.constantQuitButtonGraphic.getDrawn():
            self.constantQuitButtonGraphic.draw(self.board.canvas)
        
        #  These are the actual buttons for choosing player number.
        buttonComputerComputer = Button(self.board.canvas, graphics.Point(205, 279), graphics.Point(263, 337))
        buttonHumanComputer = Button(self.board.canvas, graphics.Point(294, 279), graphics.Point(352, 337))
        buttonHumanHuman = Button(self.board.canvas, graphics.Point(382, 279), graphics.Point(440, 337))
        while numPlayers == None:
            click = waitForClick(self.board.canvas)
            if buttonComputerComputer.clicked(click):
                numPlayers = 0
            elif buttonHumanComputer.clicked(click):
                numPlayers = 1
            elif buttonHumanHuman.clicked(click):
                numPlayers = 2
            else:
                numPlayers = None
            
            self.quitButtonTest(click)
            
        if numPlayers < 2:
            difficultyDialog = graphics.Image(graphics.Point(320, 320), difficultyPath)
            difficultyDialog.draw(self.board.canvas)
            
            #  These are the actual buttons for choosing difficulty number.
            buttonEasy = Button(self.board.canvas, graphics.Point(205, 279), graphics.Point(263, 337))
            buttonMedium = Button(self.board.canvas, graphics.Point(294, 279), graphics.Point(352, 337))
            buttonHard = Button(self.board.canvas, graphics.Point(382, 279), graphics.Point(440, 337))
            difficulty = None
            while difficulty == None:
                click = waitForClick(self.board.canvas)
                if buttonEasy.clicked(click):
                    difficulty = 1
                elif buttonMedium.clicked(click):
                    difficulty = 2
                elif buttonHard.clicked(click):
                    difficulty = 3
                else:
                    difficulty = None
                    
                self.quitButtonTest(click)
        
        playerDialog.undraw()
        difficultyDialog.undraw()
        
        #  Creates a list of players based on the information from the user.
        self.players = []
        if numPlayers >= 1:
            human1 = Player(black, True)
            self.players.append(human1)
        if numPlayers >= 2:
            human2 = Player(white, False)
            self.players.append(human2)
        if numPlayers == 0:
            computer2 = ComputerPlayer(black, True, difficulty)
            self.players.append(computer2)
            #  Undraw since the button doesn't work in computer/computer games.
            self.constantQuitButtonGraphic.undraw()
        if numPlayers <= 1:
            computer1 = ComputerPlayer(white, False, difficulty)
            self.players.append(computer1)
    
    #  Finds out whose turn it is and tells that Player to take their turn.
    #  The checkForValidMoves() function is called here so that the correct buttons will be activated for clicking.
    def turn(self):
        for player in self.players:
            if player.getTurnMarker():
                self.board.checkForValidMoves(player)
                self.infoDisplayUpdate()
                player.turn(self)
                for player in self.players:
                    player.switchTurn()
                            
    #  Tested before each turn to see if the board is full or if anyone has valid moves. Total piece number must be less than the number possible, and at least one person must have a move.
    def gameOver(self):
        return not (self.board.numberPieces < self.board.height * self.board.width and (self.players[0].canMove(self.board) or self.players[1].canMove(self.board)))
                
    #  Called at the end to count pieces.
    def findWinner(self):
        #  Figures out who the winner is, or if it's a tie, based on number of pieces on the board.
        if self.board.getScore(self.players[0], self.board.boardArray) > self.board.getScore(self.players[1], self.board.boardArray):
            winner, count = self.players[0].getColor(), self.board.getScore(self.players[0], self.board.boardArray)
        elif self.board.getScore(self.players[1], self.board.boardArray) > self.board.getScore(self.players[0], self.board.boardArray):
            winner, count = self.players[1].getColor(), self.board.getScore(self.players[1], self.board.boardArray)
        else:
            winner, count = -1, -1
        
        if winner == 0:
            winnerColor = 'white'
        elif winner == 1:
            winnerColor = 'black'
        #  Creates the strings. The shadow is the same text off-set slightly and black.
        if winner == -1 and count == -1:
            winString = "It’s a draw!"
        else:
            winString = 'The ' + winnerColor + ' player wins with ' + str(count) + ' pieces!'
        self.winMessageBackground = graphics.Image(graphics.Point(320, 321), winMessagePath)
        self.winShadow = graphics.Text(graphics.Point(321, 321), winString)
        self.winMessage = graphics.Text(graphics.Point(320, 320), winString)
        self.winShadow.setSize(36)
        self.winMessage.setSize(36)
        self.winMessage.setTextColor(textColor)
        self.winMessageBackground.draw(self.board.canvas)
        self.winShadow.draw(self.board.canvas)
        self.winMessage.draw(self.board.canvas)
        
    #  Shows information at the bottom of the board window.
    def infoDisplayUpdate(self):
        player1Y = 658
        player2Y = 678
        activePlayerY = 668
        scoreX = 147
        #  The first time the info display is created these must be created. After that they are merely updated.
        if not self.displaySet:
            #  Sets up a button that will allow you to quit during a game.
            
            self.player1 = graphics.Text(graphics.Point(75, player1Y), 'Player 1 (black):')
            self.player2 = graphics.Text(graphics.Point(75, player2Y), 'Player 2 (white):')
            self.player1.setSize(14)
            self.player2.setSize(14)
            self.player1.setTextColor(textColor)
            self.player2.setTextColor(textColor)
            self.player1.setFace('helvetica')
            self.player2.setFace('helvetica')
            self.player1.draw(self.board.canvas)
            self.player2.draw(self.board.canvas)
            
            self.player1Score = graphics.Text(graphics.Point(scoreX, player1Y), self.board.getScore(self.players[0], self.board.boardArray))
            self.player2Score = graphics.Text(graphics.Point(scoreX, player2Y), self.board.getScore(self.players[1], self.board.boardArray))

            self.activePlayer = graphics.Text(graphics.Point(600, activePlayerY), 'Empty')
            
            self.displaySet = True
            
        # They are updated here.
        self.player1Score.undraw()
        self.player2Score.undraw()
        self.player1Score = graphics.Text(graphics.Point(scoreX, player1Y), self.board.getScore(self.players[0], self.board.boardArray))
        self.player2Score = graphics.Text(graphics.Point(scoreX, player2Y), self.board.getScore(self.players[1], self.board.boardArray))
        self.player1Score.setSize(14)
        self.player2Score.setSize(14)
        self.player1Score.setTextColor(textColor)
        self.player2Score.setTextColor(textColor)
        self.player1Score.setFace('helvetica')
        self.player2Score.setFace('helvetica')
        self.player1Score.draw(self.board.canvas)
        self.player2Score.draw(self.board.canvas)
        self.activePlayer.undraw()
        #  Draws either a black or white token to represent whose turn it is.
        for player in self.players:
            if player.getTurnMarker():
                if player.getColor() == black:
                    self.activePlayer = graphics.Image(graphics.Point(500, 665), blackTokenPath)
                else:
                    self.activePlayer = graphics.Image(graphics.Point(500, 665), whiteTokenPath)
                self.activePlayer.draw(self.board.canvas)

    def quitButtonTest(self, click):
        #  Tests to see if the quit button is clicked.
        if self.constantQuitButton.clicked(click):
            quitButton = Button(self.board.canvas, graphics.Point(318, 654), graphics.Point(385, 678))
            continueButton = Button(self.board.canvas, graphics.Point(407, 654), graphics.Point(474, 678))
            continueGraphic = graphics.Image(graphics.Point(320, 665), reallyQuitPath)
            continueGraphic.draw(self.board.canvas)
            quitClickTest = False
            #  Makes sure the player wants to quit.
            while not quitClickTest:
                quitClick = waitForClick(self.board.canvas)
                if quitButton.clicked(quitClick):
                    quit()
                elif continueButton.clicked(quitClick):
                    quitClickTest = True
                    continueGraphic.undraw()
            
#  The board object draws the board, keeps track of where pieces are, handles placement of pieces, and contains the code for handling flipping pieces and determining if pieces can be flipped.
#  Pieces, buttons for mouse actions, and the board itself are within the board object.
class Board:
    def __init__(self, game, height, width):
        self.pieces = []
        self.height = height
        self.width = width
        self.numberPieces = 0
        self.draw()
    
    #  If the board's info exists from a previous game reset it.
    #  If this is the first game and it hasn't been created yet, create it.
    def resetBoard(self, game):
        #  If the board isn't empty undraws the graphics from it.
        #  This must happen before creating players only because of graphics.
        #  The graphics have fake transparencies that doesn't work if there is anything in the background.
        if game.gameBegun:
            #  Gets rid of all the pieces graphics from the previous game.
            for piece in self.pieces:
                undrawPiece(piece)
            #  And any open move markers.
            for button in self.buttons:
                if button.drawn:
                    undrawButton(button)
            #  And the info stuff.
            game.winMessage.undraw()
            game.winShadow.undraw()
            game.winMessageBackground.undraw()
            self.pieces = []
            self.numberPieces = 0
        
        #  Erased previous players as well as creating new ones.
        game.createPlayers()
        
        #  Same with the board information.
        self.boardArray = []
        for x in range(self.width):
            self.boardArray.append([])
            for y in range(self.height):
                self.boardArray[x].append('')
        self.arrayCreated = True
        
        #  And the buttons of course.
        self.buttons = []
        for i in range(self.height):
            for j in range(self.width):
                topLeft = graphics.Point(80 * j, 80 * i)
                bottomRight = graphics.Point(80 * (j + 1), 80 * (i + 1))
                self.buttons.append(Button(self.canvas, topLeft, bottomRight, j, i, movePath))
                
        #  The initial setup of 4 pieces in the middle:
        self.addPiece(white, 3, 3)
        self.addPiece(black, 4, 3)
        self.addPiece(black, 3, 4)
        self.addPiece(white, 4, 4)
        
    #  Called at the beginning of each turn to find out where the player can move.
    #  Calls other functions that will eventually activate the correct buttons, but for now all are deactivated.
    def checkForValidMoves(self, player):
        #  Deativates all buttons at the beginning, they will be activated soon if you can move there.
        for button in self.buttons:
            button.deactivate()
        #  Cycle through all the items in the board array.
        for y in range(self.height):
            for x in range(self.width):
                #  Only checks places where there are pieces.
                if self.boardArray[x][y] == '':                    
                    #  Gets the bordering pieces and cycles through them.
                    bordering = self.getBordering(x, y, self.boardArray)
                    for borderPiece in bordering:
                        #  Makes sure everything is marked unflippable so that there aren't false positives for moves.
                        for piece in self.pieces:
                            piece.makeFlippable(False)
                        if borderPiece != '' and borderPiece.getColor() != player.getColor():
                            direction = self.getCheckDirection(x, y, borderPiece.getX(), borderPiece.getY())
                            self.checkMakeFlippable(borderPiece, direction, self.boardArray)
                        #  If there are any flippable pieces after running through the whole border, the original space is activated.
                        for piece in self.pieces:
                            if piece.getFlippable():
                                self.buttons[y * 8 + x].activate()
                            #  Deativates, so none are flippable after this.
                            piece.makeFlippable(False)
    
    #  Just gives the direction to follow based on old and new coordinates.
    def getCheckDirection(self, x, y, newX, newY):
        return [newX - x, newY - y]
            
    #  Returns all adjacent spaces that are within the bounds of the board and have a piece in them.
    def getBordering(self, x, y, board):
        bordering = []
        for ix in [x - 1, x, x + 1]:
            for iy in [y - 1, y, y + 1]:
                if ix >= 0 and ix < self.width and iy >= 0 and iy < self.height and [ix, iy] != [x, y] and board[ix][iy] != '':
                    bordering.append(board[ix][iy])
        return bordering
                
    #  Takes a starting point and direction and marks pieces as flippable when appropriate.
    def checkMakeFlippable(self, piece, direction, board):
        x = piece.getX()
        y = piece.getY()
        #  Returns false if there is the edge of the board (can't flip) or empty space (don't flip yet).
        if x + direction[0] < 0 or x + direction[0] >= self.width or y + direction[1] < 0 or y + direction[1] >= self.height or board[x + direction[0]][y + direction[1]] == '':
            return False
        #  Returns true and changes the color if there is an opposite color after the piece.
        elif board[x + direction[0]][y + direction[1]].getColor() != piece.getColor():
            piece.makeFlippable(True)
            return True
        #  If it is followed by the same color, it calls the function recursively and to find out if there is
        #  an opposite color farther down the line. If there is it becomes flippable.
        elif self.checkMakeFlippable(board[x + direction[0]][y + direction[1]], direction, board):
            piece.makeFlippable(True)
            return True
        #  If there is same color afterwards but no need to flip this will happen.
        else:
            return False
            
    def getAvailableMoves(self):
        availableMoves = []
        for button in self.buttons:
            if button.getState():
                availableMoves.append(button)
        return availableMoves

    #  This and the following method are the basis of the new AI.
    #  The computer generates multiple boards and does moves on them in the background to a depth specified by the AI.
    #  The it calculates the desirousness of that board based on values for certain squares and moves accordingly.
    def getBestMove(self, board, level, playerColor):
        if playerColor == black:
            secondPlayerColor = white
        else:
            secondPlayerColor = black
            
        #  Initializes to junk values that will be replaced in the case of there being any valid moves.
        currentBest = [0, -1000000000]
        
        availableMoves = self.checkForValidHypotheticalMoves(board, ComputerPlayer(playerColor, True, level))
        
        if availableMoves == [] and self.checkForValidHypotheticalMoves(board, ComputerPlayer(secondPlayerColor, True, level)) != []:
            return self.getBestMoveOpponent(board, level, secondPlayerColor, playerColor)            

        #  Create a copy of the board array.
        for move in availableMoves:
            hypotheticalBoard = []
            for x in range(self.width):
                hypotheticalBoard.append([])
                for y in range(self.height):
                    hypotheticalBoard[x].append('')
                    
            #  Copies all the information from the original board to the new one.
            for x in range(self.getWidth()):
                for y in range(self.getHeight()):
                    if board[x][y] == '':
                        hypotheticalBoard[x][y] = ''
                    else:
                        hypotheticalBoard[x][y] = board[x][y].copy()

            #  Attempts to make each move that is possible.
            self.makeHypotheticalMove(move[0], move[1], hypotheticalBoard, ComputerPlayer(playerColor, True, level))
            
            #  If the recursion depth has not reached the pre-specified maximum call the equivilent method but for the opposing player.
            if level > 0:
                score = self.getBestMoveOpponent(hypotheticalBoard, level - 1, secondPlayerColor, playerColor)[2]
            #  if it has reached the correct depth return the score.
            else:
                score = self.getBoardScore(hypotheticalBoard, playerColor)
                
            #  If the score is better than those already tested use the new one.
            if score > currentBest[1]:
                currentBest = [move, score]
            
            #  Makes sure that the computer will always choose to win and always try not to lose.
            if availableMoves == [] and self.checkForValidHypotheticalMoves(board, ComputerPlayer(secondPlayerColor, True, level)) == []:
                if self.getScore(ComputerPlayer(playerColor, True, level), board) > self.getScore(ComputerPlayer(secondPlayerColor, True, level), board):
                    currentBest = [move, 1000000000]
                elif self.getScore(ComputerPlayer(playerColor, True, level), board) > self.getScore(ComputerPlayer(secondPlayerColor, True, level), board):
                    currentBest = [move, -1000000000]
                else:
                    pass
                
        return currentBest
        
    #  Effectively the same method as above, but for the opposing player.
    #  This means that a move that ranks as good will be returned as bad and vice versa.
    def getBestMoveOpponent(self, board, level, playerColor, originalPlayerColor):
        if playerColor == black:
            secondPlayerColor = white
        else:
            secondPlayerColor = black
            
        currentBest = [0, 1000000000, -1000000000]
        
        availableMoves = self.checkForValidHypotheticalMoves(board, ComputerPlayer(playerColor, True, level))
        
        if availableMoves == [] and self.checkForValidHypotheticalMoves(board, ComputerPlayer(secondPlayerColor, True, level)) != []:
            score = self.getBestMove(board, level, originalPlayerColor)
            return [score[0], 0, score[1]]

        for move in availableMoves:
            hypotheticalBoard = []
            for x in range(self.width):
                hypotheticalBoard.append([])
                for y in range(self.height):
                    hypotheticalBoard[x].append('')
                    
            for x in range(self.getWidth()):
                for y in range(self.getHeight()):
                    if board[x][y] == '':
                        hypotheticalBoard[x][y] = ''
                    else:
                        hypotheticalBoard[x][y] = board[x][y].copy()
                        
            self.makeHypotheticalMove(move[0], move[1], hypotheticalBoard, ComputerPlayer(playerColor, True, level))
            
            if level > 0:
                score = self.getBestMove(hypotheticalBoard, level - 1, originalPlayerColor)[1]
            else:
                score = self.getBoardScore(hypotheticalBoard, playerColor)
            
            realScore = self.getBoardScore(hypotheticalBoard, originalPlayerColor)
            
            if score < currentBest[1]:
                currentBest = [move, score, realScore]
                
            if availableMoves == [] and self.checkForValidHypotheticalMoves(board, ComputerPlayer(secondPlayerColor, True, level)) == []:
                if self.getScore(ComputerPlayer(playerColor, True, level), board) > self.getScore(ComputerPlayer(secondPlayerColor, True, level), board):
                    currentBest = [move, 1000000000, -1000000000]
                elif self.getScore(ComputerPlayer(playerColor, True, level), board) > self.getScore(ComputerPlayer(secondPlayerColor, True, level), board):
                    currentBest = [move, -1000000000, 1000000000]
                else:
                    pass
                
        return currentBest

    #  Makes a move on a board array created by the AI implementation.
    def makeHypotheticalMove(self, moveX, moveY, board, player):
        #  Makes sure the flip counts aren't messed up by restarting them.
        for x in range(len(board)):
            for piece in board[x]:
                if piece != '':
                    piece.makeFlippable(False)
        #  Check in every direction applicable to see if there are any flips.
        border = self.getBordering(moveX, moveY, board)
        for borderPiece in border:
            if borderPiece.getColor() != player.getColor():
                direction = self.getCheckDirection(moveX, moveY, borderPiece.getX(), borderPiece.getY())
                self.checkMakeFlippable(borderPiece, direction, board)
        #  Adds the new piece.
        board[moveX][moveY] = Piece(player.getColor(), moveX, moveY)
        #  And finally makes the flips.
        for x in range(len(board)):
            for piece in board[x]:
                if piece != '':
                    if piece.getFlippable():
                        piece.changeColor()
                    #  And resets the value for each piece.
                    piece.makeFlippable(False)
                
    #  Called at the beginning of each turn to find out where the player can move.
    #  Calls other functions that will eventually activate the correct buttons, but for now all are deactivated.
    def checkForValidHypotheticalMoves(self, board, player):
        availableMoveCoordinates = []
        #  Cycle through all the items in the board array.
        for x in range(len(board)):
            for y in range(len(board[x])):
                #  Only checks places where there are no pieces.
                if board[x][y] == '':     
                    #  Gets the bordering pieces and cycles through them.
                    bordering = self.getBordering(x, y, board)
                    moveFound = False
                    for borderPiece in bordering:
                        #  Makes sure everything is marked unflippable so that there aren't false positives for moves.
                        
                        for xDeactivate in range(len(board)):
                            for piece in board[xDeactivate]:
                                if piece != '':
                                    piece.makeFlippable(False)
                        
                        if borderPiece != '' and borderPiece.getColor() != player.getColor():
                            direction = self.getCheckDirection(x, y, borderPiece.getX(), borderPiece.getY())
                            #  Sends the information either to actually flip pieces or just test if they can be flipped.
                            self.checkMakeFlippable(borderPiece, direction, board)
                        
                        #  If there are any flippable pieces after running through the whole border, the original space is activated.
                        for xActivate in range(len(board)):
                            for yActivate in range(len(board[xActivate])):
                                if board[xActivate][yActivate] != '':
                                    if board[xActivate][yActivate].getFlippable():
                                        availableMoveCoordinates.append([x, y])
                                        moveFound = True
                                        break
                                    #  Deativates, so none are flippable after this.
                                    board[xActivate][yActivate].makeFlippable(False)
                            if moveFound:
                                break
                        if moveFound:
                            break
        return availableMoveCoordinates
    
    #  Gets a player's score.
    def getScore(self, player, board):
        score = 0
        color = player.getColor()
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] != '':
                    if board[x][y].getColor() == color:
                        score = score + 1
        return score
        
    #  This returns the *board's* score.
    #  This is entirely different from the normal score, as it takes into account both player's pieces and square weights.
    def getBoardScore(self, board, playerColor):
        boardScore = 0
        for x in range(len(board)):
            for piece in board[x]:
                if piece != '':
                    if piece.getColor() == playerColor:
                        boardScore = boardScore + boardWeights[x][piece.getY()]
                    else:
                        boardScore = boardScore - boardWeights[x][piece.getY()]
        
        return boardScore
        
    #  Take a move made by either human or AI, test to see what will flip, and then add the piece and flip pieces.
    def makeMove(self, player, moveX, moveY):
        #  Makes sure the flip counts aren't messed up by restarting them.
        for piece in self.pieces:
            piece.makeFlippable(False)
        #  Check in every direction applicable to see if there are any flips.
        border = self.getBordering(moveX, moveY, self.boardArray)
        for borderPiece in border:
            if borderPiece.getColor() != player.getColor():
                direction = self.getCheckDirection(moveX, moveY, borderPiece.getX(), borderPiece.getY())
                self.checkMakeFlippable(borderPiece, direction, self.boardArray)
        #  Adds the new piece.
        self.addPiece(player.color, moveX, moveY)
        #  And finally makes the flips.
        for piece in self.pieces:
            if piece.getFlippable():
                piece.changeColor()
                undrawPiece(piece)
                drawPiece(piece, self.canvas)
            #  And resets the value for each piece.
            piece.makeFlippable(False)
    
    #  Creates a piece at a given place on the board and increments the counter for pieces.
    def addPiece(self, color, x, y):
        self.boardArray[x][y] = Piece(color, x, y)
        self.pieces.append(self.boardArray[x][y])
        drawPiece(self.boardArray[x][y], self.canvas)
        #  This next line converts the 2D coordinates on the board to the list position of the appropriate button to deactivate.
        self.buttons[y * 8 + x].deactivate()
        self.numberPieces = self.numberPieces + 1
            
    #  Draws the board.
    def draw(self):
        self.canvas = graphics.GraphWin('Othello', 640, 690)
        self.image = graphics.Image(graphics.Point(320, 320), boardPath)
        self.bottomBar = graphics.Image(graphics.Point(320, 665), bottomPath)
        self.image.draw(self.canvas)
        self.bottomBar.draw(self.canvas)
        
    def getWidth(self):
        return self.width
        
    def getHeight(self):
        return self.height

#  The Button class is adapted from the Button class included with the textbook.
#  The mouse handling is the same but much of the graphics functionality has been removed,
#  And what was retained was changed.
#  Buttons are associated with a square on the board and detect clicking, as well as displaying valid moves graphically.
class Button:
    #  Buttons begin activated just so that the game doesn't think there are no available moves and immediately quit.
    #  Before the first turn they'll be deactivated appropriately.
    def __init__(self, canvas, topLeft, bottomRight, x = None, y = None, image = None):
        self.topLeft, self.bottomRight = topLeft, bottomRight
        self.x = x
        self.y = y
        self.activate()
        if x != None and y != None:
            self.center = graphics.Point(self.x * 80 + 40, self.y * 80 + 40)
        self.imageSource = image
        self.drawn = False
            
    #  Returns true for a button if the mouse event p occured within its bounds while activated.
    def clicked(self, p):
        return self.active and \
               self.topLeft.getX() <= p.getX() <= self.bottomRight.getX() and \
               self.topLeft.getY() <= p.getY() <= self.bottomRight.getY()
                
    def getX(self):
        return self.x
        
    def getY(self):
        return self.y
    
    def getState(self):
        return self.active
    
    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False

#  The Piece class handles the pieces themselves, both black and white.
#  Pieces can draw, undraw, and switch their display color.        
class Piece:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        #  The center of each piece calculated using (x,y) coordinates and width of each space.
        self.center = graphics.Point(self.x * 80 + 40, self.y * 80 + 40)
        self.makeFlippable(False)
    
    def getX(self):
        return self.x
        
    def getY(self):
        return self.y
        
    def getColor(self):
        return self.color
        
    def getFlippable(self):
        return self.flippable
    
    def makeFlippable(self, flippable):
        self.flippable = flippable
    
    #  Redraws with the new color.
    def changeColor(self):
        if self.color == white:
            self.color = black
        else:
            self.color = white
            
    def copy(self):
        return Piece(self.color, self.x, self.y)
        
#  The Player class waits for input from the player and determines what will happen each turn,
#  And determines whether the player can move when the game tells it to.
#  (Actually the board does this directly, but the player gathers data for the board functions.)
class Player:
    def __init__(self, color, turn):
        self.color = color
        self.turnMarker = turn
        
    #  Turn marker tells whether it's this player's turn or not.
    def getTurnMarker(self):
        return self.turnMarker
    
    def switchTurn(self):
        self.turnMarker = not self.turnMarker
    
    #  Called if the player is the active player for the given turn.
    #  Allows player to choose move.
    def turn(self, game):
        clicked = False
        #  If there are moves...
        if self.canMove(game.board):
            #  Draws all the available moves as clear token. Remove moves that are no longer valid.
            for button in game.board.buttons:
                if not button.getState() and button.drawn:
                    undrawButton(button)
                if button.getState() and not button.drawn:
                    drawButton(button, game.board.canvas)
            #  Waits for input. This is how the book deals with mice (not the animal), somewhat altered.
            while not clicked:
                click = waitForClick(game.board.canvas)
                for button in game.board.buttons:
                    if button.clicked(click):
                        clicked = True
                        move = button
                        #  Once the correct button is found, stop looking.
                        break
                
                game.quitButtonTest(click)
                    
            #  And finally put in the move and see what changes.
            game.board.makeMove(self, move.getX(), move.getY())
    
    def getColor(self):
        return self.color
    
    #  Called every turn player is active to see if there are any moves available.
    def canMove(self, board):
        #  This activates buttons if there are moves.
        board.checkForValidMoves(self)
        #  Initially set to false in case there are no moves.
        areMoves = False
        #  Tests for moves.
        for button in board.buttons:
            if button.getState():
                return True
        
#  The computer player inherits from the Player class, but contains the AI for determining computer play.
class ComputerPlayer(Player):
    def __init__(self, color, turn, level):
        Player.__init__(self, color, turn)
        self.level = level
    
    def turn(self, game):
        #  Makes a list of available moves for the computer.
        if self.canMove(game.board):
            for button in game.board.buttons:
                if button.drawn:
                    undrawButton(button)
            move = self.newAI(game)
            numberMoves = 0
            for button in game.board.buttons:
                if button.getState():
                    maybeMove = [button.getX(), button.getY()]
                    numberMoves = numberMoves + 1
            if numberMoves == 1:
                move = maybeMove
            if move == 0:
                return None
            game.board.makeMove(self, move[0], move[1])
        
    def newAI(self, game):
        bestMove = game.board.getBestMove(game.board.boardArray, self.level, self.getColor())[0]
        return bestMove

#  Gets mouse input using the built in graphics.py mouse handling.
def waitForClick(canvas):
    return canvas.getMouse()
    
def drawPiece(piece, canvas):
    if piece.color == white:
        piece.image = graphics.Image(piece.center, whitePath)
    else:
        piece.image = graphics.Image(piece.center, blackPath)
    piece.image.draw(canvas)
    sleep(.05)
    
def undrawPiece(piece):
    piece.image.undraw()
    
def drawButton(button, canvas):
    if button.imageSource != None:
        button.image = graphics.Image(button.center, button.imageSource)
        button.image.draw(canvas)
        button.drawn = True
    
def undrawButton(button):
    if button.imageSource != None:
        button.image.undraw()
        button.drawn = False

#  Creates the game.
def main():
    game = Game()
    game.playController()
                
main()