import json
import threading
import socket







Server = socket.gethostbyname(socket.gethostname())
port = 8080
ADDR = (Server, port)

# Create and bind the server socket
sockserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockserver.bind(ADDR)
sockserver.listen()  # Start listening for connections

print(f"Server started at {Server} on port {port}")
sockserver.listen()


Clients=[]

def recv(Current_Connected_Client):

    choose_some_one=False
    current_Talking_Client=[]
    while True:

        try:
            data = Current_Connected_Client.recv(1024).decode()
            if "someone" in data:
                choose_some_one=True

            if choose_some_one:
                print(data)
                data = json.loads(data)

                for i in Clients:
                    if int(data["someone"]) == i.fileno():
                        if current_Talking_Client:
                            current_Talking_Client = []
                        else:
                            current_Talking_Client.append(i)

                        current_Talking_Client.append(i)
                        i.send(f"server:some wants to talk to you please talk with {Current_Connected_Client.fileno()} ".encode("utf-8"))

                        choose_some_one = False
                        break
            if "someone" not in data:
                current_Talking_Client[0].send(data.encode("utf-8"))


        except ConnectionResetError as E:
            print(E)
            for i in Clients:
                if i==Current_Connected_Client:
                    Clients.remove(i)



        except ConnectionAbortedError:
            nofclients = len(Clients)
            break

    Current_Connected_Client.close()















def Listen_To_Clients():
    global Clients,nofclients
    while True:
        current_Connected_Client, client_address = sockserver.accept()
        Clients.append(current_Connected_Client)
        nofclients = len(Clients)


        threads = threading.Thread(target=handle_clients,args=(current_Connected_Client,))
        threads.start()
    if not Clients:
        print("bye")



def handle_clients(handled_cleint):

    print(f"Accepted connection from {handled_cleint}")
    if len(Clients)>1:
        for i in Clients:
            for m in Clients:
                if i.fileno() != m.fileno():
                    i.send(f"combo:{m.fileno()}\n".encode("utf-8"))
                    print(i.fileno(), m.fileno())
                    print()
    else:
        handled_cleint.send("server:this is no one to send message".encode("utf-8"))

    threads = threading.Thread(target=recv, args=(handled_cleint,))
    threads.start()


# Start the thread to handle clients

# threads.start()
# threads.join()










thread1=threading.Thread(target=Listen_To_Clients,daemon=True)
thread1.start()
thread1.join()


