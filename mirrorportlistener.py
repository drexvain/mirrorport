import socket
import threading
import cv2
import numpy as np
from colorama import Fore, init

init(autoreset=True)

LISTEN_IP = '0.0.0.0'
PORT = 9999
running = False
client = None

def recv_all(sock, size):
    data = b''
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("connection lost")
        data += part
    return data

def terminal_control():
    global running
    while True:
        cmd = input(Fore.YELLOW + '[drexvain] > ').strip().lower()
        if cmd == 'start':
            running = True
            print(Fore.GREEN + '[+] streaming started')
        elif cmd == 'stop':
            running = False
            print(Fore.RED + '[-] streaming stopped')
        elif cmd == 'help':
            print(Fore.CYAN + '''
commands:
 start   - start screen stream
 stop    - pause stream
 help    - show commands
''')
        else:
            print(Fore.RED + '[!] unknown command')

def listener_main():
    global client
    fps_choice = input(Fore.CYAN + '[?] choose framerate (1=30fps, 2=60fps): ').strip()
    if fps_choice not in ['1', '2']:
        fps_choice = '1'

    s = socket.socket()
    s.bind((LISTEN_IP, PORT))
    s.listen(1)
    print(Fore.BLUE + f"[+] waiting for connection on {LISTEN_IP}:{PORT} ...")
    client, addr = s.accept()
    print(Fore.GREEN + f"[+] connected from {addr[0]}:{addr[1]}")

    client.send(fps_choice.encode())
    threading.Thread(target=terminal_control, daemon=True).start()

    try:
        while True:
            client.send(b'1' if running else b'0')
            if running:
                size_data = recv_all(client, 4)
                size = int.from_bytes(size_data, 'big')
                img_data = recv_all(client, size)
                img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    cv2.imshow('mirrorport by drexvainn', img)
                    if cv2.waitKey(1) == ord('q'):
                        break
            else:
                time.sleep(0.1)
    except Exception as e:
        print(Fore.RED + f"[!] error: {e}")
    finally:
        client.close()
        cv2.destroyAllWindows()
# je savais pas si je devais faire que en anglais ou en francais 
if __name__ == '__main__':
    import time
    listener_main()
