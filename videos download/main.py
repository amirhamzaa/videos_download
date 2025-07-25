# main.py
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import threading
import subprocess
import os
import sys

# --- Core Application Class ---
class VideoDownloaderApp:
    """
    A simple GUI application to download videos from various websites
    using the yt-dlp command-line tool.
    """

    def __init__(self, root):
        """
        Initializes the main application window and its widgets.
        """
        self.root = root
        self.root.title("Simple Video Downloader By Amir Hamza")
        self.root.geometry("600x450") # Increased height for new elements
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # --- Member variables ---
        self.download_path = tk.StringVar()
        self.download_path.set(os.path.expanduser("~"))
        self.high_quality = tk.BooleanVar(value=True) # Variable for quality checkbox
        self.is_downloading = False

        # --- UI Components ---
        self.create_widgets()

    def create_widgets(self):
        """
        Creates and arranges all the UI widgets in the main window.
        """
        # --- Main Frame ---
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- URL Input ---
        url_label = tk.Label(main_frame, text="Video URL:", font=("Helvetica", 12), bg="#f0f0f0")
        url_label.pack(anchor="w")

        self.url_entry = tk.Entry(main_frame, font=("Helvetica", 12), width=50, relief=tk.SOLID, borderwidth=1)
        self.url_entry.pack(pady=5, fill=tk.X)
        self.url_entry.focus()

        # --- Download Path Selection ---
        path_label = tk.Label(main_frame, text="Save to:", font=("Helvetica", 12), bg="#f0f0f0")
        path_label.pack(anchor="w", pady=(10, 0))

        path_frame = tk.Frame(main_frame, bg="#f0f0f0")
        path_frame.pack(fill=tk.X)

        self.path_entry = tk.Entry(path_frame, textvariable=self.download_path, font=("Helvetica", 10), state="readonly", width=40)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        browse_button = tk.Button(path_frame, text="Browse...", command=self.browse_directory,
                                  font=("Helvetica", 10), bg="#dcdcdc", relief=tk.FLAT)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        # --- Quality Selection Checkbox ---
        quality_check = tk.Checkbutton(main_frame, text="Download Best Quality ",
                                       variable=self.high_quality, bg="#f0f0f0", font=("Helvetica", 10),
                                       anchor="w", justify=tk.LEFT)
        quality_check.pack(fill=tk.X, pady=5)

        # --- Download Button ---
        self.download_button = tk.Button(main_frame, text="Download Video", command=self.start_download_thread,
                                         font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white",
                                         relief=tk.FLAT, pady=10, cursor="hand2")
        self.download_button.pack(pady=10, fill=tk.X)

        # --- Status Display ---
        status_label = tk.Label(main_frame, text="Status:", font=("Helvetica", 12), bg="#f0f0f0")
        status_label.pack(anchor="w", pady=(5, 0))
        
        self.status_text = tk.Text(main_frame, height=6, font=("Courier", 10), state="disabled",
                                   relief=tk.SOLID, borderwidth=1, bg="#ffffff")
        self.status_text.pack(fill=tk.BOTH, expand=True)

    def browse_directory(self):
        """
        Opens a dialog to let the user select a download directory.
        """
        if self.is_downloading: return
        path = filedialog.askdirectory(title="Select a Folder to Save the Video")
        if path:
            self.download_path.set(path)

    def update_status(self, message):
        """
        Updates the status text box with a new message.
        Ensures UI updates are done in the main thread.
        """
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END) # Auto-scroll to the bottom
        self.status_text.config(state="disabled")

    def set_ui_state(self, is_downloading):
        """Enable or disable UI elements during download."""
        self.is_downloading = is_downloading
        state = tk.DISABLED if is_downloading else tk.NORMAL
        button_text = "Downloading..." if is_downloading else "Download Video"
        button_bg = "#E57373" if is_downloading else "#4CAF50"

        self.url_entry.config(state=state)
        self.download_button.config(text=button_text, state=state, bg=button_bg)
        # Keep browse button and checkbox active, or disable them:
        # for child in self.root.winfo_children():
        #     if isinstance(child, tk.Frame):
        #         for widget in child.winfo_children():
        #             if isinstance(widget, (tk.Button, tk.Checkbutton, tk.Entry)):
        #                 widget.config(state=state)

    def start_download_thread(self):
        """
        Starts the video download process in a separate thread to keep
        the GUI responsive.
        """
        video_url = self.url_entry.get().strip()
        save_path = self.download_path.get()

        if not video_url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        if not save_path:
            messagebox.showerror("Error", "Please select a save location.")
            return
        
        self.set_ui_state(True)
        # Create and start the download thread
        download_thread = threading.Thread(target=self.download_video, args=(video_url, save_path), daemon=True)
        download_thread.start()

    def download_video(self, url, path):
        """
        Handles the actual video download using the yt-dlp library.
        This function is executed in a separate thread.
        """
        try:
            self.update_status(f"Starting download for: {url}")
            self.update_status(f"Saving to: {path}")

            python_executable = sys.executable
            
            command = [
                python_executable,
                "-m",
                "yt_dlp",
            ]

            # Add quality selection arguments if the checkbox is ticked
            if self.high_quality.get():
                self.update_status("High quality selected. This may require FFmpeg.")
                # This format string tells yt-dlp to download the best video and audio and merge them.
                command.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4"])

            # Add the rest of the command for output path and URL
            command.extend([
                "-o",
                os.path.join(path, "%(title)s.%(ext)s"),
                url
            ])
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)

            for line in iter(process.stdout.readline, ''):
                self.update_status(line.strip())
            
            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                self.update_status("\n--- Download completed successfully! ---")
                messagebox.showinfo("Success", "Video downloaded successfully!")
            else:
                error_output = process.stderr.read()
                self.update_status(f"\n--- Download failed ---")
                
                if "ffmpeg or avconv not found" in error_output.lower():
                    self.update_status("ERROR: FFmpeg is required for merging high quality video and audio.")
                    self.update_status("Please install FFmpeg and ensure it's in your system's PATH.")
                    messagebox.showerror("Dependency Error", "FFmpeg was not found.\n\nTo download in best quality, you must install FFmpeg.\n\nYou can download it from ffmpeg.org.")
                elif "is not a valid url" in error_output.lower():
                     messagebox.showerror("Download Failed", f"The URL is not valid or is unsupported.\n\nPlease check the URL and try again.")
                else:
                    self.update_status(f"Error details: {error_output}")
                    messagebox.showerror("Download Failed", f"An error occurred during download.\nCheck the status window for details.")

        except Exception as e:
            self.update_status(f"An unexpected error occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            # Ensure UI is re-enabled even if there's an error
            self.set_ui_state(False)

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
