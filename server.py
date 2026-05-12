import socket, threading

HOST = "0.0.0.0"
PORT = 1234 # Idk just sth

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Server is running!")

clients = []


def handle_client(client, address):
    clients.append(client)
    username = client.recv(1024).decode()
    print(f"{username} connected")

    while True:
        try:
            data = client.recv(1024)
            if not data: break
            message = data.decode()
            print(f"{username}: {message}")

            for c in clients:
                if c != client: c.send(f"{username}: {message}".encode())

        except: break
    
    print(f"{username} disconnected")
    clients.remove(client)
    client.close()


while True:
    client, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client, addr))
    thread.start()


client.close()
server.close()