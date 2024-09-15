import json
import socket
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ttk

Server = socket.gethostbyname(socket.gethostname())

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
try:
    clientsocket.connect((Server, 8080))
    connected = True
except ConnectionRefusedError as E:
    print(E)
    connected = False

No_Of_Messages = 0
offline_messages = {}
chat_history = {}  # Global list to store chat history
talking_client = None





# Bind the closing event

def update_offline_messages(data):
    global No_Of_Messages
    if data == "label":
        No_Of_Messages += 1
        label_no_message.configure(text=f"Number of messages you have {No_Of_Messages}")
    else:
        No_Of_Messages+=1

def recv_chat_insertion(data):
    text.configure(state="normal")
    text.insert(tk.END, f"{data}\n", "recv")
    text.configure(state="disabled")

def send_chat_insertion(data):
    text.configure(state="normal")
    text.insert(tk.END, f"{data}\n", "sent")
    text.configure(state="disabled")

def handle_received_in_open_window(data):
    Formatted_Message = data.split(":")[0]
    text.after(0, recv_chat_insertion, Formatted_Message)
    update_chat_history(Formatted_Message, "recv")

def handle_received_in_closed_window(data):
    global talking_client
    Formatted_Message = data.split(":")[0]
    offlineclient = int(data.split(":")[1])
    if offlineclient not in offline_messages:
        offline_messages[offlineclient] = []
    offline_messages[offlineclient].append(Formatted_Message)
    talking_client=int(offlineclient)
    update_chat_history(Formatted_Message,"recv")
    label_no_message.after(0, update_offline_messages, "label")


def remove_clients_history_chat_and_offline_messages(data):
    pass



temp = set()


def users_to_talk_to(state,data):
    global temp
    messages = data.strip().split("\n")

    if state=="add":
        for i in messages:
            if i:
                value = i.split(":")[1]
                offline_messages[value] = {}
                temp.add(value)
        combo.configure(values=list(temp))
    else:

        removed_client=data.split(":")[1]

        temp.remove((removed_client))

        combo.configure(values=list(temp))






def handle_opened_for_onother_person_message(data):
    Formatted_Message = data.split(":")[0]
    offlineclient = int(data.split(":")[1])
    if offlineclient not in offline_messages:
        offline_messages[offlineclient] = []
    offline_messages[offlineclient].append(Formatted_Message)
    print(offline_messages)
    label_no_message.after(0, update_offline_messages, "openedforother")







def recv():
    global No_Of_Messages, offline_messages, talking_client, chat_history
    while True:
        try:
            data = clientsocket.recv(1024).decode()
            print(data)
            if data.endswith(":opened"):
                handle_received_in_open_window(data)
                continue
            if data.endswith(":closed"):
                handle_received_in_closed_window(data)
            if data.startswith("combo:"):
                users_to_talk_to("add",data)

            if data.endswith(":closedto"):
                handle_opened_for_onother_person_message(data)

            if data.startswith("abort"):
                users_to_talk_to("remove",data)
                remove_clients_history_chat_and_offline_messages(data)



        except Exception as E:
            break
    clientsocket.close()

initiate = False

def update_chat_history(data, message_type):
    global chat_history
    if message_type == "recv":
        if talking_client not in chat_history:
            chat_history[talking_client] = []
        chat_history[talking_client].append({"recv": data})
    if message_type == "sent":
        if talking_client not in chat_history:
            chat_history[talking_client] = []
        chat_history[talking_client].append({"sent": data})
    print(chat_history)

def sendata():
    global chat_history, talking_client
    if initiate:
        x = entry.get()
        clientsocket.send(x.encode("utf-8"))
        send_chat_insertion(x)
        update_chat_history(x, "sent")
    else:
        messagebox.showerror(message="please select someone to talk to")

def calculate_remaining_missed_messages(client):
    global No_Of_Messages
    message_list = []
    for length in offline_messages[client]:
        message_list.append(length)
    total_offline_messages_of_current_client = len(message_list)
    return No_Of_Messages - total_offline_messages_of_current_client

# def Load_Offlinemessages(client):
#     if client == None:
#         return
#     if client in offline_messages:
#         text.configure(state="normal")
#         for message in offline_messages[client]:
#             text.insert(tk.END, f"{message}\n", "recv")
#             chat_history
#         text.configure(state="disabled")
#
#
#
#         del offline_messages[client]

def load_chat_history(client):
    global No_Of_Messages

    if client == None:
        return
    text.configure(state="normal")
    if client in chat_history:
        for message in chat_history[client]:
            for key, value in message.items():
                if key == "recv":
                    text.insert(tk.END, f"{value}\n", "recv")
                if key == "sent":
                    text.insert(tk.END, f"{value}\n", "sent")
    text.configure(state="disabled")
    No_Of_Messages = calculate_remaining_missed_messages(client)
    del offline_messages[talking_client]


def ChoosedOne():
    global initiate, talking_client
    offlineclient = None
    data = combo.get()
    talking_client = int(data)
    someone = {"someone": data}
    someone = json.dumps(someone)
    if len(data) < 1:
        messagebox.showerror(message="Enter Some Thing To Send")
        return
    try:
        clientsocket.send(someone.encode("utf-8"))
        initiate = True
        if chat_history:
            for i in chat_history:
                if int(i) == talking_client:
                    talking_client = int(i)
                    break
        if offline_messages:
            for fileno in offline_messages:
                if int(fileno) == talking_client:
                    offlineclient = int(fileno)
                    break
        users.withdraw()
        new_window(talking_client, offlineclient)
    except OSError as E:
        print(E)
    initiate = True

def Window_State(*state):
    print(state)
    if "opened" in state:
         clientsocket.send(f"{state[0]}:{state[1]}".encode("utf-8"))
         return
    data=state[0]
    clientsocket.send(data.encode("utf-8"))

def back_to_main():
    global No_Of_Messages
    Window_State("closed")
    chat.withdraw()  # Close the current root (chat window)
    users.deiconify()  # Show the root1 window again
    label_no_message.configure(text=f"Number of messages you have {No_Of_Messages}")

def new_window(talkingclient=None, message=None):
    global text, entry, chat
    chat = tk.Toplevel()
    label = ttk.CTkButton(chat, text="Back", command=back_to_main)  # Changed to CTkButton
    label.pack(side="top", anchor="w")
    chat.geometry("500x500")
    chat.attributes("-topmost", True)
    chat.title("ChatApp")
    text = tk.Text(chat, wrap="word", state="disabled")
    text.pack(fill="both", expand=True)
    text.tag_configure("sent", justify="right")
    text.tag_configure("recv", justify="left", foreground="blue")
    text.tag_configure("server", justify="center", foreground="red")
    entry = ttk.CTkEntry(chat)  # Changed to CTkEntry
    entry.pack(side=tk.LEFT, fill="both", padx=10, pady=10, expand=True)
    button = ttk.CTkButton(chat, text="Send", command=sendata)  # Changed to CTkButton
    button.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10, expand=True)
    Window_State("opened",talking_client)

    load_chat_history(talkingclient)


users = tk.Tk()
users.geometry("500x500")
users.attributes("-topmost", True)
users.title("user")
frame = ttk.CTkFrame(users)  # Changed to CTkFrame
label = ttk.CTkLabel(frame, text="Choose someone to talk to")  # Changed to CTkLabel
label.pack(side="left")
combo = ttk.CTkComboBox(frame)
combo.pack(side="left")
combo.set("Choose")
button = ttk.CTkButton(frame, text="Talk", fg_color='#700000', cursor="hand2", command=ChoosedOne,
                       hover_color='#911616', text_color="white").pack(side=tk.LEFT, padx=10, pady=10)
frame.pack(fill="both", expand=True, padx=10)
label_no_message = ttk.CTkLabel(users, text=f"Number of messages you have {No_Of_Messages}")  # Changed to CTkLabel
label_no_message.pack(side="bottom")
thread1 = threading.Thread(target=recv, daemon=True)
if connected:
    thread1.start()
Window_State("closed")

users.mainloop()
