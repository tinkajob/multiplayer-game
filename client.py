import socket, threading, pygame, json

# pygame.init()
# pygame.display.set_mode((800, 1200))
username = input("Enter your username: ")

SERVER_IP = "127.0.0.1"
PORT = 1234

pygame.init()
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH,  HEIGHT))
pygame.display.set_caption("Multiplayer")

clock = pygame.time.Clock()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
# client.send(username.encode())

player_id = client.recv(1024).decode()
players = {}

inputs = {
    "w": False,
    "s": False,
    "a": False,
    "d": False,
}

def receive():
    global players
    while True:
        try:
            data = client.recv(1024).decode()
            if not data: break
            players = json.loads(data)
        except: break
    
threading.Thread(target=receive, daemon=True).start()

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    inputs["w"] = keys[pygame.K_w]
    inputs["s"] = keys[pygame.K_s]
    inputs["a"] = keys[pygame.K_a]
    inputs["d"] = keys[pygame.K_d]

 # Send inputs to server
    try:
        client.send(json.dumps(inputs).encode())
    except:
        break

    # Draw
    screen.fill((30, 30, 30))

    for pid, player in players.items():

        pygame.draw.rect(
            screen,
            player["color"],
            (
                player["x"],
                player["y"],
                50,
                50
            )
        )

        font = pygame.font.SysFont(None, 24)

        text = font.render(
            f"Player {pid}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            text,
            (player["x"], player["y"] - 20)
        )

    pygame.display.flip()

pygame.quit()
client.close()