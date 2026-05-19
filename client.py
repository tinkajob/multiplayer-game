import socket, threading, pygame, json

username = input("Enter your usename: ")

# ========== NETWORKING ==========
SERVER_IP = "127.0.0.1"
PORT = 1234
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
client.send(username.encode())

WIDTH = 800
HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH,  HEIGHT))
pygame.display.set_caption("Pass the Bomb!")

clock = pygame.time.Clock()
player_id = None
players = {}
inputs = {
    "w": False,
    "s": False,
    "a": False,
    "d": False,
}

font = pygame.font.SysFont(None, 24)
username_surfaces = {}

def receive():
    global players, player_id, font, username_surfaces
    buffer = ""

    while True:
        try:
            data = client.recv(4096).decode()

            if not data: break
            buffer += data

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                packet = json.loads(message)
                if packet["type"] == "id":
                    player_id = packet["id"]
                    print("My ID:", player_id)

                elif packet["type"] == "state":
                    players = packet["players"]
                    for pid, player in players.items():
                        if pid not in username_surfaces:
                            username_surfaces[pid] = font.render(player["username"], True, (255, 255, 255))

        except Exception as e:
            print("Receive error:", e)
            break
    
threading.Thread(target=receive, daemon=True).start()

while running := True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    keys = pygame.key.get_pressed()
    inputs["w"] = keys[pygame.K_w]
    inputs["s"] = keys[pygame.K_s]
    inputs["a"] = keys[pygame.K_a]
    inputs["d"] = keys[pygame.K_d]

    try:
        client.send((json.dumps(inputs) + "\n").encode())
    except:
        break

    # Draw
    screen.fill((30, 30, 30))

    for player_id, player in players.items():
        pygame.draw.rect(screen, player["color"], (player["x"], player["y"], 50, 50), border_radius=10)
        screen.blit(username_surfaces[player_id], (player["x"], player["y"] - 20))

    pygame.display.flip()

pygame.quit()
client.close()