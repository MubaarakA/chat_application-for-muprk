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


PAIR_OF_CLIENTS={}
CLIENTS=[]



def Set_Client_State(client, state):
    PAIR_OF_CLIENTS[client] = state





def Send_Data(data,sender):
    sender.send(data.encode("utf-8"))



def Check_Client_State(theOne,pair_of_client,data,current_connected_client,current_Talking_Client):
    key = {key: value for key, value in pair_of_client.items() if key == theOne[0].fileno()}

    keycheck = key.values()
    # print(keycheck)
    keycheck = [i for i in keycheck]
    keycheck = keycheck[0]
    if keycheck == "closed":

        data += f":{current_connected_client.fileno()}"
        print(data)
        data += ":closed"
        Send_Data(data,current_Talking_Client)

    else:

        data += ":opened"
        Send_Data(data, current_Talking_Client)




def recv(current_connected_client):

    global PAIR_OF_CLIENTS

    current_Talking_Client=[]
    while True:

        try:
            data = current_connected_client.recv(1024).decode()




            if data in ["opened","closed"]:
                Set_Client_State(current_connected_client.fileno(), data)
                continue




            if "someone" in data:

                data = json.loads(data)


                someone=int(data["someone"])
                theOne=[client for client in CLIENTS if client.fileno() == someone]

                current_Talking_Client.clear()
                current_Talking_Client.append(theOne[0])


            if "someone" not in data:
                Check_Client_State(theOne, PAIR_OF_CLIENTS, data, current_connected_client, current_Talking_Client[0])










        except ConnectionResetError as E:
            print(E)
            for i in CLIENTS:
                if i==current_connected_client:
                    CLIENTS.remove(i)
            break



        except ConnectionAbortedError:
            nofclients = len(CLIENTS)
            break

    current_connected_client.close()















def Listen_To_Clients():
    global CLIENTS,nofclients
    while True:
        current_Connected_Client, client_address = sockserver.accept()
        CLIENTS.append(current_Connected_Client)
        nofclients = len(CLIENTS)


        threads = threading.Thread(target=handle_clients,args=(current_Connected_Client,))
        threads.start()
    if not CLIENTS:
        print("bye")



def handle_clients(handled_cleint):

    print(f"Accepted connection from {handled_cleint}")
    if len(CLIENTS)>1:
        for i in CLIENTS:
            for m in CLIENTS:
                if i.fileno() != m.fileno():
                    i.send(f"combo:{m.fileno()}\n".encode("utf-8"))
                    print(i.fileno(), m.fileno())
                    print()


    threads = threading.Thread(target=recv, args=(handled_cleint,))
    threads.start()


# Start the thread to handle clients

# threads.start()
# threads.join()










thread1=threading.Thread(target=Listen_To_Clients,daemon=True)
thread1.start()
thread1.join()


