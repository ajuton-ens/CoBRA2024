import time

class PID:
	"""Un correcteur PID"""

	def __init__(self, kp, ki, kd, consigne_init):
		
		self.kp = kp
		self.ki = ki
		self.kd = kd
		self._consigne = consigne_init
		self.temps_precedent = time.time()

	def update(self, mesure):
		ecart_mesure = self._consigne - mesure
		temps_actuel = time.time()
		ecart_temps = temps_actuel - self.temps_precedent
		self.temps_precedent = temps_actuel

		integrale = self._consigne * ecart_temps + 0.5 * (mesure - self._consigne) * ecart_temps

		derivee = (mesure - self._consigne) / ecart_temps

		return self.kp * ecart_mesure + self.ki * integrale + self.kd * derivee


	@property
	def consigne(self):
		return self._consigne

	@consigne.setter
	def consigne(self, nouvelle_consigne):
		self._consigne = nouvelle_consigne




class Control_functions:

	def __init__(self):
		self.temps_precedent_yaw_control = time.time()
		self.yaw_control = false

	def yaw_control(self, seuil, mesure, offset):
		"""Fonction pour controller le yaw en prenant en compte le retard"""

		temps_actuel = time.time()
		if not self.yaw_control:
			temps_init = temps_actuel

		if temps_actuel - temps_precedent_yaw_control > 0.5:
			self.yaw_control = false
		elif (mesure > seuil + offset) | (mesure < -seuil + offset):
			self.yaw_control = true
			
		
		if self.yaw_control & mesure > 0 & temps_init < 1:
			self.temps_precedent_yaw_control = temps_actuel
			return 0.1/(temps_actuel - temps_init + 0.1)
		elif self.yaw_control & mesure < 0 & temps_init < 1:
			self.temps_precedent_yaw_control = temps_actuel
			return -0.1/(temps_actuel - temps_init + 0.1)
		
		return 0
