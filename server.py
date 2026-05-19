import socket, threading, json, time

HOST = "0.0.0.0"
PORT = 1234 # Idk just sth

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Server is running!")

clients = {}
inputs = {}

WIDTH = 800
HEIGHT = 600
PLAYER_SIZE = 50
SPEED = 10

def handle_client(client):
    global clients, inputs
    player_id = str(len(clients) + 1)

    clients[player_id] = {
        "x": 100 * int(player_id),
        "y": 100,
        "color": [50 * int(player_id), 255 - 50 * int(player_id), 100]
    }

    inputs[player_id] = {
        "w": False,
        "s": False,
        "a": False,
        "d": False
    }
    client.send((player_id + "\n").encode())
    print(f"Player {player_id} connected")

    try:
        buffer = ""

        while True:

            data = client.recv(1024).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:

                message, buffer = buffer.split("\n", 1)

                if message:
                    inputs[player_id] = json.loads(message)
    except: pass
    del clients[player_id]
    del inputs[player_id]
    client.close()
    print(f"{player_id} disconnected")
    

def game_loop():
    while True:
        for player_id in list(clients):
            if inputs[player_id]["w"]:
                clients[player_id]["y"] -= SPEED
            if inputs[player_id]["s"]:
                clients[player_id]["y"] += SPEED
            if inputs[player_id]["a"]:
                clients[player_id]["x"] -= SPEED
            if inputs[player_id]["d"]:
                clients[player_id]["x"] += SPEED
            
            clients[player_id]["x"] = max(0, min(WIDTH - PLAYER_SIZE, clients[player_id]["x"]))
            clients[player_id]["y"] = max(0, min(HEIGHT - PLAYER_SIZE, clients[player_id]["y"]))

        state = (json.dumps(clients) + "\n").encode()
        dead_clients = []
        for c in connected_clients:
            try: c.send(state)
            except: dead_clients.append(c)
        
        for dc in dead_clients:
            connected_clients.remove(dc)

        time.sleep(1/60)

connected_clients = []

threading.Thread(target=game_loop, daemon=True).start()

while True:
    client, addr = server.accept()
    connected_clients.append(client)
    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()


client.close()
server.close()