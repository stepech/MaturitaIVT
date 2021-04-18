import socket

DEBUG = True


def main(serv_sock: socket.socket, udp: bool = False):
    print("Příchozí spojení navázáno")
    if udp:
        while True:
            data, address = serv_sock.recvfrom(4096)
            print(data)
            serv_sock.sendto(data, address)
    else:
        while True:
            try:
                data = serv_sock.recv(4096)
                if data:
                    print(data)
                    serv_sock.sendall(data)
            finally:
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
    main(server_sock, True)


def tcp_start():

    server_ip, port = get_ip_port()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, port))

    print("Vytvořen TCP server na ip adrese", server_ip, "a portu", port)
    print("Vypněte server klávesovou zkratkou ctrl + C")

    server_socket.listen(1)
    connection, address = server_socket.accept()

    main(connection)


if __name__ == "__main__":
    print("Spouštím server")
    print("Zadejte číslo požadovaného módu:\n1 - TCP\n2 - UDP")
    mode: int = int(input("> "))
    if mode == 1:
        tcp_start()
    elif mode == 2:
        udp_start()
    else:
        print("Zadejte pouze číslo 1 nebo 2")
