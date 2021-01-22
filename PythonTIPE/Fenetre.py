import tkinter as tk
from Foret import Foret
import numpy as np
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
        self.colorCode={0:'forest green',1:'red',2:'ivory',3:'gray29'}
        #initialisation
        self.creerWidgets()
        self.playing=False
        self.skip=False
        self.suivant()
    
    def creerWidgets(self):
        """Création et disposition des widgets."""
        self.title("Le Feu")
        #le canvas pour afficher la grille sur l'écran.
        self.canvas = tk.Canvas(self, width=15*self.a*self.foret.nC+1, height=self.a*self.foret.nL+1, highlightthickness=2)
        self.creerGrille()

        #le bouton pour allumer le feu
        fra=tk.Frame(self)
        self.bouText=tk.StringVar()
        #le texte du bouton est dynamique, il change selon si l'on est au début, en pause ou en cours de propagation.
        self.bouText.set("Commencer")
        self.bou1 = tk.Button(fra,textvariable=self.bouText, width=15, command=self.play)
        self.bou1.pack(side='left')
        #le slider qui permet de modifier l'angle du vent
        la=tk.Label(fra,text="Angle du vent (°)")
        la.pack(side='right')
        self.scala2 = tk.Scale(fra, from_=0, to=360, orient=tk.HORIZONTAL)
        self.scala2.set(45)
        self.scala2.pack(side='right')
        #slider pour l'humidité
        la=tk.Label(fra,text="humidité (%)")
        la.pack(side='right')
        self.scala_humid = tk.Scale(fra, from_=1, to=50, orient=tk.HORIZONTAL)
        self.scala_humid.set(20)
        self.scala_humid.pack(side='right')
        #slider pour la vitesse du vent
        la=tk.Label(fra,text="vitesse du vent (m/s)")
        la.pack(side='right')
        self.scala_vitesse = tk.Scale(fra, from_=0, to=10, orient=tk.HORIZONTAL)
        self.scala_vitesse.set(2)
        self.scala_vitesse.pack(side='right')

        fra.pack()
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
        #l'affichage est directement mis à jour (les couleurs changent sur l'écran)
        self.canvas.update()

    def creerGrille(self):
        """Création et initialisation des carreaux qui constituent la grille de la fenêtre."""
        for x in range(self.foret.nL):
            for y in range(self.foret.nC):
                coul=self.colorCode[self.foret.grille[x,y]]
                recta=self.canvas.create_rectangle((x*self.a, y*self.a, (x+1)*self.a, (y+1)*self.a), outline="gray", fill=coul)
                #les rectangles sont affichés puis stockés avec leur couleur dans la grille d'affichage.
                self.rectGrid[x][y]=(recta,coul)

    def play(self):
        self.playing = (not self.playing)
        if self.playing:
            #désactiver les curseurs pour ne pas les bouger pendant que la simulation est en cours.
            self.scala2.config(state='disabled')
            self.scala_humid.config(state='disabled')
            self.scala_vitesse.config(state='disabled')
            self.bouText.set("Pause")
        else:
            #réactiver les curseurs pour autoriser une modification pendant la pause.
            self.scala2.config(state='normal')
            self.scala_humid.config(state='normal')
            self.scala_vitesse.config(state='normal')
            self.bouText.set("Reprendre")
        if self.playing:
            #après avoir repris on enregistre les éventuelles modifications de l'angle du vent.
            self.foret.mesher_vitesse(self.scala_vitesse.get(),np.pi/180 * self.scala2.get(),self.scala_humid.get()/100)

    def suivant(self):
        """Fonction appelée régulièrement pour faire avancer la simulation."""
        #itération suivante appelée au début pour être sûr que l'intervalle soit constant.
        self.after(200,self.suivant)
        #la forêt n'est pas modifiée si on est en pause.
        if self.playing:
            #évolution de la forêt.
            self.foret.evolutionFeu()
            #affichage des modifications de la forêt sur la grille.
            if not self.skip:
                #le skip est utilisé dans le cas où la modification de l'affichage prend plus de 200ms.
                #éviter que l'itération suivante modifie l'affichage tant que cette itération n'a pas fini.
                #les problèmes de performance ne ralentiront donc pas le feu.
                #en revanche, en cas de problème de performance, l'affichage sera mis à jour à des intervalles plus espacés.
                self.skip=True
                self.modifierGrille()
                self.skip=False
