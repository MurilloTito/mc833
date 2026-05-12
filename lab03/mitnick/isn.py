from scapy.all import *


def probe_initial_seq():
    victim_addr = "10.0.2.20"
    rsh_port = 514

    print(f"[>] Sondando {victim_addr}:{rsh_port} para coletar o numero de sequencia inicial...")

    ip_hdr = IP(dst=victim_addr)
    tcp_hdr = TCP(sport=RandShort(), dport=rsh_port, flags="S", seq=1000)
    probe_pkt = ip_hdr / tcp_hdr

    reply = sr1(probe_pkt, timeout=2, verbose=0)

    if reply is None or not reply.haslayer(TCP):
        print("[!] Sem resposta do host alvo dentro do tempo limite.")
        return

    if reply[TCP].flags == "SA":
        initial_seq = reply[TCP].seq
        print(f"[+] Resposta obtida com sucesso!")
        print(f"    - ISN retornado: {initial_seq}")
        print(f"    - Atencao: sistemas atuais geram ISN de forma aleatoria.")
    else:
        print(f"[!] Resposta fora do esperado. Flags recebidas: {reply[TCP].flags}")


if __name__ == "__main__":
    probe_initial_seq()
