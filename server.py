import socket, threading, json, time, random, pygame

HOST = "0.0.0.0"
PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
clock = pygame.time.Clock()
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
HEIGHT = 1000
PLAYER_SIZE = 50
SPEED = 10
BOMB_SIZE = 20
BOMB_POS = (WIDTH / 2 - BOMB_SIZE / 2, HEIGHT / 2 - BOMB_SIZE / 2)

def make_player(player_id, username):
    return {
        "x": 100 * int(player_id),
        "y": 100,
        "size": 50,
        "color": colors[(int(player_id) - 1) % len(colors)],
        "username": username,
        "has_bomb": False
    }

bomb = {
    "x": BOMB_POS[0],
    "y": BOMB_POS[1],
    "color": (0, 0, 0),
    "r": BOMB_SIZE,
    "timer": 0, 
    "explode_time": random.uniform(5, 20),
    "holder": None, 
    "vel_x": 0,
    "vel_y": 0,
    "pickup_cooldown": 2 # In s
}

def handle_client(client):
    global clients, inputs, colors

    username = client.recv(1024).decode()
    player_id = str(len(clients) + 1)

    clients[player_id] = make_player(player_id=player_id, username=username)

    inputs[player_id] = {
        "w": False,
        "s": False,
        "a": False,
        "d": False,
        "space": False,
        "mouse_x": 0, 
        "mouse_y": 0,
        "mouse_pressed": False
    }

    client.send((json.dumps({"type": "id", "id": player_id, "width": WIDTH, "height": HEIGHT}) + "\n").encode())
    print(f"{username} connected ({player_id})")

    try:
        buffer = ""
        while True:
            data = client.recv(1024).decode()

            if not data: break
            buffer += data

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                if message: inputs[player_id] = json.loads(message)
    except: pass
    
    del clients[player_id]
    del inputs[player_id]
    client.close()
    print(f"{username} disconnected")
    
def game_loop():
    while True:
        delta_time = clock.tick(60) / 1000.0
        for player_id in list(clients):
            # Get button presses
            pressed_UP = inputs[player_id]["w"]
            pressed_DOWN = inputs[player_id]["s"]
            pressed_LEFT = inputs[player_id]["a"]
            pressed_RIGHT = inputs[player_id]["d"]

            player = clients[player_id]

            # Normalize player movement (diagonal) and clamp to prevent going off-screen
            player_vel_x = (pressed_RIGHT - pressed_LEFT) / abs(1 + 0.41 * abs(pressed_DOWN - pressed_UP)) * SPEED
            player_vel_y = (pressed_DOWN - pressed_UP) / abs(1 + 0.41 * abs(pressed_RIGHT - pressed_LEFT)) * SPEED
            
            player["x"] = max(0, min(WIDTH - PLAYER_SIZE, player["x"] + player_vel_x))
            player["y"] = max(0, min(HEIGHT - PLAYER_SIZE, player["y"] + player_vel_y))

            px, py = player["x"], player["y"]
            
            if bomb["holder"] is None:
                bx, by = bomb["x"], bomb["y"]
                dist_sq = (px + PLAYER_SIZE / 2 - bx) ** 2 + (py + PLAYER_SIZE / 2 - by) ** 2
                if dist_sq <= (bomb["r"] * 1.5) ** 2 and bomb["pickup_cooldown"] <= 0:
                    bomb["holder"] = player_id
                    bomb["vel_x"] = 0
                    bomb["vel_y"] = 0

            if bomb["holder"] == player_id:
                bomb["x"] = px + PLAYER_SIZE / 2
                bomb["y"] = py + PLAYER_SIZE / 2

                if inputs[player_id]["mouse_pressed"]:
                    # Naredi da ti ustreli v smeri miske (space nej bo kasn dash), in vec cajta ku drzis bol mocno vrzes (da chargas shot)
                    bomb["holder"] = None
                    bomb["vel_x"] = player_vel_x * 2
                    bomb["vel_y"] = player_vel_y * 2
                    bomb["x"] += bomb["vel_x"]
                    bomb["y"] += bomb["vel_y"]
                    bomb["pickup_cooldown"] = 0.5
        
        # UPDATE BOMB
        if bomb["x"] + bomb["r"] > WIDTH or bomb["x"] - bomb["r"] < 0: bomb["vel_x"] *= (-1)
        if bomb["y"] + bomb["r"] > HEIGHT or bomb["y"] - bomb["r"] < 0: bomb["vel_y"] *= (-1)
        bomb["vel_x"] *= 0.99
        bomb["vel_y"] *= 0.99
        bomb["x"] += bomb["vel_x"]
        bomb["y"] += bomb["vel_y"]
        bomb["pickup_cooldown"] = bomb["pickup_cooldown"] - delta_time if bomb["pickup_cooldown"] > 0 else 0

        state = (json.dumps({"type": "state", "players": clients, "bomb": bomb}) + "\n").encode()
        
        dead_clients = []
        for c in connected_clients:
            try: c.send(state)
            except: dead_clients.append(c)
        
        # Delete disconnected clients
        for dc in dead_clients:
            connected_clients.remove(dc)

        # time.sleep(1/60)

connected_clients = []
threading.Thread(target=game_loop, daemon=True).start()

while True:
    client, addr = server.accept()
    connected_clients.append(client)
    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()