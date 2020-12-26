
import numpy as np
import random
import tkinter as tk
import time



class Fenetre(tk.Tk):
    def __init__(self):
        super().__init__()
        self.nC = 75
        self.nL = 150
        self.grille = np.zeros((self.nL,self.nC))
        self.rectGrid=[[(None,None) for i in range(self.nC)] for j in range(self.nL)]
        self.a = 10
        self.pNonArbre = 0.25
        self.p = 0.1
        self.pConsume = 0.04        
        self.grille = self.initialiserForet()
        self.creerLayout()
    
    def creerLayout(self):
        self.title("Le Feu")
        self.canvas = tk.Canvas(self, width=15*self.a*self.nC+1, height=self.a*self.nL+1, highlightthickness=2)
        self.creerGrille()
        self.bou1 = tk.Button(self,text='Propagation', width=8, command=self.suivant)
        self.bou1.pack(side='top')
        self.canvas.pack(fill='both')

    def modifierGrille(self):
        nL,nC = self.grille.shape
        for x in range(nL):
            for y in range(nC):
                if self.grille[x,y] == 0:
                    coul = "green"
                elif self.grille[x, y] == 2:
                    coul = "white"
                elif self.grille[x,y] == 3:
                    coul = "black"
                else: 
                    coul = "red"
                recta,coulor=self.rectGrid[x][y]
                if coul != coulor:
                    self.canvas.itemconfig(recta, fill=coul)
                    self.rectGrid[x][y]=(recta,coul)

    def creerGrille(self):
        nL,nC = self.grille.shape
        for x in range(nL):
            for y in range(nC):
                if self.grille[x,y] == 0:
                    coul = "green"
                elif self.grille[x, y] == 2:
                    coul = "white"
                elif self.grille[x,y] == 3:
                    coul = "black"
                else: 
                    coul = "red"
                recta=self.canvas.create_rectangle((x*self.a, y*self.a, (x+1)*self.a, (y+1)*self.a), outline="gray", fill=coul)
                self.rectGrid[x][y]=(recta,coul)

    def initialiserForet(self):       
        # creation de la grille
        etat = np.zeros((self.nL,self.nC))
        for i in range (self.nL):
            for j in range(self.nC):
                if random.random() < self.pNonArbre or i == self.nL-1 or i ==0 or j == self.nC-1 or j==0:
                    etat[i,j]=2
        # choix du départ du feu
        i = random.randint(0,self.nL-1)
        j = random.randint(0,self.nC-1)
        etat[i,j] = 1
        return etat

    def r(self,un):
        return 5

    def prob(self,x,y,grille1):
        k=1.2
        un=1
        if grille1[(x-1)%self.nL, y] == 1:
            return self.p*k*self.r(un)
        if grille1[x,(y+1)%self.nC] == 1:
            return self.p*k*self.r(un)*self.nC/self.nL
        if grille1[(x+1)%self.nL,y] == 1 or grille1[x,(y-1)%self.nC] == 1:
            return self.p
        return 0

    def evolutionFeu(self):
        grille1  = self.grille.copy()
        nL,nC = grille1.shape
        for x in range(nL):
            for y in range(nC):
                if grille1[x,y] == 1:
                    if random.random()<self.pConsume:
                        self.grille[x,y] = 3
                elif grille1[x,y]==0:
                     p1=self.prob(x,y,grille1)
                     if random.random() < p1:
                         self.grille[x,y] = 1

    def suivant(self):
        self.evolutionFeu()
        self.modifierGrille()
        self.after(50,self.suivant)


###########

fenetre=Fenetre()
fenetre.state('zoomed')
fenetre.mainloop()