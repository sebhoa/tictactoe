#! /usr/bin/env python3

"""
Projet TicTacToe version non objet
-- niveau lycéen --

Auteur : Sébastien Hoarau
Date   : 2018.12.19
"""

import turtle
import math
import time
import random

# ---------------------------------
# LES CONSTANTES
# ---------------------------------

EMPTY = 0
CROIX = 1
ROND = 2

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

HUMAIN = 0
MACHINE = 1

TOKEN = ['', 'X', 'O']

# ---------------------------------
# LE MODELE
# ---------------------------------

# le jeu se compose d'une grille 3x3
# contenant 3 entiers :
# 0 = cellule vide
# 1 = cellule jouée par le joueur 1
# 2 = cellule jouée par le joueur 2

def init_grid():
    return [[EMPTY] * 3 for _ in range(3)]

def play_move(grid, row, col, player):
    grid[row][col] = player
    winner = check_winner(grid, player)
    end = check_end(grid, winner)
    return winner, end

def valid_move(grid, row, col):
    return row is not None and grid[row][col] == EMPTY


def one_line(grid, player):
    for row in range(3):
        if grid[row] == [player] * 3:
            return player
    return 0

def one_diag(grid, player):
    if [grid[row][row] for row in range(3)] == [player] * 3:
        return player
    if [grid[row][2 - row] for row in range(3)] == [player] * 3:
        return player
    return 0

def one_col(grid, player):
    for col in range(3):
        if [grid[row][col] for row in range(3)] == [player] * 3:
            return player
    return 0


def check_winner(grid, player):
    """ 
    Si grid correspond à une configuration gagnante
    pour player retourne player
    Sinon retourne 0
    """
    return one_line(grid, player) or\
            one_col(grid, player) or\
            one_diag(grid, player)


def full(grid):
    return all(grid[r][c] != EMPTY for r in range(3) for c in range(3)) 

def check_end(grid, winner):
    return winner or full(grid)


# -- IA
# --

def empty_cells(grid):
    return [(r,c) for r in range(3) for c in range(3)
                if grid[r][c] == EMPTY]

def faible(grid, player):
    """
    Stratégie minimaliste : si un coup gagnant on 
    le joue, sinon, si un coup perdant on joue
    à cet endroit pour bloquer, sinon au hasard
    """
    copie = [grid[row].copy() for row in range(3)]
    for r, c in empty_cells(grid):
        copie[r][c] = player
        if check_winner(copie, player) == player:
            return r, c
        copie[r][c] = EMPTY
    adversaire = 3 - player
    for r, c in empty_cells(grid):
        copie[r][c] = adversaire
        if check_winner(copie, adversaire) == adversaire:
            return r, c
        copie[r][c] = EMPTY
    return random.choice(empty_cells(grid))


def negamax(grid, player):
    """
    Calcule le meilleur score pour le joueur courant
    Au TicTacToe, on va pouvoir explorer toutes les
    configurations et retourner le vrai score des configurations
    finales : 1 si le joueur gagne, -1 s'il perd et 0 pour un nul
    """
    winner = check_winner(grid, player)
    if winner == player:
        return 1
    elif winner == 3 - player:
        return -1
    elif full(grid):
        return 0
    else:
        bestScore = -10
        for r, c in empty_cells(grid):
            grid2 = [grid[row].copy() for row in range(3)]
            grid2[r][c] = player 
            score = -negamax(grid2, 3 - player)
            if score > bestScore:
                 bestScore = score
        return bestScore


def choice(grid, player):
    # return faible(grid, player)
    bestScore = -10
    bestPos = None, None
    for r, c in empty_cells(grid):
        grid2 = [grid[row].copy() for row in range(3)]
        grid2[r][c] = player
        score = -negamax(grid2, 3 - player)
        if score > bestScore:
            bestScore = score
            bestPos = r, c
    return bestPos


# ---------------------------------
# LA VUE
# ---------------------------------

def move_to(t, pos):
    t.up()
    t.goto(pos)
    t.down()

def draw_title(t):
    move_to(t, TITLE_POSITION)
    t.write(TITLE, align='center', font=TITLE_FONT)


def draw_grid(t):
    """
    Dessine la grille vierge
    """
    t.color((80,80,80))
    a = GRID_SIZE // 2
    b = GAME_SIZE // 2 + MARGIN // 2
    pts = [(-a,-b), (-a,b), (-b,-a), (b,-a)]
    angles = [0, 0, 90, 90]
    for index, pt in enumerate(pts):
        move_to(t, pt)
        t.seth(angles[index])
        t.fd(GRID_SIZE)


def draw_cross(t, centre, small=False):
    """
    Dessine une croix centrée au point centre
    En taille réduite si small vaut True
    """
    t.seth(0)
    t.color(CROSS_COLOR)
    t.pensize(MARK_THICKNESS)
    d = round(2*GAME_SIZE / (3*math.sqrt(2)))
    if small:
        d = round(d/1.5)
    move_to(t, centre)
    t.left(45)
    for _ in range(4):
        t.fd(d)
        move_to(t, centre)
        t.left(90)

def draw_round(t, centre, small=False):
    """
    Dessine un rond centré au point centre
    En taille réduite si small vaut True
    """
    x, y = centre
    t.seth(0)
    t.color(CIRCLE_COLOR)
    t.pensize(MARK_THICKNESS)
    move_to(t, (x, y - GAME_SIZE // 2 + MARK_THICKNESS))
    radius = GAME_SIZE // 2 - MARGIN // 2 - MARK_THICKNESS // 2
    if small:
        radius = round(radius / 1.5)
    t.circle(radius)


def center(row, col):
    """
    Traduit des coordonnées de la grille de jeu
    donc du style (0,0), (1,0) etc
    en coordonnées où seront dessinées la X ou le O
    """
    row = row - 1
    col = col - 1
    pixrow = (GAME_SIZE + MARGIN) * row
    pixcol = (GAME_SIZE + MARGIN) * col
    return (pixcol, pixrow)

def view_update(t, row, col, player):
    if player == CROIX:
        draw_cross(t, center(row, col))
    else:
        draw_round(t, center(row, col))
    t.screen.update()


def screen_choix(t):
    """
    Dessine l'écran de choix des joueurs 
    (humain / machine) qui vont jouer
    """
    draw_cross(t, (-80, 160), small=True)
    draw_round(t, (80, 180), small=True)
    t.color('black')
    combinaisons = [(p1,p2) for p1 in ('Humain', 'Machine') for p2 in ('Humain', 'Machine')]
    col = -170
    for index, pt in enumerate([(col, 50), (col, 0), (col, -50), (col, -100)]):
        move_to(t, pt)
        p1, p2 = combinaisons[index]
        t.write(f'{index+1}.  {p1:10}{p2:>10}', align='left', font=GAME_FONT)
    move_to(t, MSG_POSITION)
    t.write('Votre choix ?', align='center', font=GAME_FONT)


def screen_game(t):
    """
    Efface l'écran et redessine le titre ainsi
    que la grille de jeu
    """
    t.clear()
    draw_title(t)
    draw_grid(t)
    t.screen.update()

def inside(value):
    return -GRID_SIZE//2 <= value <= GRID_SIZE//2

def trad_click(mouse_x, mouse_y):
    """
    Transforme les coordonnées du clic sur la fenêtre
    graphique en coordonnées 3x3 de notre grille de jeu
    """
    if inside(mouse_x) and inside(mouse_y):
        row = (mouse_y + GRID_SIZE // 2) // GAME_SIZE
        col = (mouse_x + GRID_SIZE // 2) // GAME_SIZE
        return int(row), int(col)
    return None, None


# -- Gestion des messages temporaires

def annonce(t, msg):
    t.clear()
    move_to(t, MSG_POSITION)
    t.write(msg, align='center', font=GAME_FONT)

def annonce_player(t, player):
    annonce(t, f'{TOKEN[player]} joue')

def stop(t, winner):
    if winner:
        annonce(t, f'{TOKEN[winner]} GAGNE')
    else:
        annonce(t, 'PARTIE NULLE')


# ---------------------------------
# LE CONTRÔLEUR
# ---------------------------------

def init_turtle(t):
    t.ht()
    t.screen.tracer(300)
    t.screen.colormode(255)


def human(players, player):
    return players[player] == HUMAIN


def block_click(t):
    t.screen.onclick(None)

def unblock_click(view, msg, grid, players, player, gameover):
    """
    La fonction qui débloque le clic souris et lance la boucle de jeu
    avec les coordonnées du clic
    """
    view.screen.onclick(lambda x, y: gameloop(view, msg, x, y, grid, players, player, gameover))


def gameloop(view, msg, row, col, grid, players, player, gameover):
    """
    La boucle de jeu :
    En entrant on commence par bloquer les clics, le temps de traiter
    les infos courantes
    """
    block_click(view)
    winner = 0 # pas de gagnant pour l'instant
    if row is not None: # La 1ere fois qu'on arrive ici row est None
        if human(players, player):
            row, col = trad_click(row, col) # on demande à la vue de traduire le clic souris en row, col du jeu
        if not human(players, player) or valid_move(grid, row, col):
            winner, gameover = play_move(grid, row, col, player) # mise à jour du modèle
            view_update(view, row, col, player) # mise à jour de la vue (on affiche la nouvelle marque)
            player = 3 - player # on passe au joueur suivant
    play(view, msg, grid, players, player, winner, gameover)


def play(view, msg, grid, players, player, winner, gameover):
    """
    La fonction qui permet de récupérer 1 coup
    """
    if gameover:
        stop(msg, winner)
    elif human(players, player):
        # si c'est un humain qui joue, on débloque le clic qui appelera
        # la boucle de jeu avec les coordonnées du clic
        unblock_click(view, msg, grid, players, player, gameover)
        annonce_player(msg, player)
    else:
        time.sleep(1) # juste pour voir le jeu qd il s'agit de 2 machines
        row, col = choice(grid, player) # l'IA
        gameloop(view, msg, row, col, grid, players, player, gameover) 





def game_begin(key, main_turtle, snd_turtle, grid, players, player, gameover):
    """
    Le début du jeu : après la mise à jour de la liste des joueurs 
    en fonction du choix de l'utilisateur,
    on demande à la vue d'afficher l'écran de jeu : la grille vierge
    et on lance la boucle de jeu
    """
    choix = {'1':(None, HUMAIN, HUMAIN),
            '2':(None, HUMAIN,MACHINE),
            '3':(None, MACHINE, HUMAIN),
            '4':(None, MACHINE,MACHINE)}
    for p in [CROIX, ROND]:
        players[p] = choix[key][p]
    screen_game(main_turtle)
    gameloop(main_turtle, snd_turtle, None, None, grid, players, player, gameover)


def start():
    """
    La fonction d'entrée dans le jeu
    Création des tortues,
    Initialisation des diverses variables nécessaires
    """

    # Les tortues
    #
    main_turtle = turtle.Turtle()  # tortue principale
    init_turtle(main_turtle)
    snd_turtle = turtle.Turtle()   # tortue secondaire pour les messages temproraires
    init_turtle(snd_turtle)
    main_turtle.screen.listen()    # on écoute les interaction utilisateur

    # Premier écran du jeu : choix de joueurs
    #
    draw_title(main_turtle)     # On ecrit le titre
    screen_choix(main_turtle)   # écran de choix des joueurs
    
    # Initialisation des variables
    #
    player = CROIX              # joueur courant, c'est CROIX qui commence   
    gameover = False            # le booléen qui annoncera la fin de la partie
    grid = init_grid()          # initialisation de la grille
    players = [None, None, None]

    # La suite ne se fera que lorsqu'on aura appuyé sur une touche parmi 1, 2, 3, 4
    #
    main_turtle.screen.onkeypress(lambda : game_begin('1', main_turtle, snd_turtle, grid, players, player, gameover), '1')
    main_turtle.screen.onkeypress(lambda : game_begin('2', main_turtle, snd_turtle, grid, players, player, gameover), '2')
    main_turtle.screen.onkeypress(lambda : game_begin('3', main_turtle, snd_turtle, grid, players, player, gameover), '3')
    main_turtle.screen.onkeypress(lambda : game_begin('4', main_turtle, snd_turtle, grid, players, player, gameover), '4')


    # Le mainloop qui permet à la fenêtre graphique de rester ouverte
    #
    main_turtle.screen.mainloop()


# LE MAIN, minimaliste
#
start()







