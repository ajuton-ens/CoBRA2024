import threading

def fonction(param1, param2):
    pass


QUIT = True
while not QUIT:

    th = threading.Thread(target=fonction, args=(param1, param2,), daemon=True)
    #daemon -> le thread se fermera lorsque le programme python sera terminé
    th.start()
