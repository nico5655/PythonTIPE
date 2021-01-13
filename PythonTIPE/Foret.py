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
        self.p = 1.0
        self.pConsume = 0.033
        #initialisation
        self.grille = self.initialiserForet()
        self.vitesse = self.calculerEffetVent(1,np.pi/4)

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
        #i = random.randint(0,self.nL-1)
        #j = random.randint(0,self.nC-1)
        etat[self.nL//2,self.nC//2] = 1
        return etat

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

### modèle physique
    def prob(self,x,y,grille1):
        """Calcul de la probabilité d'une case de s'enflammer. Fonction faisant le lien avec le modèle physique."""
        omega=0
        for i in range(8):
            beta=i*np.pi/4
            if grille1[x-Foret.sgn(np.cos(beta)),y+Foret.sgn(np.sin(beta))]==1:
                omega+=self.vitesse[1+Foret.sgn(np.cos(beta)),1+Foret.sgn(np.sin(beta))]
        omega = omega / np.sum(self.vitesse)
        return self.prob0(x,y)*omega

    def prob0(self,x,y):
        return self.p # à revoir, la densité de la végétation devrait être directement utilisée pour le calcul de r, donc de p principal.

    def calculerEffetVent(self,un,alpha):
        """Calcule l'effet du vent."""
        vitesse_base=np.array([
            [1,1,1],
            [1,1,1],
            [0,1,1]
            ])
        vitesse_vent=np.zeros((3,3))
        for i in range(8):
            beta=i*np.pi/4
            value=np.cos(beta-alpha)
            if value > 1e-10:
                vitesse_vent[1+Foret.sgn(np.cos(beta)),1+Foret.sgn(np.sin(beta))]=value
        vitesse_vent = (self.r(un))*vitesse_vent
        print(vitesse_vent.T)
        return vitesse_base+vitesse_vent

    def sgn(x):
        if abs(x) <= 1e-10:
            return 0
        return int(x/abs(x))

    def r(self,un):
        """Fonction clé du modèle physique, renvoie le rapport entre la vitesse sans vent, et la vitesse avec le vent donné."""
        return 5
