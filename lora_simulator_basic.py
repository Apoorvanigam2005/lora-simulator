import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

TX_POWER = 20

def calculate_rssi(distance_km, sf, noise_level_dbm):
    path_loss = 30 + 20 * np.log10(distance_km + 0.1) + 20 * np.log10(868)
    spreading_penalty = (sf - 7) * 1.0
    rssi = TX_POWER - path_loss - spreading_penalty - (noise_level_dbm * 0.4)
    return round(rssi, 2)

def calculate_snr(rssi, sf):
    required_snr = -40 + sf
    return round(rssi - required_snr, 2)

root = tk.Tk()
root.title("LoRa Simulator - Student Edition")
root.geometry("1200x700")

theme_mode = tk.StringVar(value="dark")

def apply_theme():
    dark = (theme_mode.get() == "dark")
    bg = "#1e1e1e" if dark else "white"
    fg = "white" if dark else "black"
    box_bg = "#2d2d2d" if dark else "#f0f0f0"
    text_fg = "lightgreen" if dark else "green"

    root.configure(bg=bg)
    control_frame.configure(bg=bg)
    graph_frame.configure(bg=bg)

    for widget in control_frame.winfo_children():
        if isinstance(widget, (tk.Label, tk.Button)):
            widget.configure(bg=bg, fg=fg)
        elif isinstance(widget, tk.Scale):
            widget.configure(bg=bg, fg=fg, highlightbackground=bg)

    status_label.configure(bg=bg, fg="orange")
    log_box.configure(bg=box_bg, fg=text_fg)
    node_panel.configure(bg=box_bg, fg="lightblue")

control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

graph_frame = tk.Frame(root)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

distance_var = tk.DoubleVar(value=1.0)
sf_var = tk.IntVar(value=7)
payload_var = tk.IntVar(value=32)
noise_var = tk.DoubleVar(value=0)
message_var = tk.StringVar(value="Hello")

tk.Label(control_frame, text="Distance (km):").pack(anchor='w')
tk.Entry(control_frame, textvariable=distance_var, width=10).pack()

tk.Label(control_frame, text="Spreading Factor (SF):").pack(anchor='w', pady=(10, 0))
sf_menu = ttk.Combobox(control_frame, values=[7, 8, 9, 10, 11, 12], textvariable=sf_var, state="readonly", width=8)
sf_menu.pack()

tk.Label(control_frame, text="Payload Size (Bytes):").pack(anchor='w', pady=(10, 0))
tk.Entry(control_frame, textvariable=payload_var, width=10).pack()

tk.Label(control_frame, text="Noise Level (dBm):").pack(anchor='w', pady=(10, 0))
tk.Scale(control_frame, from_=0, to=20, orient='horizontal', variable=noise_var).pack()

tk.Label(control_frame, text="Message:").pack(anchor='w', pady=(10, 0))
tk.Entry(control_frame, textvariable=message_var, width=20).pack()

tk.Label(control_frame, text="Theme:").pack(anchor='w', pady=(10, 0))
ttk.Combobox(control_frame, values=["dark", "light"], textvariable=theme_mode, width=10, state="readonly").pack()
tk.Button(control_frame, text="Apply Theme", command=apply_theme).pack(pady=5)

status_label = tk.Label(control_frame, text="")
status_label.pack(pady=5)

node_panel = tk.Text(control_frame, height=5, width=40)
node_panel.pack(pady=5)

log_box = tk.Text(control_frame, height=8, width=40)
log_box.pack(pady=5)

fig, (ax_rssi, ax_snr) = plt.subplots(1, 2, figsize=(10, 4))
fig.tight_layout(pad=4)

ax_rssi.set_title("RSSI vs Distance")
ax_rssi.set_xlabel("Distance (km)")
ax_rssi.set_ylabel("RSSI (dBm)")
graph_rssi_success, = ax_rssi.plot([], [], 'go-', label='Success')
graph_rssi_fail, = ax_rssi.plot([], [], 'ro-', label='Lost')
ax_rssi.legend()

ax_snr.set_title("SNR vs Distance")
ax_snr.set_xlabel("Distance (km)")
ax_snr.set_ylabel("SNR (dB)")
graph_snr_success, = ax_snr.plot([], [], 'bo-', label='SNR')
ax_snr.legend()

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

distances_success = []
rssi_success = []
snr_success = []
distances_fail = []
rssi_fail = []

total_packets = 0
success_packets = 0

def update_pdr():
    if total_packets == 0:
        pdr_text = "PDR: 0%"
    else:
        pdr = (success_packets / total_packets) * 100
        pdr_text = f"PDR: {pdr:.1f}% | Sent: {total_packets} | Success: {success_packets}"
    status_label.config(text=pdr_text)

def send_packet():
    global total_packets, success_packets
    distance = distance_var.get()
    sf = sf_var.get()
    payload = payload_var.get()
    noise = noise_var.get()
    msg = message_var.get()

    if distance > 10:
        status_label.config(text="⚠️ Warning: LoRa range exceeded (10 km max)", fg="orange")
    else:
        status_label.config(fg="lightgreen")

    rssi = calculate_rssi(distance, sf, noise)
    snr = calculate_snr(rssi, sf)

    status = "Success" if snr > 0 or (distance < 4 and noise < 15) else "Lost"

    total_packets += 1
    if status == "Success":
        success_packets += 1
        distances_success.append(distance)
        rssi_success.append(rssi)
        snr_success.append(snr)
    else:
        distances_fail.append(distance)
        rssi_fail.append(rssi)

    log_box.insert(tk.END, f"Dist: {distance:.1f}km | SF: {sf} | RSSI: {rssi} | SNR: {snr} | {status}\n")
    log_box.see(tk.END)

    node_panel.insert(tk.END, f"Node A ➜ Node B: \"{msg}\"\nStatus: {status}\n\n")
    node_panel.see(tk.END)

    graph_rssi_success.set_data(distances_success, rssi_success)
    graph_rssi_fail.set_data(distances_fail, rssi_fail)
    graph_snr_success.set_data(distances_success, snr_success)

    ax_rssi.relim()
    ax_rssi.autoscale_view()
    ax_snr.relim()
    ax_snr.autoscale_view()
    canvas.draw()

    update_pdr()

def reset_simulation():
    global distances_success, rssi_success, snr_success, distances_fail, rssi_fail, total_packets, success_packets
    distances_success.clear()
    rssi_success.clear()
    snr_success.clear()
    distances_fail.clear()
    rssi_fail.clear()
    total_packets = 0
    success_packets = 0

    graph_rssi_success.set_data([], [])
    graph_rssi_fail.set_data([], [])
    graph_snr_success.set_data([], [])

    ax_rssi.relim()
    ax_rssi.autoscale_view()
    ax_snr.relim()
    ax_snr.autoscale_view()
    canvas.draw()

    log_box.delete('1.0', tk.END)
    node_panel.delete('1.0', tk.END)
    status_label.config(text="")

tk.Button(control_frame, text="Send Packet", command=send_packet).pack(pady=10)
tk.Button(control_frame, text="Reset", command=reset_simulation).pack(pady=5)

apply_theme()
root.mainloop()
