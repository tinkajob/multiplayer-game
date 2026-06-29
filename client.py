import socket, threading, pygame, json
from utils.utils import receive_packet
pygame.init()

username = input("Enter your usename: ")#"tinkajob"

# ========== NETWORKING ==========
SERVER_IP = "127.0.0.1"
PORT = 1234
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
client.send(username.encode())

clock = pygame.time.Clock()
players = {}
bomb = {"x": 0, "y": 0, "r": 20, "color": (0, 0, 0)}
inputs = {
    "w": False,
    "s": False,
    "a": False,
    "d": False,
}

packet, buffer = receive_packet(client, buffer="")
player_id = packet["id"]
WIDTH = packet["width"]
HEIGHT = packet["height"]

screen = pygame.display.set_mode((WIDTH,  HEIGHT))
pygame.display.set_caption("Pass the Bomb!")

font = pygame.font.SysFont("", 24)
username_surfaces = {}

def receive():
    global players, font, username_surfaces, bomb
    buffer = ""

    while True:
        try:
            packet, buffer = receive_packet(client, buffer)
            
            if packet is None: break

            if packet["type"] == "state":
                players = packet["players"]
                bomb = packet["bomb"]
                for pid, player in players.items():
                    if pid not in username_surfaces:
                        username_surfaces[pid] = font.render(player["username"], True, (255, 255, 255))

        except Exception as e:
            print("Receive error:", e)
            break
    
threading.Thread(target=receive, daemon=True).start()

running = True
while running:
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
    inputs["space"] = keys[pygame.K_SPACE]
    inputs["mouse_x"] = pygame.mouse.get_pos()[0]
    inputs["mouse_y"] = pygame.mouse.get_pos()[1]
    inputs["mouse_pressed"] = pygame.mouse.get_pressed()[0]

    try:
        client.send((json.dumps(inputs) + "\n").encode())
    except:
        break

    # Draw scene
    pygame.display.flip()
    screen.fill((30, 30, 30))

    for player_id, player in players.items():
        pygame.draw.rect(screen, player["color"], (player["x"], player["y"], player["size"], player["size"]), border_radius=10)
        username_size = username_surfaces[player_id].get_size()
        screen.blit(username_surfaces[player_id], (player["x"] + (player["size"] / 2) - (username_size[0] / 2), player["y"] - 20))
    pygame.draw.circle(screen, bomb["color"], (bomb["x"], bomb["y"]), bomb["r"])

pygame.quit()
client.close()