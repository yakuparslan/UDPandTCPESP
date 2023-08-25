import socket
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading


def get_local_ip():
    try:
    # Use the hostname of the computer to get the local IPv4 address on the network
        hostname = socket.gethostname()
        addresses = socket.getaddrinfo(hostname, None, socket.AF_INET)
        for addr in addresses:
            ip = addr[4][0]
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            return ip

        return "127.0.0.1"  # Return loopback address if no suitable IPv4 address is found

    except Exception as e:
        print(f"Error while getting local IPv4 address: {e}")
        return "127.0.0.1"




def send_udp_message(target_ip, target_port, message):
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(message.encode('utf-8'), (target_ip, target_port))
        udp_socket.close()
        print(f"Message sent to {target_ip}:{target_port} - {message}")

    except Exception as e:
        print(f"Error while sending UDP message: {e}")

def receive_udp_message(bind_ip, bind_port, buffer_size=1024):
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((bind_ip, bind_port))
        print(f"Listening for UDP messages on {bind_ip}:{bind_port}")

        while True:
            data, address = udp_socket.recvfrom(buffer_size)
            received_message = data.decode('utf-8')
            print(f"Received message from {address[0]} - {received_message}")
            update_received_messages(f"{address[0]} - {received_message}")

    except Exception as e:
        print(f"Error while receiving UDP message: {e}")

    finally:
        udp_socket.close()

def send_message_with_custom_text():
    target_ips = target_ips_listbox.curselection()

    if not target_ips:
        messagebox.showerror("Error", "Please select at least one target IP.")
        return

    target_port = int(target_port_entry.get())
    message = custom_message_entry.get()

    if not target_port or not message:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    for index in target_ips:
        target_ip = target_ips_listbox.get(index).strip()
        start_index = target_ip.find('192.')
        target_ip = target_ip[start_index:]
        send_udp_message(target_ip, target_port, message)


def send_delay_message(slider_value):
    int_value = int(float(slider_value))
    delay_value_label.config(text=f"{int_value}") 
    
    selected_ips = target_ips_listbox.curselection()

    if not selected_ips:
        messagebox.showerror("Error", "Please select at least one target IP.")
        return

    target_port = int(target_port_entry.get())

    if not target_port:
        messagebox.showerror("Error", "Please enter the target port.")
        return
    float_value = float(slider_value)
    delay_value = int(float_value)
    message = f"DELAY:{delay_value}"

    for index in selected_ips:
        target_ip = target_ips_listbox.get(index).strip()
        start_index = target_ip.find('192.')
        target_ip = target_ip[start_index:]
        send_udp_message(target_ip, target_port, message)

def send_speed_message(slider_value):
    int_value = int(float(slider_value))
    speed_value_label.config(text=f"{int_value}") 
    
    selected_ips = target_ips_listbox.curselection()

    if not selected_ips:
        messagebox.showerror("Error", "Please select at least one target IP.")
        return

    target_port = int(target_port_entry.get())

    if not target_port:
        messagebox.showerror("Error", "Please enter the target port.")
        return
    float_value = float(slider_value)
    delay_value = int(float_value*3)
    message = f"BPM:{delay_value}"

    for index in selected_ips:
        target_ip = target_ips_listbox.get(index).strip()
        start_index = target_ip.find('192.')
        target_ip = target_ip[start_index:]
        send_udp_message(target_ip, target_port, message)


def upload_ips_from_file():
    try:
    # Try to read the file from "ip.txt"
        file_path = "ip.txt"
        with open(file_path, "r") as file:
            target_ips_listbox.delete(0, tk.END)
            target_ips_listbox.insert(tk.END, *file.read().splitlines())
    except FileNotFoundError:   
        # If "ip.txt" doesn't exist, prompt the user to choose the file
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                target_ips_listbox.delete(0, tk.END)
                target_ips_listbox.insert(tk.END, *file.read().splitlines())
def clear_received_messages():
    received_messages_text.config(state=tk.NORMAL)
    received_messages_text.delete('1.0', tk.END)
    received_messages_text.config(state=tk.DISABLED)


def update_received_messages(message):
    received_messages_text.config(state=tk.NORMAL)
    received_messages_text.insert(tk.END, f"{message}\n")
    received_messages_text.config(state=tk.DISABLED)
    received_messages_text.see("end")  # Scroll to the end

def send_message_to_selected_ips(message):
    selected_ips = target_ips_listbox.curselection()

    if not selected_ips:
        messagebox.showerror("Error", "Please select at least one target IP.")
        return

    target_port = int(target_port_entry.get())

    if not target_port:
        messagebox.showerror("Error", "Please enter the target port.")
        return

    for index in selected_ips:
        target_ip = target_ips_listbox.get(index).strip()
        start_index = target_ip.find('192.')
        target_ip = target_ip[start_index:]
        send_udp_message(target_ip, target_port, message)

def create_gui():
    global target_ips_listbox, target_port_entry, custom_message_entry, received_messages_text,delay_value_label,speed_value_label
    root = tk.Tk()
    root.title("UDP Message Sender and Receiver")
    
    send_frame = ttk.Frame(root)
    send_frame.grid(row=0, column=0, padx=10, pady=10)

    target_ips_label = ttk.Label(send_frame, text="Target IPs:")
    target_ips_label.grid(row=0, column=0, columnspan=2, sticky="w")

    upload_button = ttk.Button(send_frame, text="Upload", command=upload_ips_from_file)
    upload_button.grid(row=1, column=0, padx=(0, 5), pady=(5, 0))

    target_ips_listbox = tk.Listbox(send_frame, selectmode=tk.MULTIPLE)
    target_ips_listbox.grid(row=1, column=1, padx=(0, 5), pady=(5, 0), sticky="nsew")

    target_ips_listbox_scroll = ttk.Scrollbar(send_frame, command=target_ips_listbox.yview)
    target_ips_listbox_scroll.grid(row=1, column=2, sticky="ns")
    target_ips_listbox.config(yscrollcommand=target_ips_listbox_scroll.set)

    target_port_label = ttk.Label(send_frame, text="Target Port:")
    target_port_label.grid(row=2, column=0, sticky="w")

    target_port_entry = ttk.Entry(send_frame)
    target_port_entry.grid(row=2, column=1, padx=(0, 5), sticky="we")
    target_port_entry.insert(tk.END, "1234")

    custom_message_label = ttk.Label(send_frame, text="Custom Message:")
    custom_message_label.grid(row=3, column=0, sticky="w", pady=(5, 0))

    custom_message_entry = ttk.Entry(send_frame)
    custom_message_entry.grid(row=3, column=1, padx=(0, 5), sticky="we", pady=(5, 0))
    custom_message_entry.insert(tk.END, "T15:00:00")
    send_custom_button = ttk.Button(send_frame, text="Send", command=send_message_with_custom_text)
    send_custom_button.grid(row=3, column=2, padx=(0, 5), pady=(5, 0))

    
    start_button = ttk.Button(send_frame, text="Start", command=lambda: send_message_to_selected_ips("START"))
    start_button.grid(row=4, column=0, padx=(0, 5), pady=(5, 0))

    stop_button = ttk.Button(send_frame, text="Stop", command=lambda: send_message_to_selected_ips("STOP"))
    stop_button.grid(row=4, column=1, padx=(0, 5), pady=(5, 0))

    reset_button = ttk.Button(send_frame, text="Reset", command=lambda: send_message_to_selected_ips("RESET"))
    reset_button.grid(row=3, column=3, padx=(0, 5), pady=(  5, 0))

    rec = ttk.Button(send_frame, text="Cycle", command=lambda: send_message_to_selected_ips("REC"))
    rec.grid(row=4, column=3, padx=(0, 5), pady=(  5, 0))

    push_button = ttk.Button(send_frame, text="Push", command=lambda: send_message_to_selected_ips("PUSH"))
    push_button.grid(row=4, column=2, padx=(0, 5), pady=(5, 0))

    clear_button = ttk.Button(send_frame, text="Clear", command=clear_received_messages)
    clear_button.grid(row=8, column=1, padx=(0, 5), pady=(5, 0))

    delay_label = ttk.Label(send_frame, text="Delay:")
    delay_label.grid(row=6, column=0, sticky="w")

    delay_slider = ttk.Scale(send_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200,command=send_delay_message)
    delay_slider.grid(row=6, column=1, padx=(0, 5), sticky="we")
    delay_slider.set(30)  # Set the default value to 30

    delay_value_label = ttk.Label(send_frame, text="30")
    delay_value_label.grid(row=6, column=2, padx=(5, 0), pady=(5, 0))

    save = ttk.Button(send_frame, text="Save", command=lambda: send_message_to_selected_ips("SAVE"))
    save.grid(row=6, column=3, padx=(0, 5), pady=(  5, 0))


    speed_label = ttk.Label(send_frame, text="Speed:")
    speed_label.grid(row=7, column=0, sticky="w")

    speed_slider = ttk.Scale(send_frame, from_=0, to=255, orient=tk.HORIZONTAL, length=200,command=send_speed_message)
    speed_slider.grid(row=7, column=1, padx=(0, 5), sticky="we")
    speed_slider.set(40)  # Set the default value to 30

    speed_value_label = ttk.Label(send_frame, text="40")
    speed_value_label.grid(row=7, column=2, padx=(5, 0), pady=(5, 0))




    received_messages_text = tk.Text(send_frame, wrap=tk.WORD, state=tk.DISABLED)
    received_messages_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

    received_messages_scroll = ttk.Scrollbar(send_frame, command=received_messages_text.yview)
    received_messages_scroll.grid(row=5, column=4, sticky="ns")
    received_messages_text.config(yscrollcommand=received_messages_scroll.set)


    try:
        with open("ip.txt", "r") as file:
            target_ips_listbox.insert(tk.END, *file.read().splitlines())
    except FileNotFoundError:
        pass  # If the file doesn't exist, do nothing

    try:
        ip_to_device = {
            "192.168.64.101": "HR01",
            "192.168.64.102": "HR02",
            "192.168.64.103": "HR03",
            "192.168.64.104": "HR04",
            "192.168.64.105": "HR05",
            "192.168.64.106": "HR06",
            "192.168.64.107": "HR07",
            "192.168.64.108": "HR08",
            "192.168.64.109": "HR09",
            "192.168.64.110": "HR10",
            "192.168.64.111": "HR11",
            "192.168.64.112": "HR12",
            "192.168.64.113": "HR13",
            "192.168.64.114": "HR14",
            "192.168.64.115": "HR15",
            "192.168.64.116": "HR16",
            "192.168.64.117": "HR17",
            "192.168.64.118": "HR18",
            "192.168.64.119": "HR19",
            "192.168.64.120": "HR20",
            "192.168.64.121": "HR21"
        }

        for ip, device in ip_to_device.items():
            target_ips_listbox.insert(tk.END, f"{device} - {ip}")

    except FileNotFoundError:
        pass  # If the file doesn't exist, do nothing


    local_ip = get_local_ip()
    # Start receiving messages in a separate thread
    receive_thread = threading.Thread(target=receive_udp_message, args=(local_ip, 1234))
    receive_thread.daemon = True
    receive_thread.start()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
    try:
        ip_to_device = {
            "192.168.64.101": "HR01",
            "192.168.64.102": "HR02",
            "192.168.64.103": "HR03",
            "192.168.64.104": "HR04",
            "192.168.64.105": "HR05",
            "192.168.64.106": "HR06",
            "192.168.64.107": "HR07",
            "192.168.64.108": "HR08",
            "192.168.64.109": "HR09",
            "192.168.64.110": "HR10",
            "192.168.64.111": "HR11",
            "192.168.64.112": "HR12",
            "192.168.64.113": "HR13",
            "192.168.64.114": "HR14",
            "192.168.64.115": "HR15",
            "192.168.64.116": "HR16",
            "192.168.64.117": "HR17",
            "192.168.64.118": "HR18",
            "192.168.64.119": "HR19",
            "192.168.64.120": "HR20",
            "192.168.64.121": "HR21",
            "192.168.64.140": "HR22"
        }

        for index, (ip, device) in enumerate(ip_to_device.items()):
            target_ips_listbox.insert(tk.END, f"{device} - {ip}", index)

    except FileNotFoundError:
        pass  # If the file doesn't exist, do nothing

    