import socket, threading, pygame

# pygame.init()
# pygame.display.set_mode((800, 1200))
username = input("Enter your username: ")

SERVER_IP = "127.0.0.1"
PORT = 1234

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
client.send(username.encode())

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            print(f"{message}")
        except: break
    
def send():
    while True:
        message = input()
        client.send(message.encode())

threading.Thread(target=receive, daemon=True).start()
threading.Thread(target=send, daemon=True).start()


while True: pass


