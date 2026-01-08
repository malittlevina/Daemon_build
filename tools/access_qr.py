import socket
import qrcode
import sys

def get_local_ip():
    try:
        # Connect to a public DNS to find the most appropriate local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_qr():
    ip = get_local_ip()
    port = 5000
    url = f"http://{ip}:{port}"
    
    print(f"\n[Access] To test on mobile/tablet, connect to the same Wi-Fi and open:")
    print(f"👉  {url}")
    print("\nOr scan this QR Code:\n")
    
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.print_ascii(invert=True)

if __name__ == "__main__":
    generate_qr()
