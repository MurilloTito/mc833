import socket

def servidor_udp():
    host = '127.0.0.1'  # Endereço IP do servidor
    porta = 12345       # Porta para escutar conexões

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor_socket.bind((host, porta))

    print(f"Servidor UDP aguardando mensagens em {host}:{porta}...")

    clientes = set()  # Conjunto para armazenar endereços dos clientes

    while True:
        mensagem, endereco = servidor_socket.recvfrom(1024)
        mensagem_decodificada = mensagem.decode('utf-8')

        if endereco not in clientes:
            clientes.add(endereco)

        print(f"Mensagem recebida de {endereco}: {mensagem_decodificada}")

        # Retransmitir a mensagem para todos os clientes
        for cliente in clientes:
            if cliente != endereco:  # Não enviar de volta para o remetente
                servidor_socket.sendto(mensagem, cliente)

if __name__ == "__main__":
    servidor_udp()