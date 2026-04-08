import os
import socket
import subprocess
from rich import print
from rich.markdown import Markdown
from utils import unpack_iph, unpack_udp, unpack_data, build_udp_packet

# Porta onde o cliente espera receber a resposta
REC_PORT = 12345

def start_client():
    """
    Inicia o cliente de streaming utilizando Raw Sockets.
    Você deve garantir que as funções de unpack e build_packet estejam prontas.
    """
    sender = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    sender.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    sniffer.bind(("eth0", 0))

    dest_ip = "172.20.0.2" # IP do Servidor alterado para bater com o do Dockerfile

    print(Markdown("""# Aplicação de Streaming (Client-Side)
    - Digite **catalog** para listar vídeos.
    - Digite **stream <nome_do_video>** para assistir.
    - Digite **q** para sair.
    """))
    print("-" * 25)

    try:
        while True:            
            msg = input("\nVocê (Cliente) > ")
            if msg == 'q': break

            packet = build_udp_packet(
                src_ip="172.21.0.2", 
                dest_ip=dest_ip,
                src_port=REC_PORT,
                dest_port=9999,
                data=msg
            )

            sender.sendto(packet, (dest_ip, 0))
            print("[-] Pacote enviado. Aguardando resposta do servidor...")
            if msg.startswith('stream '):
                video_name = msg.split(' ', 1)[1].strip()
                os.makedirs('downloads', exist_ok=True)
                out_path = os.path.join('downloads', video_name)
                with open(out_path, 'wb') as out_file:
                    print(f"[-] Recebendo stream para {out_path} ...")
                    recv_count = 0
                    while True:
                        raw_packet, _ = sniffer.recvfrom(65535)

                        if len(raw_packet) < 28:
                            continue

                        header_ip = unpack_iph(raw_packet)
                        if header_ip[6] != 17:
                            continue

                        header_udp = unpack_udp(raw_packet)
                        if header_udp[1] != REC_PORT:
                            continue

                        data = unpack_data(raw_packet)
                        if not data:
                            continue

                        recv_count += 1
                        if recv_count % 10 == 0:
                            print(f"[<] Recebidos {recv_count} pacotes (último {len(data)} bytes)")

                        if data == b'__STREAM_END__':
                            print('[+] Stream finalizado pelo servidor')
                            break

                        if data.startswith(b'Erro:'):
                            print('> Resposta do Servidor: ' + data.decode('utf-8', errors='ignore'))
                            break

                        out_file.write(data)
                        out_file.flush()
                        
                print(f"[+] Stream finalizado.")
                print(f"[+] Vídeo salvo em: {out_path}")
                print("[+] Copie o arquivo para o host e rode com mpv localmente.")

            else:
                while True:
                    raw_packet, _ = sniffer.recvfrom(65535)

                    if len(raw_packet) < 28:
                        continue

                    header_ip = unpack_iph(raw_packet)

                    flags_offset = header_ip[4]

                    if flags_offset & 0x1FFF != 0:
                        continue

                    if header_ip[6] != 17:
                        continue

                    header_udp = unpack_udp(raw_packet)
                    src_ip = socket.inet_ntoa(header_ip[8])

                    if src_ip != dest_ip:
                        continue

                    if header_udp[1] != REC_PORT:
                        continue

                    extract_data = unpack_data(raw_packet)
                    if extract_data:
                        print(f'> Resposta do Servidor: {extract_data.decode("utf-8", errors="ignore")}')
                    break

    except KeyboardInterrupt:
        print("\n[!] Encerrando cliente...")
    finally:
        sender.close()
        sniffer.close()

if __name__ == "__main__":
    start_client()
