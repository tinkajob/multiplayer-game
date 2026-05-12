import socket

HOST = "0.0.0.0"
PORT = 1234 # Idk just sth

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

client, addr = server.accept()


  


client.close()
server.close()