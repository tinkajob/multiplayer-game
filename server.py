import socket, threading, json, time, random

HOST = "0.0.0.0"
PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Server is running!")

colors = [
    (255, 0, 0),       # red
    (0, 255, 0),       # green
    (0, 0, 255),       # blue
    (255, 255, 0),     # yellow
    (255, 165, 0),     # orange
    (128, 0, 128),     # purple
    (255, 105, 180),   # pink
    (0, 255, 255),     # cyan
    (255, 0, 255),     # magenta
    (139, 69, 19),     # brown
    (50, 205, 50),     # lime
    (135, 206, 235),   # sky blue
    (255, 215, 0),     # gold
    (192, 192, 192),   # silver
]

clients = {}
inputs = {}

WIDTH = 1600
HEIGHT = 1200
PLAYER_SIZE = 50
SPEED = 10
BOMB_POS = (780, 580)
BOMB_SIZE = 20

bomb = {
    "x": BOMB_POS[0],
    "y": BOMB_POS[1],
    "color": (0, 0, 0),
    "size": 40,
    "timer": 0, 
    "explode_time": random.uniform(5, 20),
    "holder": None
}

def handle_client(client):
    global clients, inputs, colors

    username = client.recv(1024).decode()
    player_id = str(len(clients) + 1)

    clients[player_id] = {
        "x": 100 * int(player_id),
        "y": 100,
        "size": 50,
        "color": colors[(int(player_id) - 1) % len(colors)],
        "username": username
    }

    inputs[player_id] = {
        "w": False,
        "s": False,
        "a": False,
        "d": False
    }
    
    client.send((json.dumps({"type": "id", "id": player_id}) + "\n").encode())
    print(f"{username} connected ({player_id})")

    try:
        buffer = ""
        while True:
            data = client.recv(1024).decode()

            if not data: break
            buffer += data

            while "\n" in buffer:

                message, buffer = buffer.split("\n", 1)
                if message:
                    inputs[player_id] = json.loads(message)
    except: pass
    
    del clients[player_id]
    del inputs[player_id]
    client.close()
    print(f"{username} disconnected")
    
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

        state = (json.dumps({"type": "state", "players": clients, "bomb": bomb}) + "\n").encode()
        
        dead_clients = []
        for c in connected_clients:
            try: c.send(state)
            except: dead_clients.append(c)
        
        # Delete disconnected clients
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