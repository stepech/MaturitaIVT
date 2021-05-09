import socket

DEBUG = False


def main(serv_sock: socket.socket, udp: bool = False):
    """posílá veškerou komunikaci zpátky odesílateli. Hlavní program se nachází ve složce client"""
    print("Spouštím navraceč balíčků")
    if udp:
        while True:
            try:
                data, address = serv_sock.recvfrom(1024)
                if data == "VERIFY".encode('utf-8'):
                    serv_sock.sendto("CONFVER".encode('utf-8'), address)
                    print("Přijato připojení z", address)
                    continue
                serv_sock.sendto(data, address)
            except ConnectionResetError:
                pass
    else:
        while True:
            data = serv_sock.recv(1024)
            if not data: break
            print("Přijmut balíček, odesílám přes TCP")
            serv_sock.send(data)
        serv_sock.close()


def get_ip_port():
    """často používaná metoda, získá od uživatele ip adresu a číslo portu"""
    if DEBUG:
        return "127.0.0.1", 3310
    print("Zadejte číslo portu na který se server naváže\nPro výchozí port (3310) ponechte prázdné")
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
    """Provede speciální UDP handshake, aby potvrdil spojení"""
    server_ip, port = get_ip_port()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((server_ip, port))

    print("Vytvořen UDP server na ip adrese", server_ip, "a portu", port)
    print("Vypněte server klávesovou zkratkou ctrl + C")

    main(server_sock, True)


def tcp_start():
    """Provede TCP handshake"""

    server_ip, port = get_ip_port()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, port))

    print("Vytvořen TCP server na ip adrese", server_ip, "a portu", port)
    print("Vypněte server klávesovou zkratkou ctrl + C")

    server_socket.listen(1)
    connection, address = server_socket.accept()
    print("Přijato TCP připojení z", address)
    main(connection)


def init():
    """Naběhne při spuštění"""
    print("Spouštím server")
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


if __name__ == "__main__":
    init()
