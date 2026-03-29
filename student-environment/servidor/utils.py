import struct
import socket

# Formatos para auxiliar o struct.unpack e struct.pack
# IP_FORMAT: 20 bytes, seguindo a ordem do cabeçalho IPv4
IP_FORMAT = "!BBHHHBBH4s4s"   
# UDP_FORMAT: 8 bytes (Source Port, Dest Port, Length, Checksum)
UDP_FORMAT = "!HHHH"          

def unpack_iph(pkg: bytes):
    """
    Realiza o unpack do header IP (os primeiros 20 bytes do pacote).

    Instruções:
    1. Utilize a constante IP_FORMAT com struct.unpack.
    2. O header IP começa no índice 0 e vai até o 20.
    3. Retorne a tupla com os campos desempacotados.
    """
    # Detecta se o pacote inclui um cabeçalho Ethernet (EtherType 0x0800)
    offset = 14 if len(pkg) >= 34 and pkg[12:14] == b'\x08\x00' else 0
    return struct.unpack(IP_FORMAT, pkg[offset:offset+20])

def unpack_udp(pkg: bytes):
    """
    Realiza o unpack do header UDP.

    Instruções:
    1. O header UDP começa logo após o header IP (índice 20) e tem 8 bytes de tamanho.
    2. Utilize a constante UDP_FORMAT.
    3. Retorne a tupla com (src_port, dest_port, length, checksum).
    """
    offset = 14 if len(pkg) >= 34 and pkg[12:14] == b'\x08\x00' else 0
    return struct.unpack(UDP_FORMAT, pkg[offset+20:offset+28])

def unpack_data(pkg: bytes):
    """
    Extrai o payload (dados) do pacote.

    Instruções:
    1. O payload começa após o header IP (20 bytes) e o header UDP (8 bytes).
    2. Retorne apenas os bytes correspondentes aos dados.
    """
    offset = 14 if len(pkg) >= 34 and pkg[12:14] == b'\x08\x00' else 0
    if len(pkg) > offset + 28:
        return pkg[offset+28:]
    return b''

def calculate_checksum(msg: bytes) -> int:
    """
    Calcula o Checksum de 16 bits para o cabeçalho.

    Instruções:
    1. Verifique se o tamanho da mensagem é ímpar; se for, adicione um byte nulo (b'\x00').
    2. Some os valores de 16 bits (2 bytes por vez).
    3. Realize o 'carry' (soma os bits que excederem 16 bits de volta ao total).
    4. Retorne o complemento de um da soma final, mascarado para 16 bits (0xffff).
    """
    if len(msg) % 2 == 1:
        msg += b'\x00'
    
    checksum = 0
    for i in range(0, len(msg), 2):
        word = (msg[i] << 8) + msg[i + 1]
        checksum += word
    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF

def build_udp_packet(src_ip: str, dest_ip: str, src_port: int, dest_port: int, data) -> bytes:
    """
    Constrói um pacote IP/UDP completo do zero.

    Passos necessários:
    1. Encode do payload para bytes.
    2. Construção do Pseudo-Header UDP (IP Origem, IP Destino, Zero, Protocolo 17, UDP Length).
    3. Cálculo do Checksum UDP (Pseudo-Header + Header UDP temporário + Payload).
    4. Construção do Header UDP final com o Checksum calculado.
    5. Construção do Header IP:
        - Definir campos como Versão/IHL (0x45), TTL (64), Protocolo (17).
        - Calcular o Checksum do Header IP.
    6. Concatenar Header IP + Header UDP + Payload e retornar os bytes.
    """
    
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = data
    
    pseudo_header = struct.pack('!4s4sBBH', socket.inet_aton(src_ip), socket.inet_aton(dest_ip), 0, 17, len(data_bytes) + 8)
    udp_header = struct.pack(UDP_FORMAT, src_port, dest_port, len(data_bytes) + 8, 0)
    checksum = calculate_checksum(pseudo_header + udp_header + data_bytes)
    udp_header = struct.pack(UDP_FORMAT, src_port, dest_port, len(data_bytes) + 8, checksum)

    flags_fragment = 0x4000  # Don't Fragment

    ip_header = struct.pack(
        IP_FORMAT,
        0x45,
        0,
        20 + 8 + len(data_bytes),
        0,
        flags_fragment,
        64,
        17,
        0,
        socket.inet_aton(src_ip),
        socket.inet_aton(dest_ip)
    )
    ip_checksum = calculate_checksum(ip_header)
    ip_header = struct.pack(IP_FORMAT, 0x45, 0, 20 + 8 + len(data_bytes), 0, 0, 64, 17, ip_checksum, socket.inet_aton(src_ip), socket.inet_aton(dest_ip))
    return ip_header + udp_header + data_bytes