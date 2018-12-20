# projet TicTacToe 

Où comment réaliser un jeu de plateau 1 vs 1 en utilisant le module `turtle` de Python et, si possible, en codant proprement (pas de variables globales dans tous les sens). Afin de rendre l'ensemble accessible au niveau lycée, nous allons nous contenter de programmation impérative, pas d'objets. Un soupçon de programmation événementielle.

Nous allons quand même essayer de séparer les fonctions en trois catégories :

- celles dévolues à l'affichage (la vue)
- celles qui s'occuperont de la partie *métier* du jeu : contrôle d'un coup valide, calcul de position gagnante etc. (le modèle)
- et enfin les fonctions qui vont orchestrer tout ça, demander les interactions avec l'utilisateur etc. (le contrôleur)

Dans cet article nous verrons les concepts suivants :

- Manipulation du module turtle : plusieurs tortues en même temps, écriture de textes dans la fenêtre graphique
- Programmation événementielle
- Lambda expression

Mais commençons par décrire un peu notre modèle de jeu.

## Le modèle

Le jeu se joue sur une grille de 3x3 :

![Début de partie de TicTacToe](/Figs/ex_interface_2.png)

Nous allons utiliser une liste de listes pour modéliser cela, avec trois valeurs possible pour chaque élément des listes intérieures :

- 0 pour une cellule vide
- 1 pour une cellule jouée par le joueur 1
- 2 pour une cellule jouée par le joueur 2

Ainsi la situation de notre figure pourrait être modélisée comme suit :

```python
[[0,0,0], [1,1,0], [2,0,0]]
```

Dans notre programme, nous manipulerons sous le nom de `grid` une telle liste. L'initialisation de cette `grid` pourra se faire par la fonction :

```python
def init_grid():
    return [[EMPTY] * 3 for _ in range(3)]
```

`EMPTY` est une constante, valant 0. Prenez l'habitude de ne manipuler des objets litteraux qu'à travers des constantes, regroupées en tête de script et facilement modifiables si besoin.


Avant de voir un peu le squelette de notre programme, notamment de notre contrôleur, détaillons quelques fonctionnalités prises en charge par le modèle.

C'est le modèle qui va jouer un coup. En quoi cela consiste-il et de quoi avons-nous besoin ? De la grille bien sûr et aussi du joueur courant ainsi que des coordonnées (ligne, colonne) de la cellule jouée.

```python
def play_move(grid, row, col, player):
    grid[row][col] = player
```

Mais le modèle peut aller un peu plus loin et une fois ce coup joué, tester s'il y a un gagnant et si la partie est terminée. La fonction retournera alors ces deux informations récupérées et exploitées par le contrôleur. Voici le code complet de la fonction :


```python
def play_move(grid, row, col, player):
    grid[row][col] = player
    winner = check_winner(grid, player)
    end = check_end(grid, winner)
    return winner, end
```

### Tester une configuration gagnante

Une configuration `grid` est gagnante pour le joueur dont le numéro est `pid` si la liste `[pid, pid, pid]` se retrouve comme une ligne ou une colonne ou une des deux diagonales de `grid` 

```python
def check_winner(grid, player):
    return one_line(grid, player) or\
            one_col(grid, player) or\
            one_diag(grid, player)
```

Dans ces fonctions nous allons utiliser des constructions en compréhension de liste. En effet, si l'obtention d'un ligne de la grille ne pose pas de souci : `grid[row]` pour les valeurs de `row` allant de 0 à 2 sont les trois lignes de notre grille.

Pour les colonnes c'est un peu différent. Il nous faut mettre dans une liste les `grid[row][col]` pour un `col` donné et pour `row` variant de 0 à 2. Ceci est obtenu par compréhension de liste :

```python
[grid[row][col] for row in range(3)]
```

Va nous donner la colonne correpondant à `col` Voici concrètement l'utilisation dans la fonction qui recherche si le joueur courant est gagnant sur une colonne de la grille :


```python
def one_col(grid, player):
    for col in range(3):
        if [grid[row][col] for row in range(3)] == [player] * 3:
            return player
    return 0
```

Je vous laisse trouver en exercice la fonction pour les diagonales :wink:

Concernant la fin de partie, là non plus pas de difficulté majeure : la partie est terminée si nous avons un gagnant (`check_winner` aura retourné 1 ou 2) ou si la grille est pleine.

```python
def check_end(grid, winner):
    return winner or full(grid)
```

Avec 

```python
def full(grid):
    return EMPTY not in all_values(grid) 

def all_values(grid):
    return [grid[r][c] for r in range(3) for c in range(3)]
```

On pourrait écrire cela de façon plus *pythonique* en utilisant les expressions génératrices, dont nous parlerons peut-être dans un autre article, et la fonction python `all`. Juste pour vous montrer :

```python
def full(grid):
    return all(grid[r][c] != EMPTY for r in range(3) for c in range(3))
```

**Explication rapide :** nous générons les booléens `grid[r][c] != EMPTY` pour toutes les valeurs de `r` et `c` (ie pour toutes les coordonnées de cellules) et nous vérifions avec `all` que tous ces booléens sont bien égaux à `True`.

Maintenant que nous avons vu le plus simple, attaquons nous aux difficultés. D'abord le contrôleur.


## Le contrôleur

C'est lui qui lance le programme, interagit avec l'utilisateur, ordonne à la vue de se mettre à jour, au modèle de valider puis de jouer un coup, etc.

Ici, nous ne codons pas réellement un [modèle MVC][1] puisque nous ne faisons pas de programmation orientée objet. Mais comme dit en intro, nous regroupons nos diverses fonctions selon leur rôle.

Voici le squelette du déroulé du script :

1. Au lancement, page d'accueil avec choix de joueurs :

![Etape 00](/Figs/etape_00.png)

2. L'utilisateur fait son choix en appuyant sur une des touches 1, 2, 3 ou 4 et on passe alors au deuxième écran :

![Etape 01](/Figs/etape_01.png)

3. A partir de là on entre dans la boucle de jeu qui consiste en :
    1. Récupérer un coup 
    2. Valider ce coup et le jouer
    3. Mettre à jour la vue
    4. Recommencer en 1. jusqu'à ce que la partie soit terminée

![Etape 02](/Figs/etape_02.png)

Avant de présenter nos différentes fonctions de contrôleur, listons un peu ce dont nous aurons besoin pour la suite en termes de données et donc de variables à initialiser et qui seront à passer en paramètres à nos diverses fonctions. 

### Des tortues

Nous allons utiliser des objets `Turtle` pour le dessin de notre jeu et pour les interactions (appui sur une touche pour le choix des joueurs et clic souris pour jouer un coup). Nous en utiliserons deux : `main_turtle` pour le dessin du jeu et `snd_turtle` pour l'affichage du message annonçont c'est à qui de jouer.

En effet ce message doit changer à chaque tour c'est-à-dire qu'il faudra régulièrement effacer (par la méthode `clear`) ce que cette tortue a dessiné ou écrit. pour ne pas avoir à tout redessiner il est plus simple de prévoir une tortue dédiée à ces messages.

### Entiers et liste pour les joueurs

Nous allons stocker dans une liste le type des joueurs : humain ou machine. Ainsi notre variables `players` vaudra `[None, 0, 1]` pour une partie où un humain jouant la croix affrontera la machine avec les ronds. Pourquoi une liste de 3 ? Pour que l'indice coïncide avec l'identifiant du joueur. Le premier élément de cette liste ne sert à rien (d'où le `None`).

Rappelez-vous dans le modèle, le joueur courant est repéré par son numéro : 1 ou 2... ou plus exactement par `CROIX` et `ROND` les deux constantes associées à 1 et 2.

Ainsi on parlera de `players[CROIX]` qui représente le type du joueur 1. Par exemple la fonction qui teste que le joueur courant est humain :

```python
def human(players, player):
    return players[player] == HUMAN
```

En effet on aura aussi les deux constantes :

```python
HUMAN = 0
MACHINE = 1
```

Le joueur courant est stocké dans une variable `player` (sans s).


### Un booléen pour la fin de partie

`gameover` un booléen initialisé à `False` et mis à jour après chaque coup joué permettra au contrôleur de savoir quand la partie est terminée.

Voilà nos diverses fonctions devrons embarquer ces paramètres assez nombreux. C'est un des inconvénients de ne pas faire de programmation objet : au lieu d'avoir un objet avec des attibuts, on se trimballe tout un paquet de variables.


### Commençons...

Voici donc le début de la fonction de démarrage du contrôleur :

```python
def start():
    # Les tortues
    #
    main_turtle = turtle.Turtle()  # tortue principale
    init_turtle(main_turtle)
    snd_turtle = turtle.Turtle()   # tortue secondaire
    init_turtle(snd_turtle)
    main_turtle.screen.listen()    # on écoute les interactions

    # Initialisation des variables
    #
    player = CROIX      # joueur courant, c'est CROIX qui commence   
    gameover = False    # le booléen qui annoncera la fin de la partie
    grid = init_grid()  # initialisation de la grille
    players = [None, None, None]

    # Premier écran du jeu : choix de joueurs
    #
    draw_title(main_turtle)     # On ecrit le titre
    screen_choix(main_turtle)   # écran de choix des joueurs
    

    # Ici il manque quelques instructions
    # ...

    # Le mainloop qui permet à la fenêtre graphique de rester ouverte
    #
    main_turtle.screen.mainloop()
```

Nous commençons par la création de nos deux tortues et leurs réglages (qui consistent essentiellement à cacher la tortue, faire en sorte de dessiner plus vite etc.). La ligne `main_turtle.screen.listen()` permet *d'écouter* les événements dans la fenêtre graphique (nous en aurons deux : l'appui sur une touche pour choisir qui joue et le clic souris lors de la partie).

Nous poursuivons par l'initialisation des diverses variables dont nous avons déjà parlé. Et le contrôleur demande l'affichage du premier écran avec le titre et le menu de choix des joueurs. 

La dernière ligne propre à toute utilisation du module turtle maintient ouvert la fenêtre graphique de nos tortues.

Avant de poursuivre, (les instructions manquantes) voyons la différence essentielle entre programmation impérative et programmation événementielle.

### Impératif vs Evénementiel

Dans la programmation impérative classique les instructions sont exécutées les unes à la suite des autres :

```
instruction 1
instruction 2
...
instruction n
```

Et tant qu'une instruction _i_ n'est pas terminée, l'instruction *i+1* n'est pas exécutée.

En programmation événementiel nous aurons :

```
instruction 1
instruction 2
ecoute_evenement_1(action_1)
ecoute_evenement_2(action_2)
instruction 3
...
```

Les instructions 1 et 2 sont éxécutées dans cet ordre puis notre programme *pose* des *écoutes* sur deux événements (l'appui sur une touche particulière du clavier et un clic de souris par exemple), puis passe à l'instruction 3. Les actions 1 et 2 (des appels à des fonctions) ne se feront que lorsque les événements associés se produiront. Ainsi, dans les instructions 3 et suivantes, on ne peut pas supposer que les actions 1 et 2 ont été réalisées. Notre flux d'instruction n'est plus tout à fait linéaire.

Ainsi, si l'instruction 3 ne doit être réalisée **que** si une des actions l'a été alors il ne faut pas mettre cette instruction à cet endroit, mais dans le groupe d'instructions de l'action correspondante.


### Retour à notre contrôleur

Revenons à notre jeu. Lorsque l'écran de choix des joueurs s'affiche, nous ne devons plus rien faire qu'attendre que l'utilisateur fasse son choix. Toute la suite va donc se dérouler dans une fonction qui ne sera appelée que lorsque l'utilisateur va provoquer un événement en lien avec son choix. Ici bien sûr il s'agira d'appuyer sur la touche `1` s'il choisit le premier choix, `2` pour le deuxième etc.

Les quatre instructions manquantes correspondent donc à ces quatre choix :

```python
    main_turtle.screen.onkeypress(lambda : game_begin('1', main_turtle, snd_turtle, grid, players, player, gameover), '1')
    main_turtle.screen.onkeypress(lambda : game_begin('2', main_turtle, snd_turtle, grid, players, player, gameover), '2')
    main_turtle.screen.onkeypress(lambda : game_begin('3', main_turtle, snd_turtle, grid, players, player, gameover), '3')
    main_turtle.screen.onkeypress(lambda : game_begin('4', main_turtle, snd_turtle, grid, players, player, gameover), '4')
```

La méthode `onkeypress` prend deux arguments. Le premier est une fonction **sans** argument et le deuxième une chaîne de caractère correspondant à la touche à laquelle on souhaite réagir. 

**Une fonction sans argument**. Souvent cette contrainte fait que les gens programment avec des variables globales, modifiées dans tous les sens par des fonctions sans argument. Ce n'est pas propre et je vous déconseille de faire cela.

Ici, nous appelons la fonction `game_begin` qui nécessite de nombreux arguments (toutes nos variables importantes pour la suite du jeu). L'astuce est d'utiliser une fonction anonyme : `lambda` 

En Python, lorsque nous écrivons :

```python
def f(x, y):
    return 2*x - 3*y
```

Nous définissons une fonction qui s'appelle `f` et qui prend deux arguments en paramètres. Une **lambda expression** peut définir la même fonction mais sans lui donner de nom :

```python
lambda x, y : 2*x + 3*y
```

Et c'est une telle fonction que nous appelons dans nos `onkeypress` :

```python
lambda : game_begin(...)
```

Notre fonction lambda n'a aucun argument et une seule instruction : l'appel à la fonction `game_begin` avec tous ses arguments.

Et notre fonction `game_begin` qui lance la boucle de jeu :

```python
def game_begin(key, main_turtle, snd_turtle, grid,\
                players, player, gameover):

    choix = {'1':(None, HUMAIN, HUMAIN),
            '2':(None, HUMAIN,MACHINE),
            '3':(None, MACHINE, HUMAIN),
            '4':(None, MACHINE,MACHINE)}
    for p in [CROIX, ROND]:
        players[p] = choix[key][p]
    screen_game(main_turtle)
    gameloop(main_turtle, snd_turtle, None, None, grid,\
                players, player, gameover)
```

Cette fonction possède beaucoup d'arguments :

- `key` la chaine de caractères correspondant à la touche choisie par l'utilisateur
- `main_turtle`, `snd_turtle` nos deux tortues, la 1re servant à dessiner la seconde pour les messages, 
- `grid` la grille qui modélise l'état du jeu (où se trouvent les 0, les 1 et les 2),
- `players` la liste des joueurs (vous vous souvenez ? leur type en fait au sens `HUMAIN` ou `MACHINE`,
- `player` le joueur courant (ie si c'est `CROIX` qui joue ou `ROND`)
- `gameover` le booléen qui renseigne sur la fin de la partie

La fonction met à jour la liste des joueurs avec le choix de l'utilisateur puis la vue affiche l'écran de jeu (on efface le menu du choix des joueurs et on affiche la grille de jeu vierge). Enfin on lance la boucle de jeu avec tous les paramètres plus deux autres réglés sur `None` et `None` pour l'instant et qui correspondront aux coordonnées de l'endroit où le joueur humain aura cliqué.


### La boucle de jeu

Nous approchons de la fin des fonctions du contrôleur. Il s'agit des deux plus importantes : la boucle de jeu qui elle même va appeler la fonction qui joue un coup et rappelle la boucle de jeu et ce jusqu'à la fin de la partie. Pourquoi deux fonctions ? Comme nous l'avons déjà vu tout à l'heure lorsuqe le jeu doit attendre l'interaction de l'utilisateur on ne peut mettre aucune autre instruction derrière. On écoute le clic souris, et on ne fait rien pendant ce temps. Le clic déclenche l'appel à la deuxième fonction.

Voici notre boucle :

```python
def gameloop(view, msg, row, col, grid, players, player, gameover):
    block_click(view)
    winner = 0 
    if row is not None: 
        if human(players, player):
            row, col = trad_click(row, col) 
        if not human(players, player) or valid_move(grid, row, col):
            winner, gameover = play_move(grid, row, col, player)
            view_update(view, row, col, player) 
            player = 3 - player 
    play(view, msg, grid, players, player, winner, gameover)
```

La fonction commence en bloquant les interactions utilisateur puisque là, a priori, on a des coordonnées (`row` et `col`) à traiter : il ne faut donc surtout pas qu'un clic vienne lancer une action qui viendrait perturber le traitemen en cours.

Ensuite on positionne à 0 une variable locale pour mémoriser l'ID d'un éventuel joueur gagnant. On teste que `row` n'est pas `None` (la 1re fois c'est le cas, `row` vaudra `None` et on appelera directement la fonction `play`).  Si c'est le cas, on doit tester si le joueur courant est humain. Si oui, alors cela signifie que `row` et `col` sont des coordonnées sur la fenêtre de jeu et qu'il faut les transformer en coordonnées de notre grille de jeu. Ensuite, on demande au modèle de jouer ce coup (il s'agit de l'appel à `play_move`), à la vue de mettre à jour l'affichage et on passe au joueur suivant. Enfin on peut lancer le choix du coup suivant avec la fonction `play` :

```python
def play(view, msg, grid, players, player, winner, gameover):
    if gameover:
        stop(msg, winner)
    elif human(players, player):
        unblock_click(view, msg, grid, players, player, gameover)
        annonce_player(msg, player)
    else:
        row, col = choice(grid, players, player) # l'IA
        gameloop(view, msg, row, col, grid, players, player, gameover) 
```

Le rôle de la fonction `play` est de rappeler la boucle de jeu avec un nouveau coup. On commence par vérifier que la partie n'est pas terminée. Si elle ne l'est pas, on va obtenir un nouveau coup par un clic sur la zone de jeu si le joueur est humain ou par calcul si le joueur est la machine.

Pour le joueur humain, c'est la fonction `unblock_click` qui réalise ce travail en posant une *écoute* sur le clic souris avec comme action associée l'appel à la boucle de jeu.

```python
def unblock_click(view, msg, grid, players, player, gameover):
    view.screen.onclick(lambda x, y: gameloop(view, msg, x, y, grid, players, player, gameover))
```

La méthode `onclick` du module `turtle` fonctionne comme la méthode `onkeypress` vue précédemment à la différence que la fonction action doit avoir deux paramètres pour récupérer les coordonnées du point qui a été cliqué. Une fois de plus nous avons avons besoin d'appeler une fonction avec bien plus de paramètres et utilisons une lambda expression pour nous en sortir.

Voilà il nous resterait à commenter les diverses fonctions de la partie vue. Néanmoins, si elles sont fastidieuses à écrire (il s'agit de géométrie : calculer des coordonnées de points où faire nos dessins pour que l'ensemble soit cohérent), elles ne présentent pas vraiment de difficulté ou d'intérêt algorithmique particulier.

Le script complet est disponible ici : [tictactoe.py][2]

## Conclusion

Voilà notre présentation touche à sa fin. Elle était longue et j'espère que vous avez tenu jusqu'au bout. Mais comme d'habitude pas mal de concepts sont sous-jacents surtout quand on essaie de coder proprement. N'hésitez pas à revenir, à bien étudier le code, à aller approfondir certains concepts. 

Le principal inconvénient de cette version, me semble-t-il : l'utilisation de fonctions avec beaucoup (trop) d'arguments. En passant à la programmation objet on lève cet inconvénient tout en découpant encore plus les trois rôles : modèle, vue et contrôleur.

Je vous mets donc la version objet ici : [tictactoe_oo.py][3]


[1]:https://fr.wikipedia.org/wiki/Mod%C3%A8le-vue-contr%C3%B4leur
[2]:/tictactoe/tictactoe.py
[3]:/tictactoe/tictactoe_oo.py


