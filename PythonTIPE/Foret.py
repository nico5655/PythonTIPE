import numpy as np
import random
import time

class Foret(object):
    """La simulation de la forêt qui sera affichée."""

    def __init__(self,nC,nL):
        #taille de la forêt
        self.nC=nC
        self.nL=nL
        #probabilités de base.
        self.pNonArbre = 0.25
        self.p = 0.1
        self.pConsume = 0.04
        #initialisation
        self.grille = self.initialiserForet()

    def initialiserForet(self):
        """Initialisation de la forêt."""
        # creation de la grille
        etat = np.zeros((self.nL,self.nC))
        #initialisation de la grille
        for i in range (self.nL):
            for j in range(self.nC):
                #Certaines zones ne seront pas des arbres.
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
        """Calcul de la probabilité d'une case de s'enflammer. Fonction liée au modèle physique."""
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
        """Evolution du feu"""
        #la grille est copiée afin que les modifications faites durant cette itération n'affecte pas les calculs.
        grille1  = self.grille.copy()
        nL,nC = grille1.shape
        for x in range(nL):
            for y in range(nC):
                #les cases qui brûlent peuvent être consumées.
                if grille1[x,y] == 1:
                    if random.random()<self.pConsume:
                        self.grille[x,y] = 3
                #les cases vertes peuvent être allumées.
                elif grille1[x,y]==0:
                     p1=self.prob(x,y,grille1)
                     if random.random() < p1:
                         self.grille[x,y] = 1

    