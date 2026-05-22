import filtres_2025 as filtre

# Kp : gain P
# Ki : gain I
# Kd : gain D
# sat : saturation (dans notre cas c'est 100)
# sample_time : ecart de temps entre chaque update de l'asservicement (environ 0.02 et 0.1)



class PID:
    def __init__(self, Kp, Ki, Kd, sat, sample_time, fc):
        self.Kp, self.Ki, self.Kd, self.sat, self.sample_time = Kp, Ki, Kd, sat, sample_time
        
        self.ret = 0            # valeur retourné par le block asservicement
        self.consigne = 0       # conssigne
        self.sum = 0            # intégrale
        self.old_erreur = None     # utilisé pour la dérivée

        self.dt_update = 0      # delta T entre chaque execution de l'asservicement
        self.derive_filtre = 0  # filtre pass-bas pour filtrer la dérivée

        self.Corr_Kp, self.Corr_Ki, self.Corr_Kd = 0, 0, 0
        self.mes = 0
        self.filtre_derive = filtre.PasseBas_ordre_1(fc)

        self.etat = True

    def __str__(self):
        return str(round(self.ret, 3)) + "\t" + \
                str(round(self.Corr_Kp, 3)) + "\t" + \
                str(round(self.Corr_Ki, 3)) + "\t" + \
                str(round(self.Corr_Kd, 3)) + "\t" + \
                str(round(self.mes, 3)) + "\t" + \
                str(round(self.derive_filtre, 3))
        
    def update(self, mes, dt):

        if not self.etat:
            return 0

        self.dt_update += dt
        self.mes = mes
        if self.dt_update < 1.0/self.sample_time:
            return self.ret

        erreur = self.consigne - mes

        self.Corr_Kp = self.Kp * erreur



        self.sum += erreur * self.dt_update
        if self.Ki != 0:
            if self.sum > self.sat/self.Ki: self.sum = self.sat / self.Ki        #  saturation du correcteur i
            elif self.sum < -self.sat/self.Ki: self.sum = -self.sat / self.Ki

        self.Corr_Ki = self.Ki * self.sum

        


        if self.old_erreur == None: self.old_erreur = erreur
        derive = (erreur - self.old_erreur) / self.dt_update
        self.old_erreur = erreur

        self.derive_filtre = self.filtre_derive.filtre1(derive, self.dt_update)    #  filtrage de la dérivée

        

        self.Corr_Kd = self.Kd * self.derive_filtre


        self.ret = self.Corr_Kp + self.Corr_Ki + self.Corr_Kd


        if self.ret > self.sat: self.ret = self.sat    #  saturation de tout les correcteurs
        elif self.ret < -self.sat: self.ret = -self.sat

        self.dt_update = 0
        return self.ret
    

    def loadPIDJson(self, json_data):
        self.Kp = json_data["Kp"]
        self.Ki = json_data["Ki"]
        self.Kd = json_data["Kd"]
        self.sample_time = json_data["sample_time"]
        self.filtre_derive.fc = json_data["filtre_derivee"]
        self.sat = json_data["saturation"]
        print("loadPIDJson: ",self.sat)

        

    def sendPIDJson(self):
        json_data = {}
        json_data["Kp"] = self.Kp
        json_data["Ki"] = self.Ki
        json_data["Kd"] = self.Kd
        json_data["sample_time"] = self.sample_time
        json_data["filtre_derivee"] = self.filtre_derive.fc
        json_data["saturation"] = self.sat
        return json_data