import tkinter as tk
from Foret import Foret
import time

class Fenetre(tk.Tk):
    """La fenêtre qui affichera la forêt simulée."""

    def __init__(self):
        super().__init__()
        #la forêt qui sera simulée.
        self.foret=Foret(75,150)
        #Grille d'affichage correspondant à la grille forêt.
        self.rectGrid=[[(None,None) for i in range(self.foret.nC)] for j in range(self.foret.nL)]
        #taille d'affichage d'un carreau de la grille forêt.
        self.a = 10
        #Code couleur pour faire correspondre la simulation à l'affichage.
        self.colorCode={0:'green',1:'red',2:'white',3:'black'}
        self.creerWidgets()
    
    def creerWidgets(self):
        """Création et disposition des widgets."""
        self.title("Le Feu")
        #le canvas pour afficher la grille sur l'écran.
        self.canvas = tk.Canvas(self, width=15*self.a*self.foret.nC+1, height=self.a*self.foret.nL+1, highlightthickness=2)
        self.creerGrille()
        #le bouton pour allumer le feu
        self.bou1 = tk.Button(self,text='Propagation', width=8, command=self.suivant)
        self.bou1.pack(side='top')
        self.canvas.pack(fill='both')

    def modifierGrille(self):
        """Affichage sur la fenêtre des modifications enregistrées dans la forêt."""
        for x in range(self.foret.nL):
            for y in range(self.foret.nC):
                coul=self.colorCode[self.foret.grille[x,y]]
                recta,coulor=self.rectGrid[x][y]
                #la modification de la grille d'affichage n'a lieu que quand nécessaire afin d'améliorer les performances.
                if coul != coulor:
                    #modification de la couleur du rectangle affiché sur l'écran.
                    self.canvas.itemconfig(recta, fill=coul)
                    #modification du rectangle et de la couleur stockés dans la grille d'affichage.
                    self.rectGrid[x][y]=(recta,coul)

    def creerGrille(self):
        """Création et initialisation des carreaux qui constituent la grille de la fenêtre."""
        for x in range(self.foret.nL):
            for y in range(self.foret.nC):
                coul=self.colorCode[self.foret.grille[x,y]]
                recta=self.canvas.create_rectangle((x*self.a, y*self.a, (x+1)*self.a, (y+1)*self.a), outline="gray", fill=coul)
                #les rectangles sont affichés puis stockés avec leur couleur dans la grille d'affichage.
                self.rectGrid[x][y]=(recta,coul)

    def suivant(self):
        """Fonction appelée régulièrement pour faire avancer la simulation."""

        #évolution de la forêt.
        self.foret.evolutionFeu()
        #affichage des modifications de la forêt sur la grille.
        self.modifierGrille()
        #itération suivante.
        self.after(50,self.suivant)

