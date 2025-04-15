import os
import paramiko
from ftplib import FTP
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
from PIL import Image, ImageTk

# Server configurations (replace with your server details)
SERVERS = {
 
}

class FileUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Singapore File Uploader")
        self.root.geometry("600x400")
        self.root.configure(bg="#2E3440")  # Dark theme background

        # Custom font
        self.custom_font = ("Helvetica", 12)

        # Drag and drop support
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        # File list
        self.file_list = []

        # Header
        self.header = tk.Label(root, text="Singapore File Uploader", bg="#2E3440", fg="#ECEFF4", font=("Helvetica", 18, "bold"))
        self.header.pack(pady=10)

        # Instructions
        self.label = tk.Label(root, text="Drag and drop files or click 'Select Files' to upload", bg="#2E3440", fg="#ECEFF4", font=self.custom_font)
        self.label.pack(pady=10)

        # Select Files Button
        self.select_button = ttk.Button(root, text="Select Files", command=self.select_files, style="TButton")
        self.select_button.pack(pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", style="TProgressbar")
        self.progress.pack(pady=20)

        # Upload Button
        self.upload_button = ttk.Button(root, text="Upload Files", command=self.start_upload, style="TButton", state=tk.DISABLED)
        self.upload_button.pack(pady=5)

        # Status Label
        self.status_label = tk.Label(root, text="", bg="#2E3440", fg="#ECEFF4", font=self.custom_font)
        self.status_label.pack(pady=10)

        # Loading Animation
        self.loading_label = tk.Label(root, text="", bg="#2E3440", fg="#ECEFF4", font=self.custom_font)
        self.loading_label.pack(pady=5)

        # Configure styles
        self.configure_styles()

    def configure_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.theme_use("clam")

        # Button style
        style.configure("TButton", font=self.custom_font, background="#4C566A", foreground="#ECEFF4", borderwidth=0, padding=10)
        style.map("TButton", background=[("active", "#5E81AC")])

        # Progress bar style
        style.configure("TProgressbar", background="#5E81AC", troughcolor="#3B4252", thickness=20)

    def on_drop(self, event):
        """Handle files dropped into the window."""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if os.path.isfile(file):
                self.file_list.append(file)
        self.update_ui()

    def select_files(self):
        """Open a file dialog to select files."""
        files = filedialog.askopenfilenames(title="Select Files")
        if files:
            self.file_list.extend(files)
            self.update_ui()

    def update_ui(self):
        """Update the UI based on the current state."""
        if self.file_list:
            self.upload_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"{len(self.file_list)} file(s) selected")
        else:
            self.upload_button.config(state=tk.DISABLED)
            self.status_label.config(text="No files selected")

    def start_upload(self):
        """Start the upload process in a separate thread."""
        self.upload_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)
        self.loading_label.config(text="Uploading...")

        # Start upload in a separate thread
        upload_thread = threading.Thread(target=self.upload_files)
        upload_thread.start()

    def upload_files(self):
        """Upload files to the appropriate server (FTP or SFTP)."""
        if not self.file_list:
            messagebox.showwarning("No Files", "No files selected for upload.")
            return

        self.progress["value"] = 0
        self.progress["maximum"] = len(self.file_list)

        # Track successful and failed uploads
        successful_uploads = []
        failed_uploads = []

        for index, file_path in enumerate(self.file_list):
            file_name = os.path.basename(file_path)
            server_key = file_name[:7].upper()

            if server_key not in SERVERS:
                failed_uploads.append((file_name, "No server configured for prefix"))
                continue

            server_config = SERVERS[server_key]
            try:
                if server_config["type"] == "sftp":
                    self.upload_to_sftp(file_path, server_config)
                elif server_config["type"] == "sftp2222":
                    self.upload_to_sftp2222(file_path, server_config)
                elif server_config["type"] == "sftp1":
                    self.upload_to_sftp1(file_path, server_config)
                elif server_config["type"] == "sftp2":
                    self.upload_to_sftp2(file_path, server_config)
                elif server_config["type"] == "ftp":
                    self.upload_to_ftp(file_path, server_config)
                else:
                    failed_uploads.append((file_name, f"Unsupported server type: {server_config['type']}"))
                    continue

                successful_uploads.append((file_name, server_config["username"]))
                self.progress["value"] = index + 1
                self.root.update_idletasks()
            except Exception as e:
                failed_uploads.append((file_name, f"Error: {str(e)}"))

        # Display summary
        self.show_summary(successful_uploads, failed_uploads)

        # Reset UI
        self.file_list.clear()
        self.update_ui()
        self.loading_label.config(text="Upload Complete")
        self.upload_button.config(state=tk.NORMAL)
        self.select_button.config(state=tk.NORMAL)

    def show_summary(self, successful_uploads, failed_uploads):
        """Display a summary of successful and failed uploads."""
        summary = "Upload Summary:\n\n"
        summary += "Successful Uploads:\n"
        for file_name, username in successful_uploads:
            summary += f"- {file_name} (Server: {username})\n"

        summary += "\nFailed Uploads:\n"
        for file_name, error in failed_uploads:
            summary += f"- {file_name} (Error: {error})\n"

        messagebox.showinfo("Upload Summary", summary)

    def upload_to_sftp(self, file_path, server_config):
        """Upload a file to an SFTP server port 22 root directory."""
        transport = paramiko.Transport((server_config["host"], 22))
        transport.connect(username=server_config["username"], password=server_config["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)

        file_name = os.path.basename(file_path)
        remote_path = f"/{file_name}"  # Change this to your desired remote path
        sftp.put(file_path, remote_path)
        sftp.close()
        transport.close()

    def upload_to_sftp1(self, file_path, server_config):
        """Upload a file to an SFTP server over port 2222 root directory."""
        transport = paramiko.Transport((server_config["host"], 2222))
        transport.connect(username=server_config["username"], password=server_config["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)

        file_name = os.path.basename(file_path)
        remote_path = f"/{file_name}"  # Change this to your desired remote path
        sftp.put(file_path, remote_path)
        sftp.close()
        transport.close()

    def upload_to_sftp2(self, file_path, server_config):
        """Upload a file to an SFTP server for integration 1500204 directory."""
        transport = paramiko.Transport((server_config["host"], 2222))
        transport.connect(username=server_config["username"], password=server_config["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)

        file_name = os.path.basename(file_path)
        remote_path = f"/POS/15/1500204/{file_name}"  # Change this to your desired remote path
        sftp.put(file_path, remote_path)
        sftp.close()
        transport.close()

    def upload_to_sftp2222(self, file_path, server_config):
        """Upload a file to an SFTP server for tenant 2500100 ONLY."""
        transport = paramiko.Transport((server_config["host"], 2222))
        transport.connect(username=server_config["username"], password=server_config["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)

        file_name = os.path.basename(file_path)
        remote_path = f"/POS/25/2500100/{file_name}"  # Change this to your desired remote path
        sftp.put(file_path, remote_path)
        sftp.close()
        transport.close()

    def upload_to_ftp(self, file_path, server_config):
        """Upload a file to an FTP server."""
        ftp = FTP(server_config["host"])
        ftp.login(server_config["username"], server_config["password"])
        ftp.cwd("/")  # Change this to your desired remote directory

        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as file:
            ftp.storbinary(f"STOR {file_name}", file)
        ftp.quit()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileUploaderApp(root)
    root.mainloop()
