import numpy as np
import random
import time
from numpy.lib import stride_tricks
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

class Foret(object):
    """La simulation de la forêt qui sera affichée."""
    def __init__(self,nC,nL):
        #taille de la forêt.
        self.nC = nC
        self.nL = nL
        #paramètre (coeff de l'humidité utilisé à deux endroits).
        self.a = 2.10
        #probabilités de base.
        self.pNonArbre = 0.25
        #coefficient d'extinction
        self.coeffExtinction = 0.05
        #probabilité d'extinction des cases à l'intérieur du périmètre du feu
        #(pas de végétal adjacent).
        self.coeffExtinction_interieur = 0.2
        #valeurs par défaut des paramètres.
        self.distortion_temps = 1
        self.v_vent_defaut = 3
        self.humidite_defaut = 0.2
        #initialisation
        self.grille = self.initialiserForet()
        self.calculer_modele(self.v_vent_defaut,np.pi / 4, self.humidite_defaut)
        
    def initialiserForet(self):
        """Initialisation de la forêt."""
        # creation de la grille.
        etat = np.zeros((self.nL,self.nC))
        #initialisation de la grille.
        for i in range(self.nL):
            for j in range(self.nC):
                if (random.random() < self.pNonArbre) or (i == (self.nL - 1)) or (i == 0) or j == (self.nC - 1) or (j == 0):
                    etat[i,j] = 2
        # choix du départ du feu.
        etat[self.nL // 2,self.nC // 2] = 1
        return etat

    def evolutionFeu(self):
        """Evolution du feu: calcul des probabilités et tirage."""

        #tous ces calculs sont fait via numpy sans boucle for.
        #numpy lance les calculs directement en C ce qui permet une exécution
        #plus rapide.

        #voisinages
        #on copie la grille pour s'assurer que les calculs soient effectués
        #avant les modifications.
        grille1 = self.grille.copy()
        #les strides sont habituellement utilisées pour du traitement d'image
        #par exemple pour flouter une image en remplaçant un point par la
        #moyenne de ses voisins.
        #Le principe est d'augmenter le nombre de dimensions ici en passant de
        #deux à 4 dimensions.
        #on transforme un tableau de nombres en un tableau de matrices 3x3
        #la matrice 3x3 qui remplacent le nombre contient le nombre lui-même et
        #ses 8 voisins.
        #les strides manipulent directement la représentation binaire du
        #tableau dans la mémoire.
        #bien que risquée et à manipuler avec extrême précaution, cette méthode
        #offre un GIGANTESQUE gain de performance.
        #plus d'info ici:
        #https://realpython.com/numpy-array-programming/#image-feature-extraction
        shape = (grille1.shape[0] - 2, grille1.shape[1] - 2, 3, 3)
        patches = stride_tricks.as_strided(grille1, shape=shape, strides=(2 * grille1.strides))

        #allumage
        #on coupe les bords car les cases sans voisins n'ont pas été stridées.
        #la multiplication termes à termes annulera les coefficients de
        #vitesses pour les cases éteintes.
        allumage = (patches == 1) * self.mesh_v[1:(self.nL - 1),1:(self.nC - 1)]
        #on somme ensuite les matrices de vitesse avant de les diviser par le
        #total pour obtenir les probabilités.
        allumage = allumage.sum(axis=(-1, -2)) / (self.mesh_v[1:(self.nL - 1),1:(self.nC - 1)]).sum(axis=(-1, -2))
        #on tire un tableau de nombre aléatoires (un nombre par case)
        rdms = np.random.rand(self.nL - 2,self.nC - 2)#tirage
        grille2 = self.grille[1:(self.nL - 1),1:(self.nC - 1)]
        #on compare ces nombres avec les probabilités d'allumage et on allume
        #si le nombre est en-dessous de la probabilité.
        grille2[(rdms < allumage) & (grille2 == 0)] = 1

        #extinction
        #cases n'ayant pas de végétation adjacentes sont considérées comme
        #ayant plus de chances de s'éteindre.
        #le front de flamme étant déjà passé aux autres cases, le peu de feu
        #qui reste s'éteint plus facilement.
        #On considère ces cases comme "finies".
        extinction = (patches == 0)#cases de végétal
        extinction[extinction == True] = 1
        extinction = extinction.sum(axis=(-1, -2))
        #le tableau contient maintenant le nombre de cases de végétal
        #adjacentes pour chaque case.
        rdms = np.random.rand(self.nL - 2,self.nC - 2)#tirage
        pcs_interieur = 1 - np.exp(-self.coeffExtinction_interieur * self.distortion_temps)
        grille2[(extinction == 0) & (grille2 == 1) & (rdms < pcs_interieur)] = 3
        #la probabilité d'extinction étant adjacente à des cases de végétal.
        pcons_perimetre = 1 - np.exp(-self.coeffExtinction * self.distortion_temps)
        grille2[(extinction != 0) & (rdms < pcons_perimetre) & (grille2 == 1)] = 3

        #update
        self.grille[1:(self.nL - 1),1:(self.nC - 1)] = grille2.copy()

### modèle physique
    def calculer_modele(self,un,alpha,humidite):
        """Calcul des tableaux de vitesses et de la distortion temporelle en fonction des nouvelles valeurs des paramètres."""
        #calcul de la matrice de vitesse
        mat_direction = self.calculerMatriceDirectionVent(alpha)
        #à chaque point on associe sa matrice de vitesse 3x3
        vit = self.r(un,humidite) * mat_direction + np.ones((3,3))
        print(vit)
        arr = np.ones((self.nL,self.nC,3,3))
        for i in range(self.nL):
            for j in range(self.nC):
                #pour l'instant, pas de densité de végétation donc la vitesse
                #est pareille partout.
                arr[i,j] = vit
        self.mesh_v = arr
        #selon les rapports de vitesse, le temps est accéléré ou décéléré
        self.distortion_temps = ((1 + self.a * humidite) / (1 + self.a * self.humidite_defaut)) * (self.r(self.v_vent_defaut,self.humidite_defaut) / (self.r(un,humidite)))


    def calculerMatriceDirectionVent(self,alpha):
        """Calcule la matrice de direction du vent."""
        vitesse_vent = np.zeros((3,3))
        for i in range(8):
            #on fait tourner un angle par les 8 directions.
            beta = i * np.pi / 4
            #voir diapo pour les justification des calculs
            value = np.cos(beta - alpha)
            #10^(-10) au lieu de 0 pour les erreurs de calcul de flottant sur
            #les sin et cos.
            #seules les valeurs strictements positives doivent être prises en
            #compte.
            #dans le cas contraire, on est contre le vent et la propagation
            #sera prise comme sans vent.
            #TODO: revoir pour comment utiliser la matrice des 1
            ##pas top pour l'instant affiner quand les vrais calculs de r
            ##seront possibles.
            if value > 1e-10:
                #modification de la case correspondante dans la matrice du
                #vent.
                #par exemple (1,1)+(1,1)=(2,2) pour 45°.
                vitesse_vent[1 + Foret.sgn(np.cos(beta)),1 + Foret.sgn(np.sin(beta))] = value
        #on utilise flip car l'axe des y de la grille est inversé.
        return np.flip(vitesse_vent,0)

    def sgn(x):
        #1 si x>0, 0 si x=0, -1 si x<0.
        #on utilise 10^(-10) au lieu de 0 pour prendre en compte les erreurs de
        #flottant.
        if abs(x) <= 1e-10:
            return 0
        return int(x / abs(x))

    def r(self,un,humidite):
        """Fonction clé du modèle physique, renvoie le rapport entre la vitesse sans vent, et la vitesse avec le vent donné."""
        A0 = 5.73
        b0 = 0.23
        rac = 1 + ((b0 * un - 1) / ((b0 * un) ** 2 + 1) ** (1 / 2))
        A = (A0 / ((1 + self.a * humidite) ** 3)) * rac
        A13 = A ** (1 / 3)
        B = A ** 2 + 9 * A + 3 * ((A + 81 / 4) ** (1 / 2)) + 27 / 2
        num = B ** (2 / 3) + A13 * (A + 6)
        den = B ** (1 / 3)
        r = 1 + (A13 / 3) * ((num / den) + A13 ** 2)
        return r

