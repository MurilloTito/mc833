from scapy.all import IP, Ether, sniff, sendp, get_if_hwaddr, getmacbyip, TCP, UDP

IFACE_A = "eth0" # Rede A
IFACE_B = "eth1" # Rede B

MAC_A = get_if_hwaddr(IFACE_A)
MAC_B = get_if_hwaddr(IFACE_B)

# Cache de MAC para não travar o roteador com requisições ARP lentas
cache_mac = {}

def forward_packet(pkt):
    # 1. Verificações básicas
    if not pkt.haslayer(IP) or not pkt.haslayer(Ether):
        return

    # 2. Evitar loops
    if pkt[Ether].src in [MAC_A, MAC_B]:
        return

    # 3. Determinar interface de saída
    dst_ip = pkt[IP].dst

    if dst_ip.startswith("10.0.1."):
        out_iface = IFACE_A
        mac_origem = MAC_A

    elif dst_ip.startswith("10.0.2."):
        out_iface = IFACE_B
        mac_origem = MAC_B

    else:
        return

    mac_destino = cache_mac.get(dst_ip) or getmacbyip(dst_ip)

    if not mac_destino:
        return

    cache_mac[dst_ip] = mac_destino

    if pkt.haslayer(TCP):

        flags = str(pkt[TCP].flags)

        if flags in ['', 'F', 'FPU']:
            print(
                f"[DROP] TCP {pkt[IP].src} -> {pkt[IP].dst} "
                f"Flags maliciosas detectadas: {flags}"
            )
            return

        else:
            print(
                f"[OK] TCP {pkt[IP].src} -> {pkt[IP].dst} "
                f"Flags: {flags}"
            )

    pkt[Ether].src = mac_origem
    pkt[Ether].dst = mac_destino

    pkt[IP].ttl -= 1

    del pkt[IP].chksum

    if pkt.haslayer(TCP):
        del pkt[TCP].chksum

    elif pkt.haslayer(UDP):
        del pkt[UDP].chksum

    print(
        f"Encaminhando {pkt[IP].src} -> {pkt[IP].dst} via {out_iface}"
    )

    sendp(pkt, iface=out_iface, verbose=False)


print("Roteador Scapy Ativo (L2 Mode)...")

sniff(
    iface=[IFACE_A, IFACE_B],
    prn=forward_packet,
    store=0
)