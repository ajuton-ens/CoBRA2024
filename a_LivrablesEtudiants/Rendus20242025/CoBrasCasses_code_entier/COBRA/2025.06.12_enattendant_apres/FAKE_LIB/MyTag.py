import numpy as np

class Tag :
    def __init__(self):
        self.WIDTH = 1536
        self.HEIGH = 864

        #coefficients de distorsion de la camera

        self.mtx = np.array([[ 977.08159964 	,  0.00000000e+00,  789.18761132],[ 0.00000000e+00,  977.14004212, 434.47165678],[ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
        self.dist = np.array([[-0.02727091,  0.1312434,   0.00479796,  0.00269239, -1.30723302]])
        self.fx = self.mtx[0][0]
        self.cx = self.mtx[0][2]
        self.fy = self.mtx[1][1]
        self.cy = self.mtx[1][2]
        
        #Positions des tags dans l'environnement

    def Detection_Tags(self):
        tags=[0,0,0,0]
        return tags

    def calculAngles(self,R):
        return np.degrees(np.array([0, 0, 0]))

    def nb_tag_detect(self):
        tags=self.Detection_Tags()
        n=len(tags)
        return n

    def localisation(self):
        """Renvoie:
            (x, y, z, alpha)
            - La position de la caméra (x, y, z) dans le repère du sol
            - L'angle de lacet (c'est le seul qui nous interesse dans le cas d'un dirigeable
        """
        #            X                    Y                     Z              Lacet
        return(0, 0, 0, 0)
