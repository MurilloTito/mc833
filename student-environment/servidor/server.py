import socket
import time
from rich import print
from utils import build_udp_packet, unpack_iph, unpack_udp, unpack_data

def send_catalog(sender, src_ip: str, src_port: int, client_ip: str, client_port: int):
    """
    Envia uma mensagem de catálogo para o cliente.
    """
    msg = "Catálogo: big_buck_bunny.ts, moon_video.ts, speech_video.ts"
    
    try:
        # Converter para bytes se necessário
        if isinstance(msg, str):
            msg = msg.encode()
        
        udp_packet = build_udp_packet(src_ip, client_ip, src_port, client_port, msg)
        sender.sendto(udp_packet, (client_ip, 0))
    except Exception as e:
        print(f"[!] Erro ao enviar catálogo: {e}")

def start_server(interface, src_ip, buffer_size, src_port, dst_port):
    """
    Loop principal do servidor que escuta pacotes brutos e processa comandos.
    """
    # Socket para ENVIAR (Raw IP)
    sender = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    sender.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Socket para ESCUTAR (Sniffer na interface)
    sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    sniffer.bind((interface, 0))

    print(f"[+] Servidor rodando em {src_ip}:{src_port} na interface {interface}")

    try:
        while True:
            # Recebe o pacote bruto da rede
            raw_packet, _ = sniffer.recvfrom(buffer_size)

            # Processar cabeçalho IP
            ip_header = unpack_iph(raw_packet)
            if not ip_header or ip_header[6] != 17:
                continue

            client_ip = socket.inet_ntoa(ip_header[8])

            # Processar cabeçalho UDP
            udp_header = unpack_udp(raw_packet)
            if udp_header[1] != src_port:
                continue

            # Extrair dados (uma única vez)
            packet_data = unpack_data(raw_packet)
            command = packet_data.decode(errors='ignore').strip()

            # Processar comandos
            if command == 'catalog':
                send_catalog(sender, src_ip, src_port, client_ip, udp_header[0])
                print(f"[+] Enviado catálogo para {client_ip}:{udp_header[0]}")
            
            elif command.startswith('stream'):
                video_name = command[7:].strip()  # Remove 'stream ' e espaços
                print(f"[+] Pedido de streaming para: {video_name}")
                start_streaming(sender, src_ip, src_port, client_ip, udp_header[0], video_name)

    except KeyboardInterrupt:
        print("\n[!] Desligando servidor...")
    finally:
        sender.close()
        sniffer.close()

def start_streaming(sender, src_ip, src_port, client_ip, client_port, video_name):
    """
    Função para iniciar o streaming de um vídeo para o cliente.
    """
    print(f"[+] Iniciando streaming do vídeo '{video_name}' para {client_ip}:{client_port}")
    
    try:
        with open(f"videos/{video_name}", "rb") as video_file:
            chunk_size = 512
            
            while True:
                chunk = video_file.read(chunk_size)
                
                if not chunk:
                    print(f"[+] Streaming do vídeo '{video_name}' finalizado")
                    # Envia marcador de fim de stream
                    end_marker = b"__STREAM_END__"
                    udp_packet = build_udp_packet(src_ip, client_ip, src_port, client_port, end_marker)
                    sender.sendto(udp_packet, (client_ip, 0))
                    break
                
                udp_packet = build_udp_packet(src_ip, client_ip, src_port, client_port, chunk)
                sender.sendto(udp_packet, (client_ip, 0))
                time.sleep(0.1)
                
    except FileNotFoundError:
        error_msg = f"Erro: Vídeo '{video_name}' não encontrado".encode()
        print(f"[!] Vídeo não encontrado: {video_name}")
        udp_packet = build_udp_packet(src_ip, client_ip, src_port, client_port, error_msg)
        sender.sendto(udp_packet, (client_ip, 0))
        # Envia também o marcador de fim para sinalizar término
        end_marker = b"__STREAM_END__"
        udp_packet = build_udp_packet(src_ip, client_ip, src_port, client_port, end_marker)
        sender.sendto(udp_packet, (client_ip, 0))
    except Exception as e:
        print(f"[!] Erro ao fazer streaming: {e}")
    

if __name__ == "__main__":
    # Parâmetros: interface, ip_do_servidor, buffer, porta_servidor, porta_cliente
    start_server("eth0", "172.20.0.2", 65535, 9999, 12345)
