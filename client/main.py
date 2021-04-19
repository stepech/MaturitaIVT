import socket
import os
from datetime import datetime

DEBUG = False

"""
###################################
###FUNKCE PRO PŘÍPRAVU PROSTŘEDÍ###
###################################
"""


def init():
    """Naběhne při spuštění"""
    print("Spouštím klienta")
    print("Zadejte číslo požadovaného módu:\n1 - TCP\n2 - UDP")
    mode: int = int(input("> "))
    if mode == 1:
        tcp_start()
    elif mode == 2:
        udp_start()
    else:
        print("Zadejte pouze číslo 1 nebo 2")


def get_ip_port():
    """často používaná metoda, získá od uživatele ip adresu a číslo portu"""
    if not DEBUG:
        print("Zadejte IP adresu serveru")
        server_ip: str = input("> ")
        print("Zadejte číslo portu na který se server naváže\nVýchozí port = 3310")
        port: str = input("> ")
        print(port)
        if port == "":
            port = "3310"
        port: int = int(port)
        return server_ip, port
    else:
        return "127.0.0.1", 3310


def udp_start():
    """Inicializuje UDP připojení. Provede kontrolní výměnu balíčků jako zkoušku"""
    ip, port = get_ip_port()
    payload = "VERIFY".encode('utf-8')
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.sendto(payload, (ip, port))
    data = client_sock.recv(1024)
    if data == "CONFVER".encode('utf-8'):
        print("Spojení navázáno!")
    if do_big():
        start1(client_sock, True, (ip, port))
    else:
        start2(client_sock, True, (ip, port))



def tcp_start():
    """Inicializuje TCP připojení."""
    ip, port = get_ip_port()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((ip, port))
    if do_big():
        start1(client_sock)
    else:
        start2(client_sock)


def do_big():
    """Zeptá se na formu testu, který bude probíhat"""
    question = "Vyberte testovací mód:" \
               "\n1 - Množství velkých souborů" \
               "\n2 - Množství malých souborů"
    print(question)
    choice = int(input("> "))
    if choice == 1:
        print("Spouštím odesílání velkých souborů")
        return True
    elif choice == 2:
        print("Spouštím odesílání malých souborů")
        return False
    else:
        pass


"""
##########################
###HLAVNÍ ČÁST PROGRAMU###
##########################
"""


def start1(client_soc: socket.socket, udp: bool = False, address=None):
    """Funkce pro odeslání 9999 souborů o celkové velikosti 10 MB"""

    for file in os.listdir("cache"):
        os.remove(os.path.join("cache", file))

    # Vytvoření 30 souborů v /client/cache/
    for i in range(9999):
        name = "cache/test{0}.txt"
        print("Zapisuji", i + 1)
        if i < 10:
            fill = str(i) * int(2 ** 10)
            name = name.format("000" + str(i))
        elif i < 100:
            fill = str(i) * int(2 ** 10 / 2)
            name = name.format("00" + str(i))
        elif i < 1000:
            fill = str(i) * int(2 ** 10 / 3)
            name = name.format("0" + str(i))
        else:
            fill = str(i) * int(2 ** 10 / 4)
            name = name.format(str(i))
        with open(name, 'w') as file:
            file.write(fill)

    print("Zahajuji odesílání")
    i = 0
    e = 0
    m = 0
    if udp:
        client_soc.settimeout(2.0)
    start_time = datetime.now()
    for file in os.listdir("cache"):
        f = open(os.path.join("cache", file), "rb").read()
        if udp:
            client_soc.sendto(f, address)
        else:
            client_soc.send(f)
        try:
            data: bytes = client_soc.recv(4096)
            i = i + 1
            print(int(i/9999*1000)/10, "%")
            if f != data:
                e = e + 1
        except socket.timeout:
            m = m + 1

    end_time = datetime.now()
    print("Celkem bylo přeneseno", i, "balíčků")
    if udp:
        print("Pomocí UDP")
    else:
        print("Pomocí TCP")
    print("Z celkových", i, "balíčků dorazilo", e, "poškozených")
    print("To je chybovost", e/i*100, "%")
    if udp:
        print("Z celkových", i, "balíčků nedorazilo", m)
        print("To je ztrátovost", e/i*100, "%")
    print("Celkový spotřebovaný čas činí", end_time-start_time)
    input("Pro opuštění programu stiskněte Enter")


def start2(client_soc: socket.socket, udp: bool = False, address=None):
    """Funkce pro odeslání 100,000 balíčků s vyplněným jedním charakterem"""
    f = "1".encode('utf-8')
    j = 0
    e = 0
    m = 0
    if udp:
        client_soc.settimeout(2.0)
    start_time = datetime.now()
    for i in range(100000):
        if udp:
            client_soc.sendto(f, address)
        else:
            client_soc.send(f)
        print(int(i/100000*1000)/10, "%")
        try:
            data: bytes = client_soc.recv(4096)
            j = j + 1
            if data != f:
                e = e + 1
        except socket.timeout:
            m = m + 1
    end_time = datetime.now()
    print("Celkem bylo přeneseno", "100,000", "balíčků")
    if udp:
        print("Pomocí UDP")
    else:
        print("Pomocí TCP")
    print("Z celkových", 100000, "balíčků dorazilo", e, "poškozených")
    print("To je chybovost", e / j * 100, "%")
    if udp:
        print("Z celkových", 100000, "balíčků nedorazilo", m)
        print("To je ztrátovost", e/100000*100, "%")
    print("Celkový spotřebovaný čas činí", end_time - start_time)
    input("Pro opuštění programu stiskněte Enter")



if __name__ == "__main__":
    init()
