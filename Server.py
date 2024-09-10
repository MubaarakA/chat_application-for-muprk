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

clients_state={}
CLIENTS=[]



def set_client_state(client, state):
    with lock:
        if "opened" in state:
            opened_window_client = state.split(":")[1]

            clients_state[client]={"opened":opened_window_client}
        else:
             clients_state[client] = {state}
        print(clients_state)





def send_data(data, sender):
    sender.send(data.encode("utf-8"))



def check_client_state(theOne, client_state, data, current_connected_client, current_Talking_Client):
    print("ehchhe")
    key = {key: value for key , value in client_state.items() if key == theOne[0].fileno()}

    keycheck = key.values()
    keycheck = [i for i in keycheck]

    keycheck = keycheck[0]
    print(keycheck,"key")
    if  "closed" in keycheck:

        data += f":{current_connected_client.fileno()}"
        data += ":closed"
        send_data(data, current_Talking_Client)
        return

    if int(keycheck["opened"])==int(current_connected_client.fileno()):
        data += ":opened"
        send_data(data, current_Talking_Client)
        return

    else:
        data += f":{current_connected_client.fileno()}"
        data += ":closedto"
        send_data(data, current_Talking_Client)






def receive_message(current_connected_client):

    global clients_state
    current_Talking_Client=[]
    while True:

        try:
            data = current_connected_client.recv(1024).decode()
            print(data,"my")




            if  "opened" in data:
                set_client_state(current_connected_client.fileno(), data)
                continue
            else:
                if data=="closed":
                    set_client_state(current_connected_client.fileno(), data)
                    continue





            if "someone" in data:

                data = json.loads(data)


                someone=int(data["someone"])
                target_client=[client for client in CLIENTS if client.fileno() == someone]

                current_Talking_Client.clear()
                current_Talking_Client.append(target_client[0])


            else:
                print("else")
                check_client_state(target_client, clients_state, data, current_connected_client, current_Talking_Client[0])




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


