import socket

def cliente():
    host = '127.0.0.1'  # Endereço IP do servidor
    porta = 12345       # Porta do servidor

    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect((host, porta))

    print(f"Conectado ao servidor em {host}:{porta}")

    while True:
        mensagem_cliente = input("Cliente: ")
        cliente_socket.send(mensagem_cliente.encode('utf-8'))
        if mensagem_cliente.lower() == 'sair':
            print("Encerrando conexão com o servidor.")
            break
        mensagem_servidor = cliente_socket.recv(1024).decode('utf-8')
        if mensagem_servidor.lower() == 'sair':
            print("Servidor encerrou a conexão.")
            break
        print(f"Servidor: {mensagem_servidor}")

    cliente_socket.close()

if __name__ == "__main__":
    cliente()