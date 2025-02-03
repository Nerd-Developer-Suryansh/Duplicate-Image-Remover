import os
import hashlib
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import threading
from tkinter import ttk

# Setup logging for better tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def calculate_image_hash(image_path):
    """Calculate the hash of an image."""
    try:
        with Image.open(image_path) as img:
            img = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')  # Convert to grayscale
            pixels = list(img.getdata())
            avg_pixel = sum(pixels) / len(pixels)
            bits = ''.join(['1' if pixel > avg_pixel else '0' for pixel in pixels])
            hex_representation = '{:016x}'.format(int(bits, 2))
            return hex_representation
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
        return None

def remove_duplicate_images(directory, recursive=False):
    """Remove duplicate images in the specified directory and optionally its subdirectories."""
    image_hashes = {}
    duplicates = []
    # Check if the directory exists
    if not os.path.exists(directory):
        logging.error(f"The directory {directory} does not exist.")
        return duplicates

    # Walk through the directory (and subdirectories if recursive is True)
    for root, dirs, files in os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]:
        for filename in files:
            if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                image_path = os.path.join(root, filename)
                image_hash = calculate_image_hash(image_path)

                # Skip if the hash could not be generated
                if image_hash is None:
                    continue

                # Check for duplicates based on hash
                if image_hash in image_hashes:
                    duplicates.append(image_path)  # Found duplicate image
                else:
                    image_hashes[image_hash] = image_path
    return duplicates

def select_directory():
    """Open a file dialog to select a directory."""
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)

def detect_duplicates_thread():
    """Run detect duplicates in a separate thread."""
    detect_button.config(state=tk.DISABLED)  # Disable the detect button while processing
    directory = directory_entry.get()
    if not os.path.exists(directory):
        messagebox.showerror("Error", "Directory does not exist!")
        detect_button.config(state=tk.NORMAL)
        return

    status_label.config(text="Detecting duplicates...")
    
    # Run duplicate detection in a separate thread
    duplicates_thread = threading.Thread(target=detect_duplicates, args=(directory,))
    duplicates_thread.start()

def detect_duplicates(directory):
    """Detect duplicate images and show them in the listbox."""
    duplicates = remove_duplicate_images(directory)
    
    if duplicates:
        duplicates_listbox.delete(0, tk.END)  # Clear any previous entries
        for duplicate in duplicates:
            duplicates_listbox.insert(tk.END, duplicate)
        status_label.config(text=f"{len(duplicates)} duplicates found.")
    else:
        messagebox.showinfo("No Duplicates", "No duplicates found.")
        status_label.config(text="No duplicates found.")
    
    detect_button.config(state=tk.NORMAL)  # Enable the detect button after processing

def remove_selected_duplicates():
    """Remove selected duplicate images."""
    selected_items = duplicates_listbox.curselection()
    if not selected_items:
        messagebox.showerror("Error", "No image selected for removal.")
        return

    for index in selected_items:
        image_path = duplicates_listbox.get(index)
        try:
            os.remove(image_path)
            duplicates_listbox.delete(index)  # Remove from listbox
            logging.info(f"Removed duplicate: {image_path}")
        except Exception as e:
            logging.error(f"Error removing {image_path}: {e}")
            messagebox.showerror("Error", f"Failed to remove {image_path}")

    status_label.config(text="Selected duplicates removed.")

def apply_green_theme():
    """Apply the Green theme to the entire app."""
    root.config(bg="#e8f5e9")
    directory_label.config(bg="#e8f5e9", fg="black")
    directory_entry.config(bg="white", fg="black", bd=2, font=("Helvetica", 12), relief="flat")
    browse_button.config(style="Green.TButton")
    detect_button.config(style="Green.TButton")
    remove_button.config(style="Green.TButton")
    status_label.config(bg="#e8f5e9", fg="black", font=("Helvetica", 10))
    listbox_frame.config(bg="#e8f5e9")
    duplicates_listbox.config(bg="white", fg="black")
    inventor_label.config(bg="#e8f5e9", fg="black")  # Set the inventor label color

# Set up the main window using tkinter
root = tk.Tk()
root.title("Duplicate Image Finder")
root.geometry("650x600")

# Initialize the style
style = ttk.Style()

# Define a new style for Green buttons with a light hover effect
style.configure("Green.TButton", 
                background="#388e3c", 
                foreground="black", 
                font=("Helvetica", 12, "bold"), 
                relief="flat")
style.map("Green.TButton", 
          background=[("active", "#66bb6a")],  # Lighter green on hover
          foreground=[("active", "black")])  # Black text on hover

# Custom font and colors
font = ("Helvetica", 12)
button_font = ("Helvetica", 12, "bold")

# Directory selection
directory_label = tk.Label(root, text="Select Directory:", font=font)
directory_label.pack(pady=15)

directory_entry = tk.Entry(root, font=font, width=55, bd=2)
directory_entry.pack(pady=5)

browse_button = ttk.Button(root, text="Browse", command=select_directory, style="Green.TButton")
browse_button.pack(pady=10)

# Buttons for detecting and removing duplicates
detect_button = ttk.Button(root, text="Detect Duplicates", command=detect_duplicates_thread, style="Green.TButton")
detect_button.pack(pady=15)

remove_button = ttk.Button(root, text="Remove Selected Duplicates", command=remove_selected_duplicates, style="Green.TButton")
remove_button.pack(pady=10)

# Scrollable Listbox to display duplicates
listbox_frame = tk.Frame(root)
listbox_frame.pack(pady=15)

scrollbar = tk.Scrollbar(listbox_frame)
duplicates_listbox = tk.Listbox(listbox_frame, width=80, height=12, font=font, selectmode=tk.SINGLE, bd=2, yscrollcommand=scrollbar.set)
scrollbar.config(command=duplicates_listbox.yview)
duplicates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Status label
status_label = tk.Label(root, text="Select a directory and click 'Detect Duplicates'.", font=("Helvetica", 12))
status_label.pack(pady=15)

# Inventor's name
inventor_label = tk.Label(root, text="Invented by: Suryansh Niranjan", font=("Helvetica", 12, "italic"))
inventor_label.pack(pady=20)

# Apply the Green theme after widget creation
apply_green_theme()

# Start the GUI loop
root.mainloop()
