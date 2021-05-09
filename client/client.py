import socket
import os
from datetime import datetime, timedelta
from time import sleep

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
    try:
        mode: int = int(input("> "))
    except ValueError:
        init()
        return
    if mode == 1:
        tcp_start()
    elif mode == 2:
        udp_start()
    else:
        print("Zadejte pouze číslo 1 nebo 2")
        init()


def get_ip_port():
    """často používaná metoda, získá od uživatele ip adresu a číslo portu"""
    if DEBUG:
        return "127.0.0.1", 3310
    print("Zadejte číslo portu na který se klient naváže\nPro výchozí port (3310) ponechte prázdné")
    port: str = input("> ")
    if port == "":
        port = "3310"
    try:
        port: int = int(port)
    except ValueError:
        print("Port může být zadán pouze číslicemi a bez mezer.\nZadejte port znovu")
        return get_ip_port()
    print("Zadejte IP adresu serveru")
    server_ip: str = input("> ")
    return server_ip, port


def udp_start():
    """Inicializuje UDP připojení. Provede kontrolní výměnu balíčků jako zkoušku"""
    ip, port = get_ip_port()
    payload = "VERIFY".encode('utf-8')
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = None
    try:
        client_sock.sendto(payload, (ip, port))
        data = client_sock.recv(1024)
    except ConnectionResetError:
        pass
    except socket.gaierror:
        print("Adresa zadána ve špatném formátu")
        udp_start()
        return
    while data != "CONFVER".encode('utf-8'):
        print("Neobdržena odpověď serveru. Je server spuštěn a vše správně zadáno?\nZkouším znova za 4 vteřiny")
        sleep(4)
        client_sock.sendto(payload, (ip, port))
        try:
            data = client_sock.recv(1024)
        except ConnectionResetError:
            continue
    print("Spojení navázáno!")
    client_sock.settimeout(2.0)
    if do_big():
        start1(client_sock, True, (ip, port))
    else:
        start2(client_sock, True, (ip, port))


def tcp_start():
    """Inicializuje TCP připojení."""
    ip, port = get_ip_port()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_sock.connect((ip, port))
            break
        except ConnectionRefusedError:
            print("Spojení odmítnuto serverem. Je program na server spuštěn a port správně nakonfigurován?\nZkouším znova za 4 vteřiny")
            sleep(4)
        except socket.gaierror:
            print("Zadána špatná IP adresa")
            tcp_start()
            return

    print("Spojení navázáno")
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
    try:
        choice = int(input("> "))
    except ValueError:
        print("Zadejte pouze číslice 1 nebo 2")
        return do_big()
    if choice == 1:
        print("Spouštím odesílání velkých souborů")
        return True
    elif choice == 2:
        print("Spouštím odesílání malých souborů")
        return False
    else:
        print("Zadejte pouze číslice 1 nebo 2")
        return do_big()


"""
##########################
###HLAVNÍ ČÁST PROGRAMU###
##########################
"""


def start1(client_soc: socket.socket, udp: bool = False, address=None):
    """Funkce pro odeslání 9999 souborů o celkové velikosti 10 MB"""

    try:
        for file in os.listdir("cache"):
            os.remove(os.path.join("cache", file))
    except FileNotFoundError:
        os.mkdir("cache")

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
    p_results(udp, i, e, m, end_time - start_time)


def start2(client_soc: socket.socket, udp: bool = False, address=None):
    """Funkce pro odeslání 100,000 balíčků s vyplněným jedním charakterem"""
    f = "1".encode('utf-8')
    j = 0
    e = 0
    m = 0
    start_time = datetime.now()
    for i in range(100000):
        if udp:
            client_soc.sendto(f, address)
        else:
            client_soc.send(f)
        try:
            data: bytes = client_soc.recv(4096)
            j = j + 1
            print(int(i / 100000 * 1000) / 10, "%")
            if data != f:
                e = e + 1
        except socket.timeout:
            m = m + 1

    end_time = datetime.now()
    p_results(udp, j, e, m, end_time - start_time)


def p_results(udp: bool, i: int, e: int, m: int, duration: timedelta):
    print("Celkem bylo přeneseno", i, "balíčků")
    if udp:
        print("Pomocí UDP")
    else:
        print("Pomocí TCP")
    print("Z celkových", i, "balíčků dorazilo", e, "poškozených")
    print("To je chybovost", e / i * 100, "%")
    print("Z celkových", i, "balíčků nedorazilo", m)
    print("To je ztrátovost", e / i * 100, "%")
    print("Celkový hrubý spotřebovaný čas činí", duration)
    if udp and m != 0:
        # úprava aby se z výpočtu odečetla prodleva kdy program čeká na data která nepřijdou (timeout)
        substract = timedelta(seconds=m*2)
        print("Celkový čistý čas ciní", duration - substract)
    input("Pro opuštění programu stiskněte Enter")


if __name__ == "__main__":
    init()
