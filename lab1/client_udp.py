import socket
import threading

def receber_mensagens(cliente_socket):
    while True:
        try:
            mensagem, _ = cliente_socket.recvfrom(1024)
            print(f"\nMensagem recebida: {mensagem.decode('utf-8')}")
        except:
            break

def cliente_udp():
    host = '127.0.0.1'  # Endereço IP do servidor
    porta = 12345       # Porta do servidor

    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    nome = input("Digite seu nome: ")
    print(f"Conectado ao servidor UDP em {host}:{porta}")

    # Thread para receber mensagens do servidor
    threading.Thread(target=receber_mensagens, args=(cliente_socket,), daemon=True).start()

    while True:
        mensagem = input(f"{nome}: ")
        if mensagem.lower() == 'sair':
            print("Encerrando conexão.")
            break
        mensagem_completa = f"{nome}: {mensagem}"
        cliente_socket.sendto(mensagem_completa.encode('utf-8'), (host, porta))

    cliente_socket.close()

if __name__ == "__main__":
    cliente_udp()