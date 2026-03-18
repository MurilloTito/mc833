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
    unpack_iph = struct.unpack(IP_FORMAT, pkg[0:20])
    return unpack_iph

def unpack_udp(pkg: bytes):
    """
    Realiza o unpack do header UDP.

    Instruções:
    1. O header UDP começa logo após o header IP (índice 20) e tem 8 bytes de tamanho.
    2. Utilize a constante UDP_FORMAT.
    3. Retorne a tupla com (src_port, dest_port, length, checksum).
    """
    unpack_udp = struct.unpack(UDP_FORMAT, pkg[20:28])
    return unpack_udp

def unpack_data(pkg: bytes):
    """
    Extrai o payload (dados) do pacote.

    Instruções:
    1. O payload começa após o header IP (20 bytes) e o header UDP (8 bytes).
    2. Retorne apenas os bytes correspondentes aos dados.
    """
    unpack_data = struct.unpack(pkg[28:], pkg)
    return unpack_data

def calculate_checksum(msg: bytes) -> int:
    """
    Calcula o Checksum de 16 bits para o cabeçalho.

    Instruções:
    1. Verifique se o tamanho da mensagem é ímpar; se for, adicione um byte nulo (b'\x00').
    2. Some os valores de 16 bits (2 bytes por vez).
    3. Realize o 'carry' (soma os bits que excederem 16 bits de volta ao total).
    4. Retorne o complemento de um da soma final, mascarado para 16 bits (0xffff).
    """
    pass

def build_udp_packet(src_ip: str, dest_ip: str, src_port: int, dest_port: int, data: str) -> bytes:
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
    pass