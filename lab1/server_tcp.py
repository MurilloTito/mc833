import socket
import threading

# Função para lidar com a comunicação com um cliente
def handle_client(client_socket, clients):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Mensagem recebida: {message}")
                broadcast(message, clients, client_socket)
            else:
                break
        except:
            break

    client_socket.close()

# Função para retransmitir mensagens para todos os clientes
def broadcast(message, clients, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(message.encode('utf-8'))

# Configuração do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(5)
print("Servidor escutando na porta 12345...")

clients = []

while True:
    client_socket, addr = server.accept()
    print(f"Conexão aceita de {addr}")
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket, clients)).start()