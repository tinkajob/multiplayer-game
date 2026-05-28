import json

def load_json(path):
    with open(path) as file:
        return json.load(file)
    
def receive_packet(client, buffer):
    while "\n" not in buffer:
        data = client.recv(4096).decode()
        if not data: return {}

        buffer += data
    
    message, buffer = buffer.split("\n", 1)
    return json.loads(message), buffer