import socket, threading, pygame, json

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

player_id = client.recv(1024).decode().strip()
players = {}

inputs = {
    "w": False,
    "s": False,
    "a": False,
    "d": False,
}

def receive():
    global players

    buffer = ""

    while True:
        try:
            data = client.recv(4096).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:

                message, buffer = buffer.split("\n", 1)

                if message:

                    # FIRST packet = player id
                    if message.isdigit():
                        print("My ID:", message)

                    # Everything else = game state
                    else:
                        players = json.loads(message)

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

    keys = pygame.key.get_pressed()
    inputs["w"] = keys[pygame.K_w]
    inputs["s"] = keys[pygame.K_s]
    inputs["a"] = keys[pygame.K_a]
    inputs["d"] = keys[pygame.K_d]

 # Send inputs to server
    try:
        client.send((json.dumps(inputs) + "\n").encode())
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