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


lock=threading.Lock()

pair_of_clients={}
CLIENTS=[]



def set_client_state(client, state):
    with lock:
        pair_of_clients[client] = state





def send_data(data, sender):
    sender.send(data.encode("utf-8"))



def check_client_state(theOne, pair_of_client, data, current_connected_client, current_Talking_Client):
    key = {key: value for key , value in pair_of_client.items() if key == theOne[0].fileno()}

    keycheck = key.values()
    keycheck = [i for i in keycheck]
    keycheck = keycheck[0]
    if keycheck == "closed":

        data += f":{current_connected_client.fileno()}"
        print(data)
        data += ":closed"
        send_data(data, current_Talking_Client)

    else:

        data += ":opened"
        send_data(data, current_Talking_Client)




def receive_message(current_connected_client):

    global pair_of_clients
    current_Talking_Client=[]
    while True:

        try:
            data = current_connected_client.recv(1024).decode()




            if data in ["opened","closed"]:
                set_client_state(current_connected_client.fileno(), data)
                continue




            if "someone" in data:

                data = json.loads(data)


                someone=int(data["someone"])
                target_client=[client for client in CLIENTS if client.fileno() == someone]

                current_Talking_Client.clear()
                current_Talking_Client.append(target_client[0])


            if "someone" not in data:
                check_client_state(target_client, pair_of_clients, data, current_connected_client, current_Talking_Client[0])




        except ConnectionResetError as E:
            print(E)
            for i in CLIENTS:
                if i==current_connected_client:
                    CLIENTS.remove(i)
            break



        except ConnectionAbortedError:
            break

    current_connected_client.close()













def listen_to_clients():
    global CLIENTS,nofclients
    while True:
        current_Connected_Client, client_address = sockserver.accept()
        with lock:
            CLIENTS.append(current_Connected_Client)


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


    threads = threading.Thread(target=receive_message, args=(handled_cleint,))
    threads.start()


# Start the thread to handle clients

# threads.start()
# threads.join()










thread1=threading.Thread(target=listen_to_clients, daemon=True)
thread1.start()
thread1.join()


