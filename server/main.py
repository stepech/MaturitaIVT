import socket

DEBUG = False


def main(serv_sock: socket.socket, udp: bool = False):
    """posílá veškerou komunikaci zpátky odesílateli. Hlavní program se nachází ve složce client"""
    print("Spouštím navraceč balíčků")
    if udp:
        while True:
            try:
                data, address = serv_sock.recvfrom(1024)
                print(data)
                serv_sock.sendto(data, address)
            except ConnectionResetError:
                pass
    else:
        while True:
            data = serv_sock.recv(1024)
            if not data: break
            print(data)
            serv_sock.send(data)
        serv_sock.close()


def get_ip_port():
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
    """Provede speciální UDP handshake, aby potvrdil spojení"""
    server_ip, port = get_ip_port()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((server_ip, port))

    print("Vytvořen UDP server na ip adrese", server_ip, "a portu", port)
    print("Vypněte server klávesovou zkratkou ctrl + C")

    while True:
        data, addr = server_sock.recvfrom(1024)
        if data == "VERIFY".encode('utf-8'):
            server_sock.sendto("CONFVER".encode('utf-8'), addr)
            break
    print("Přijato UDP připojení z", addr)
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


if __name__ == "__main__":
    """Inicializuje program"""
    print("Spouštím server")
    print("Zadejte číslo požadovaného módu:\n1 - TCP\n2 - UDP")
    mode: int = int(input("> "))
    if mode == 1:
        tcp_start()
    elif mode == 2:
        udp_start()
    else:
        pass
