import socket
import json
import smbus2
import sensors_lib.MyBNO055 as MyBNO055
import time

i2cbus = smbus2.SMBus(1) 
mybno = MyBNO055.BNO055(i2cbus)
mybno.calibration()

adresse_socket = ("",8087)
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind(adresse_socket)
socket_server.listen(1)

print("En attente de connexion du client...")
socket_cree_pour_client, adresse_client = socket_server.accept()
print(f"Client connecté depuis {adresse_client}")

while True:
    try:
        a_json = json.dumps(mybno.read_linear_acceleration())
        socket_cree_pour_client.send(a_json.encode("utf-8"))
    except:
        break
    time.sleep(0.3)

print("Fin de la communication")
socket_cree_pour_client.close()
socket_server.close()
