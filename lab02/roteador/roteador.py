from scapy.all import *

def analisar_pacote(pacote):
    print(f"Pacote recebido: {pacote}")

    correct_client_IP = "10.0.2.2"

    if IP in pacote:
        ip_src = pacote[IP].src
        ip_dst = pacote[IP].dst

        if ip_src == correct_client_IP:
            print(f"Pacote de {ip_src} para {ip_dst} é permitido.")
        else:
            print(f"Pacote de {ip_src} para {ip_dst} é bloqueado.")
    else:
        print("Pacote não contém camada IP.")

if __name__ == "__main__":
    sniff(count=5, prn=analisar_pacote)

