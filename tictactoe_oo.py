#! /usr/bin/env python3

"""
Projet TicTacToe
Le célèbrissime jeu de plateau 1vs1, codé
avec le module turtle

Lancement du script : ./tictactoe.py Puis 
tout doit se faire à la souris ;-)

Auteur : Sébastien Hoarau 
Date   : Décembre 2018
"""

# -- LES MODULES
# --

import turtle
import math
import time
import random

CROSS = 1
ROUND = 2


# -- LES CLASSES
# --

class GameView(turtle.Turtle):
    """ LA VUE """

    TITLE = 'TicTacToe'
    TITLE_FONT = ('helvetica', 36, 'normal')
    GAME_FONT = ('helvetica', 28, 'normal')
    TITLE_POSITION = 0, 250
    MSG_POSITION = 0, -250
    GAME_SIZE = 120     # la dimension d'une croix ou d'un rond
                        # cette dimension conditionne l'ensemble
                        # de l'interface
    MARGIN = 15
    THICKNESS = 6           # taille du trait des éléments graphiques
    GRID_SIZE = 3 * GAME_SIZE + 2 * THICKNESS

    CROSS_COLOR = 'firebrick'
    CIRCLE_COLOR = 'darkcyan'
    MARK_THICKNESS = THICKNESS * 2

    TOKEN = ['', 'X', 'O']

    def __init__(self, controller, model):
        self.controller = controller
        self.model = model

        # -- init de la tortue
        #
        turtle.Turtle.__init__(self)
        self.ht()
        self.screen.tracer(300)
        self.screen.colormode(255)
        self.pensize(GameView.THICKNESS)
        

        # -- 2e tortue pour les messages temporaires
        #
        self.turtle_msg = turtle.Turtle()
        self.turtle_msg.ht()


    def mainloop(self):
        self.screen.update()
        self.screen.mainloop()


    def first_screen(self):
        self.draw_title()
        self.cross((-80, 160), small=True)
        self.round((80, 180), small=True)
        self.color('black')
        combinaisons = [(p1,p2) for p1 in ('Humain', 'Machine') for p2 in ('Humain', 'Machine')]
        col = -170
        for index, pt in enumerate([(col, 50), (col, 0), (col, -50), (col, -100)]):
            self.move_to(pt)
            p1, p2 = combinaisons[index]
            self.write(f'{index+1}.  {p1:10}{p2:>10}', align='left', font=GameView.GAME_FONT)
        self.move_to(GameView.MSG_POSITION)
        self.write('Votre choix ?', align='center', font=GameView.GAME_FONT)


    def draw_title(self):
        self.move_to(GameView.TITLE_POSITION)
        self.write(GameView.TITLE, align='center', \
                font=GameView.TITLE_FONT)

    def game_screen(self):
        self.clear()
        self.draw_title()
        self.draw_grid()
        self.screen.update()

    def draw_grid(self):
        self.color((80,80,80))
        a = GameView.GRID_SIZE // 2
        b = GameView.GAME_SIZE // 2 + GameView.MARGIN // 2
        pts = [(-a,-b), (-a,b), (-b,-a), (b,-a)]
        angles = [0, 0, 90, 90]
        for index, pt in enumerate(pts):
            self.move_to(pt)
            self.seth(angles[index])
            self.fd(GameView.GRID_SIZE)

    def inside(self, value):
        return -GameView.GRID_SIZE // 2 <= value <= GameView.GRID_SIZE // 2

    def trad_click(self, mouse_x, mouse_y):
        if self.inside(mouse_x) and self.inside(mouse_y):
            row = (mouse_y + GameView.GRID_SIZE // 2) // GameView.GAME_SIZE
            col = (mouse_x + GameView.GRID_SIZE // 2) // GameView.GAME_SIZE
            return int(row), int(col)
        return None, None

    def center(self, row, col):
        row = row - 1
        col = col - 1
        pixrow = (GameView.GAME_SIZE + GameView.MARGIN) * row
        pixcol = (GameView.GAME_SIZE + GameView.MARGIN) * col
        return (pixcol, pixrow)



    def cross(self, centre, small=False):
        self.seth(0)
        self.color(GameView.CROSS_COLOR)
        self.pensize(GameView.MARK_THICKNESS)
        d = round(2*GameView.GAME_SIZE / (3*math.sqrt(2)))
        if small:
            d = round(d/1.5)
        self.move_to(centre)
        self.left(45)
        for _ in range(4):
            self.fd(d)
            self.move_to(centre)
            self.left(90)

    def round(self, centre, small=False):
        x, y = centre
        self.seth(0)
        self.color(GameView.CIRCLE_COLOR)
        self.pensize(GameView.MARK_THICKNESS)
        self.move_to((x, y - GameView.GAME_SIZE // 2 + GameView.MARK_THICKNESS))
        radius = GameView.GAME_SIZE // 2 - GameView.MARGIN // 2 - GameView.MARK_THICKNESS // 2
        if small:
            radius = round(radius / 1.5)
        self.circle(radius)


    def draw_fcts(self):
        return [None, self.cross, self.round]

    def update(self):
        row, col = self.controller.last_move
        self.draw_fcts()[self.model.player](self.center(row, col))
        self.screen.update()

    def move_to(self, pos, other=None):
        if other:
            other.up()
            other.goto(pos)
            other.down()
        else:
            self.up()
            self.goto(pos)
            self.down()

    def annonce(self, msg):
        self.turtle_msg.clear()
        self.move_to(GameView.MSG_POSITION, self.turtle_msg)
        self.turtle_msg.write(msg, align='center', font=GameView.GAME_FONT)

    def annonce_player(self):
        self.annonce(f'{GameView.TOKEN[self.model.player]} joue')


    def stop(self):
        winner = self.model.winner
        if winner:
            self.annonce(f'{GameView.TOKEN[winner]} GAGNE')
        else:
            self.annonce('PARTIE NULLE')
        self.screen.update()


class GameModel:
    """ LE MODÈLE """

    EMPTY = 0
    HUMAIN = 0
    MACHINE = 1

    def __init__(self):
        self.grid = [[0] * 3 for _ in range(3)]
        self.player = CROSS
        self.winner = 0


    def valid_move(self, row, col):
        return self.grid[row][col] == GameModel.EMPTY

    def choice(self):
        """ La machine joue au hasard pour l'instant """
        candidats = [(row, col) for row in range(3) for col in range(3)
                        if self.valid_move(row, col)]
        return random.choice(candidats)

    def next_player(self):
        self.player = 3 - self.player


    def one_line(self):
        """
        Retourne l'ID du joueur courant si celui-ci à 3
        aligné sur une ligne, 0 sinon
        """
        for row in range(3):
            if self.grid[row] == [self.player] * 3:
                return self.player
        return 0

    def one_diag(self):
        """
        Retourne l'ID du joueur courant s'il en a 3
        alignés sur une deux diagonales, 0 sinon
        """
        if [self.grid[row][row] for row in range(3)] == [self.player] * 3:
            return self.player
        if [self.grid[row][2 - row] for row in range(3)] == [self.player] * 3:
            return self.player
        return 0

    def one_col(self):
        """
        Retourne l'ID du joueur courant s'il en a 3
        alignés sur une des colonnes, 0 sinon
        """
        for col in range(3):
            if [self.grid[row][col] for row in range(3)] == [self.player] * 3:
                return self.player
        return 0


    def full(self):
        return all(self.grid[r][c] != GameModel.EMPTY
                        for r in range(3) for c in range(3))

    def check_winner(self):
        return self.one_line() or\
                self.one_col() or\
                self.one_diag()

    def update_winner(self):
        self.winner = self.check_winner()


    def end_game(self):
        return self.winner != 0 or self.full()

    def play(self, move):
        row, col = move
        self.grid[row][col] = self.player
        self.update_winner()
        self.next_player()
        return self.end_game()




class GameController:
    """ LE CONTRÔLEUR """

    def __init__(self):
        self.model = GameModel()
        self.view = GameView(self, self.model)

        self.wait = False       # pour temporiser qd la machine joue seule
        self.players = tuple()  # qui sont les joueurs
        self.gameover = False
        self.last_move = None



    def block_click(self):
        self.view.screen.onclick(None)

    def unblock_click(self):
        self.view.screen.onclick(self.gameloop)

    def human(self):
        return self.players[self.model.player] == GameModel.HUMAIN

    def valid_move(self, row, col):
        if row is not None and self.model.valid_move(row, col):
            self.last_move = row, col
            return True
        return False

    def annonce_player(self):
        self.view.annonce_player()

    def gameloop(self, x = None, y = None):
        self.block_click()
        if x is not None:
            if self.human():
                row, col = self.view.trad_click(x, y)
            if not self.human() or self.valid_move(row, col):   
                self.view.update()
                self.gameover = self.model.play(self.last_move)
        self.play()

    def play(self):
        if self.gameover:
            self.stop()
        elif self.human():
            self.annonce_player()
            self.unblock_click()
        else:
            self.annonce_player()
            if self.wait:
                time.sleep(2)
            self.last_move = self.model.choice()
            self.gameloop(1)

    def mainloop(self):
        self.view.mainloop()

    def stop(self):
        self.view.stop()

    def game_begin(self, key):
        choix = {'1':(None, GameModel.HUMAIN, GameModel.HUMAIN),
                '2':(None, GameModel.HUMAIN,GameModel.MACHINE),
                '3':(None, GameModel.MACHINE, GameModel.HUMAIN),
                '4':(None, GameModel.MACHINE,GameModel.MACHINE)}
        self.players = choix[key]
        if self.players[CROSS] == GameModel.MACHINE and\
                    self.players[ROUND] == GameModel.MACHINE:
            self.wait = True
        self.view.game_screen()
        self.gameloop()

    def start(self):
        self.view.screen.listen()
        self.view.draw_title()
        self.view.first_screen()
        # Choix de qui joue
        #
        self.view.screen.onkeypress(lambda : self.game_begin('1'), '1')
        self.view.screen.onkeypress(lambda : self.game_begin('2'), '2')
        self.view.screen.onkeypress(lambda : self.game_begin('3'), '3')
        self.view.screen.onkeypress(lambda : self.game_begin('4'), '4')



ttt = GameController()
ttt.start()
ttt.mainloop()

