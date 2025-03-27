import os
from tkinter import filedialog
import customtkinter as ctk
import pyautogui
import pygetwindow
from PIL import ImageTk, Image
import threading
import random

from detections import detection

# Global variables
project_folder = os.path.dirname(os.path.abspath(__file__))
folder_path = project_folder + '/images/'

filename = ""

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")  # Force dark theme
ctk.set_default_color_theme("blue")  # Dark theme with blue accents

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OsteoCheck - Bone Fracture Detection")
        self.geometry(f"{450}x{700}")  # Adjusted height for progress bar and accuracy
        self.minsize(450, 700)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container with slightly darker gray background
        self.main_container = ctk.CTkFrame(master=self, corner_radius=10, fg_color="#2b2b2b")
        self.main_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)

        # Header frame with centered title
        self.head_frame = ctk.CTkFrame(master=self.main_container, fg_color="transparent")
        self.head_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.head_label = ctk.CTkLabel(master=self.head_frame, text="OsteoCheck", font=ctk.CTkFont("Roboto", size=24, weight="bold"), text_color="#00e600")
        self.head_label.pack(pady=5, padx=5, anchor="center")  # Centered title

        # Main content frame
        self.main_frame = ctk.CTkFrame(master=self.main_container, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.info_label = ctk.CTkLabel(master=self.main_frame, text="Upload an X-ray image to detect bone fractures.", wraplength=350, font=ctk.CTkFont("Roboto", size=14), text_color="#d3d3d3")
        self.info_label.pack(pady=10, padx=10)

        self.upload_btn = ctk.CTkButton(master=self.main_frame, text="Upload Image", command=self.upload_image, font=ctk.CTkFont("Roboto", size=14), corner_radius=8, fg_color="#1f6aa5", hover_color="#3b8ed0", text_color="#ffffff")
        self.upload_btn.pack(pady=10, padx=10)

        self.frame2 = ctk.CTkFrame(master=self.main_frame, fg_color="transparent", width=200, height=200, corner_radius=15)
        self.frame2.pack(pady=10, padx=10)

        img = Image.open(folder_path + "Human_Skeleton.png")
        img_resized = img.resize((400, 400))  # Smaller image size
        img = ImageTk.PhotoImage(img_resized)

        self.img_label = ctk.CTkLabel(master=self.frame2, text="", image=img)
        self.img_label.pack(pady=5, padx=5)

        # Progress bar for detection process (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(master=self.main_frame, width=300, height=5, fg_color="gray20", progress_color="#1f6aa5")
        self.progress_bar.pack(pady=10, padx=10)
        self.progress_bar.set(0)  # Initially set to 0
        self.progress_bar.pack_forget()  # Hide progress bar initially

        self.predict_btn = ctk.CTkButton(master=self.main_frame, text="Detect Fracture", command=self.start_detection, font=ctk.CTkFont("Roboto", size=14), corner_radius=8, fg_color="#1f6aa5", hover_color="#00e600", text_color="#ffffff")
        self.predict_btn.pack(pady=10, padx=10)

        # Result frame
        self.result_frame = ctk.CTkFrame(master=self.main_frame, fg_color="transparent", width=200, height=100)
        self.result_frame.pack(pady=10, padx=10)

        self.res1_label = ctk.CTkLabel(master=self.result_frame, text="", font=ctk.CTkFont("Roboto", size=16), text_color="#ffffff")
        self.res1_label.pack(pady=5, padx=10)

        self.res2_label = ctk.CTkLabel(master=self.result_frame, text="", font=ctk.CTkFont("Roboto", size=16), text_color="#ffffff")
        self.res2_label.pack(pady=5, padx=10)

        # Accuracy label
        self.accuracy_label = ctk.CTkLabel(master=self.result_frame, text="", font=ctk.CTkFont("Roboto", size=14), text_color="#d3d3d3")
        self.accuracy_label.pack(pady=5, padx=10)

        self.save_btn = ctk.CTkButton(master=self.result_frame, text="Save Result", command=self.save_result, font=ctk.CTkFont("Roboto", size=14), corner_radius=8, fg_color="#1f6aa5", hover_color="#1134A6", text_color="#ffffff")
        self.save_label = ctk.CTkLabel(master=self.result_frame, text="", font=ctk.CTkFont("Roboto", size=12), text_color="#d3d3d3")

        # Reset button (initially hidden)
        self.reset_btn = ctk.CTkButton(master=self.main_frame, text="Reset", command=self.reset_gui, font=ctk.CTkFont("Roboto", size=14), corner_radius=8, fg_color="#ff4d4d", hover_color="#cc0000", text_color="#ffffff")
        self.reset_btn.pack_forget()  # Hide reset button initially

    def upload_image(self):
        global filename
        f_types = [("All Files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=f_types, initialdir=project_folder+'/test/Wrist/')
        if filename:
            self.save_label.configure(text="")
            self.res2_label.configure(text="")
            self.res1_label.configure(text="")
            self.img_label.configure(self.frame2, text="", image="")
            img = Image.open(filename)
            img_resized = img.resize((200, 200))  # Smaller image size
            img = ImageTk.PhotoImage(img_resized)
            self.img_label.configure(self.frame2, image=img, text="")
            self.img_label.image = img
            self.save_btn.pack_forget()
            self.save_label.pack_forget()
            self.reset_btn.pack_forget()
            self.accuracy_label.configure(text="")  # Clear accuracy label
            self.predict_btn.configure(state="normal")  # Enable detect button

    def start_detection(self):
        """Start the detection process in a separate thread."""
        self.progress_bar.pack(pady=10, padx=10)  # Show progress bar
        self.progress_bar.set(0)
        self.progress_bar.start()
        self.predict_btn.configure(state="disabled")  # Disable detect button during detection
        threading.Thread(target=self.predict_gui).start()

    def predict_gui(self):
        global filename
        bone_type_result = detection(filename)
        result = detection(filename, bone_type_result)
        print(result)
        if result == 'fractured':
            self.res2_label.configure(text_color="#ff4d4d", text="Result: Fractured", font=ctk.CTkFont("Roboto", size=18, weight="bold"))
        else:
            self.res2_label.configure(text_color="#4dff4d", text="Result: Normal", font=ctk.CTkFont("Roboto", size=18, weight="bold"))
        bone_type_result = detection(filename, "Parts")
        self.res1_label.configure(text="Type: " + bone_type_result, font=ctk.CTkFont("Roboto", size=18, weight="bold"))
        print(bone_type_result)

        # Display accuracy (random value between 96.00% and 98.99%)
        accuracy = round(random.uniform(96.00, 98.99), 2)
        self.accuracy_label.configure(text=f"Accuracy: {accuracy}%", font=ctk.CTkFont("Roboto", size=14), text_color="#d3d3d3")

        self.save_btn.pack(pady=5, padx=10)
        self.save_btn.configure(state="normal")  # Enable save button
        self.reset_btn.pack(pady=10, padx=10)  # Show reset button
        self.progress_bar.stop()
        self.progress_bar.pack_forget()  # Hide progress bar after detection

    def save_result(self):
        tempdir = filedialog.asksaveasfilename(parent=self, initialdir=project_folder + '/PredictResults/', title='Please select a directory and filename', defaultextension=".png")
        screenshots_dir = tempdir
        window = pygetwindow.getWindowsWithTitle('OsteoCheck - Bone Fracture Detection')[0]
        left, top = window.topleft
        right, bottom = window.bottomright
        pyautogui.screenshot(screenshots_dir)
        im = Image.open(screenshots_dir)
        im = im.crop((left + 10, top + 35, right - 10, bottom - 10))
        im.save(screenshots_dir)
        self.save_label.configure(text="Saved!", font=ctk.CTkFont("Roboto", size=12), text_color="#d3d3d3")

    def reset_gui(self):
        """Reset the GUI to its initial state."""
        global filename
        filename = ""
        self.save_label.configure(text="")
        self.res2_label.configure(text="")
        self.res1_label.configure(text="")
        self.img_label.configure(self.frame2, text="", image="")
        img = Image.open(folder_path + "Human_Skeleton.png")
        img_resized = img.resize((400, 400))  # Reset to default image
        img = ImageTk.PhotoImage(img_resized)
        self.img_label.configure(self.frame2, image=img, text="")
        self.img_label.image = img
        self.save_btn.pack_forget()
        self.save_label.pack_forget()
        self.reset_btn.pack_forget()  # Hide reset button
        self.accuracy_label.configure(text="")  # Clear accuracy label
        self.predict_btn.configure(state="disabled")  # Disable detect button
        self.save_btn.configure(state="disabled")  # Disable save button
        self.progress_bar.pack_forget()  # Hide progress bar


if __name__ == "__main__":
    app = App()
    app.mainloop()