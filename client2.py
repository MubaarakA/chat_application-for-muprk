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

print("connecting")
print(clientsocket.fileno())


def recv():
    temp = []  # holds what user can chat with becouse user can choose 1 or more people

    while True:

        try:
            data = clientsocket.recv(1024).decode()
            if data.split(":")[0] == "server":
                text.configure(state="normal")
                text.insert(tk.END, f"{data}\n", "server")

                text.configure(state="disabled")

            if data.startswith("combo:"):
                print(data)

                messages = data.strip().split("\n")
                print(messages)
                for i in messages:
                    if i:
                        value = i.split(":")[1]

                        if value not in temp:
                            temp.append(value)
                            combo.configure(values=temp)

                            # i did this becouse when 2 clients are talking
                            # then some clients will be sent the same
                            #file no when onother client comes
                            #to aviod i will make sure that
                            #fileno doesnot exist in temp

                print(temp, "from")



            else:

                text.configure(state="normal")
                text.insert(tk.END, f"{data}\n", "recv")

                text.configure(state="disabled")

        except ConnectionResetError as E:
            print(E)
            label.configure(foreground="black")
            break
    clientsocket.close()


initate = False


def sendata():
    if initate:
        x = entry.get()
        clientsocket.send(x.encode("utf-8"))
        text.configure(state="normal")
        text.insert(tk.END, f"{x}\n", "sent")

        text.configure(state="disabled")
    else:
        messagebox.showerror(message="please select some one to talk to")


def ChoosedOne():
    global initate

    data = combo.get()
    someone = {"someone": data}
    someone = json.dumps(someone)
    try:
        clientsocket.send(someone.encode("utf-8"))
    except OSError as E:
        print(E)

    initate = True


root = tk.Tk()

root.geometry("500x500")
root.attributes("-topmost", True)
root.title("aaaaa")
frame = tk.Frame(root)

label = tk.Label(frame, text="chooseee some one to talk to")
label.pack(side="left")

combo = ttk.CTkComboBox(frame)

combo.pack(side="left")

combo.set("choose")
button = ttk.CTkButton(frame,
                       text="Talk",
                       command=ChoosedOne,
                       fg_color='#700000',  # Set foreground color
                       hover_color='#911616', text_color="white").pack(side=tk.LEFT, padx=10, pady=10)

frame.pack(side="top")
text = tk.Text(wrap="word", state="disabled")

text.pack(fill="both", expand=True)
text.tag_configure("sent", justify="right")
text.tag_configure("recv", justify="left", foreground="blue")
text.tag_configure("server", justify="center", foreground="red")

entry = tk.Entry()
entry.pack(side=tk.LEFT, fill="both", padx=10, pady=10, expand=True)
button = tk.Button(text="send", command=sendata).pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10, expand=True)

thread1 = threading.Thread(target=recv, daemon=True)
if connected:
    thread1.start()

root.mainloop()
