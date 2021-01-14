import numpy as np
import random
import time
from numpy.lib import stride_tricks

class Foret(object):
    """La simulation de la forêt qui sera affichée."""

    def __init__(self,nC,nL):
        #taille de la forêt
        self.nC = nC
        self.nL = nL
        #probabilités de base.
        self.pNonArbre = 0.25
        self.p = 1.0
        self.pConsume = 0.033
        #initialisation
        self.grille = self.initialiserForet()
        self.vitesse = self.calculerEffetVent(1,np.pi / 4)
        self.mesh_v=self.mesher_vitesse()
        
    def mesher_vitesse(self):
        arr=np.ones((self.nL,self.nC,3,3))
        for i in range(self.nL):
            for j in range(self.nC):
                arr[i,j]=self.vitesse.copy()
        return arr

    def initialiserForet(self):
        """Initialisation de la forêt."""
        # creation de la grille
        etat = np.zeros((self.nL,self.nC))
        #initialisation de la grille
        for i in range(self.nL):
            for j in range(self.nC):
                #Certaines zones ne seront pas des arbres.
                if (random.random() < self.pNonArbre) or (i == (self.nL - 1)) or (i == 0) or j == (self.nC - 1) or (j == 0):
                    etat[i,j] = 2
        # choix du départ du feu
        etat[self.nL // 2,self.nC // 2] = 1
        return etat

    def evolutionFeu(self):
        """Evolution du feu"""
        #la grille est copiée afin que les modifications faites durant cette
        #itération n'affecte pas les calculs.

        #en feu
        grille1 = self.grille.copy()
        shape = (grille1.shape[0] - 2, grille1.shape[1] - 2, 3, 3)
        patches = stride_tricks.as_strided(grille1, shape=shape, strides=(2*grille1.strides))
        patches = (patches==1)
        patches=patches*self.mesh_v[1:(self.nL-1),1:(self.nC-1)]
        patches=patches.sum(axis=(-1, -2))/np.sum(self.vitesse)
        rdms=np.random.rand(self.nL-2,self.nC-2)#tirage
        on_fire=rdms<patches
        grille2=self.grille[1:(self.nL-1),1:(self.nC-1)]
        grille2[on_fire & (grille2 == 0)] = 1
        self.grille[1:(self.nL-1),1:(self.nC-1)]=grille2.copy()

        #consumé
        rdms=np.random.rand(self.nL,self.nC)#tirage
        self.grille[(rdms<self.pConsume) & (self.grille == 1)] = 3


### modèle physique
    def calculerEffetVent(self,un,alpha):
        """Calcule l'effet du vent."""
        vitesse_base = np.array(
            [[1,1,1],
            [1,1,1],
            [0,1,1]])
        vitesse_vent = np.zeros((3,3))
        for i in range(8):
            beta = i * np.pi / 4
            value = np.cos(beta - alpha)
            if value > 1e-10:
                vitesse_vent[1 + Foret.sgn(np.cos(beta)),1 + Foret.sgn(np.sin(beta))] = value
        vitesse_vent = (self.r(un)) * vitesse_vent
        print(np.flip(vitesse_vent.T,0))
        return np.flip(vitesse_base + vitesse_vent,0)

    def sgn(x):
        if abs(x) <= 1e-10:
            return 0
        return int(x / abs(x))

    def r(self,un):
        """Fonction clé du modèle physique, renvoie le rapport entre la vitesse sans vent, et la vitesse avec le vent donné."""
        return 5
