import socket
import time
import mss
import cv2
import numpy as np

SERVER_IP = '127.0.0.1'  
PORT = 9999

def send_frames():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print("[+] connecting to listener...")
        sock.connect((SERVER_IP, PORT))
        print("[+] connected.")

        fps_byte = sock.recv(1)
        fps = 60 if fps_byte == b'2' else 30
        delay = 1 / fps

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while True:
                control = sock.recv(1)
                if control == b'1':
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    data = encoded.tobytes()
                    size = len(data).to_bytes(4, 'big')
                    sock.sendall(size + data)
                    time.sleep(delay)
                else:
                    time.sleep(0.1)

if __name__ == '__main__':
    send_frames()
