class PID:
    def __init__(self, Kp, Ki, Kd, consigne):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.consigne = consigne

        self.previous_error = 0
        self.integral = 0

    def compute(self, measured_value):
        
        
        """Calcule la sortie PID en fonction de la valeur mesurée"""
        error = self.consigne - measured_value

        # Terme proportionnel
        P = self.Kp * error

        # Terme intégral
        self.integral += error
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+I+D

        # Sortie PID (limitée entre 0 et 100 pour la vitesse du moteur)
        output = max(min(R, 50), 10)
        return output
    
    def compute2(self, measured_value):
        
        
        """Calcule la sortie PID en fonction de la valeur mesurée"""
        error = self.consigne - measured_value
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360  

        # Terme proportionnel
        P = self.Kp * error

        # Terme intégral
        self.integral += error
        self.integral = max(min(self.integral, 100), -100)
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+D
        print (R)
        # Sortie PID (limitée entre -50,-20 et 20,50 pour la vitesse du moteur)
        if R<0 : 
            output = min(max(R, -50), -20)
        else :
            output = max(min(R, 50), 20)
        return output
    
    def compute3(self, error):
               
        """Calcule la sortie PID en fonction de l'erreur mesurée"""

        # Terme proportionnel
        P = self.Kp * error

        # Terme intégral
        self.integral += error
        self.integral = max(min(self.integral, 100), -100)
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+D

        # Sortie PID (limitée entre 0 et 100 pour la vitesse du moteur)
        if R>0 : 
            output = max(min(R, 50), 20)
        else : 
            output=min(max(R,50),20)
        return output