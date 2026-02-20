from email import parser
from operator import index
import queue
import customtkinter as ctk
from tkinter import Image, filedialog, messagebox
import pandas as pd
import os
import threading
from PIL import Image

# -----------------------------
# IMPORT YOUR PARSERS HERE
# -----------------------------
from engine_electricity import parse_electricity_pdf
from engine_mobile import parse_mobile_pdf


class BillParserApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        
        self.progress_queue = queue.Queue()
        #self.configure(fg_color="#05192F")   # light grey corporate background
        self.configure(fg_color="#042345")
        
        self.title("Bill Buddy - Billing Automation Tool")
        self.geometry("650x500")
        self.generated_output_path = None

        self.after(100, lambda: self.state('zoomed'))


        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        # VARIABLES
        self.bill_type = ctk.StringVar(value="electricity")
        self.pdf_folder = ""
        self.site_file = ""
        self.output_file = ""
     
        self.create_widgets()
        self.after(100, self.check_progress_queue)

    def check_progress_queue(self):
        try:
            while True:
                percent, message = self.progress_queue.get_nowait()

                self.progress_bar.set(percent / 100)
                self.progress_label.configure(text=f"{int(percent)}%")

                if message:
                    self.status_label.configure(text=message)

        except queue.Empty:
            pass

        self.after(100, self.check_progress_queue)

    def start_parsing(self):

        # Clear old queue values
        while not self.progress_queue.empty():
            self.progress_queue.get()

        # Reset UI
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        self.status_label.configure(text="")

        self.progress_bar.pack(pady=10, fill="x", padx=40)

        thread = threading.Thread(target=self.run_parsing, daemon=True)
        thread.start()

    def create_widgets(self):

        # Title
        title = ctk.CTkLabel(self, text="Bill Buddy", font=("Arial", 36, "bold"),text_color="#E2EDF9")
        title.pack(pady=15)

        self.title_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        self.label_font = ctk.CTkFont(family="Segoe UI", size=20)
        self.button_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")


        # -----------------------------
        # BILL TYPE
        # -----------------------------
        frame_type = ctk.CTkFrame(self)
        frame_type.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(frame_type, text="Select Bill Type:", font=self.label_font).pack(anchor="w", padx=10, pady=5)

        ctk.CTkRadioButton(frame_type, text="Electricity Bills", variable=self.bill_type, value="electricity", font=self.label_font, fg_color="#05192F").pack(anchor="w", padx=20)
        ctk.CTkRadioButton(frame_type, text="Mobile Bills", variable=self.bill_type, value="mobile", font=self.label_font, fg_color="#05192F").pack(anchor="w", padx=20)

        # -----------------------------
        # PDF FOLDER
        # -----------------------------
        frame_pdf = ctk.CTkFrame(self)
        frame_pdf.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(frame_pdf, text="Select PDF Folder:", font=self.label_font).pack(anchor="w", padx=10, pady=5)
        ctk.CTkButton(frame_pdf, text="Browse", command=self.select_pdf_folder, font=self.button_font, fg_color="#042345").pack(anchor="w", padx=20)

        # FIX: Dedicated label for PDF folder
        self.pdf_label = ctk.CTkLabel(frame_pdf, text="No folder selected", font=self.label_font)
        self.pdf_label.pack(anchor="w", padx=20, pady=5)

        # -----------------------------
        # SITE ID FILE
        # -----------------------------
        frame_site = ctk.CTkFrame(self)
        frame_site.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(frame_site, text="Select Site ID Mapping File:", font=self.label_font).pack(anchor="w", padx=10, pady=5)
        ctk.CTkButton(frame_site, text="Browse", command=self.select_site_file, font=self.button_font, fg_color="#042345").pack(anchor="w", padx=20)

        # FIX: Dedicated label for site file
        self.site_label = ctk.CTkLabel(frame_site, text="No file selected", font=self.label_font)
        self.site_label.pack(anchor="w", padx=20, pady=5)

        # -----------------------------
        # OUTPUT FILE
        # -----------------------------
        #frame_output = ctk.CTkFrame(self)
        #frame_output.pack(pady=10, fill="x", padx=20)

        #ctk.CTkLabel(frame_output, text="Select Output Excel File:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        #ctk.CTkButton(frame_output, text="Browse", command=self.select_output_file).pack(anchor="w", padx=20)

        # FIX: Dedicated label for output file
        #self.output_label = ctk.CTkLabel(frame_output, text="No output file selected", font=("Arial", 12))
        #self.output_label.pack(anchor="w", padx=20, pady=5)

        # -----------------------------
        # RUN BUTTON
        # -----------------------------
        #ctk.CTkButton(self, text="Process Bills", font=self.button_font, fg_color="#14324F", command=lambda: threading.Thread(target=self.run_parsing).start()).pack(pady=10)

        self.process_button =  ctk.CTkButton(self, text="Process Bills", font=self.button_font, fg_color="#14324F", command=self.start_parsing)
        self.process_button.pack(pady=10)

        self.view_button = ctk.CTkButton(self, text="View Generated File", font=self.button_font, fg_color="#14324F", command=self.open_output_file, state="disabled")
        self.view_button.pack(pady=10)

        # -----------------------------
        # PROGRESS BAR
        # -----------------------------
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, fill="x", padx=40)
        self.progress_bar.pack_forget()   # hide initially

        self.progress_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 14), text_color="#E2EDF9")
        self.progress_label.pack()


        # Do NOT pack here — keep it hidden initially
        
        # -----------------------------
        # STATUS LABEL (ONLY FOR PROGRESS)
        # -----------------------------
        self.status_label = ctk.CTkLabel(self, text="", font=self.label_font, text_color="#E2EDF9")
        self.status_label.pack(pady=10)

        # Bottom-right branding frame
        self.brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.brand_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # Logo (optional)
        #self.logo_image = ctk.CTkImage(light_image=Image.open("logo.png"), size=(24, 24))
        #self.logo_label = ctk.CTkLabel(self.brand_frame, image=self.logo_image, text="")
        #self.logo_label.pack(side="left", padx=(0,5))

        self.brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.brand_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.logo_image = ctk.CTkImage(
            light_image=Image.open("logo2.png"),
            dark_image=Image.open("logo2.png"),
            size=(24, 24)
        )

        self.logo_label = ctk.CTkLabel(self.brand_frame, image=self.logo_image, text="")
        self.logo_label.pack(side="left", padx=(0,5))

        self.dev_label = ctk.CTkLabel(
            self.brand_frame,
            text="Developed by Svasha IT Solutions",
            font=("Segoe UI", 12),
            text_color="#959494"
        )
        self.dev_label.pack(side="left")


        

    # -----------------------------
    # FILE DIALOG FUNCTIONS
    # -----------------------------
    def select_pdf_folder(self):
        bill_type = self.bill_type.get()

        # -------------------------
        # ELECTRICITY → SELECT FOLDER
        # -------------------------
        if bill_type == "electricity":
            folder = filedialog.askdirectory(
                title="Select Folder Containing Electricity PDFs"
            )
            if folder:
                self.pdf_folder = folder
                self.single_pdf_file = None
                self.pdf_label.configure(text=f"Folder selected: {folder}")
            return  # IMPORTANT: stop here

        # -------------------------
        # MOBILE → SELECT SINGLE PDF
        # -------------------------
        file_path = filedialog.askopenfilename(
            title="Select Mobile Bill PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.single_pdf_file = file_path
            self.pdf_folder = os.path.dirname(file_path)
            self.pdf_label.configure(text=f"Selected file: {file_path}")


    def select_site_file(self):
        self.site_file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")])
        if self.site_file:
            self.site_label.configure(text=self.site_file)

    def select_output_file(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if self.output_file:
            self.output_label.configure(text=self.output_file)

    def open_output_file(self):
        if self.generated_output_path and os.path.exists(self.generated_output_path):
            os.startfile(self.generated_output_path)  # Windows only
        else:
            messagebox.showerror("Error", "Output file not found.")

    
    # -----------------------------
    # MAIN PARSING LOGIC
    # -----------------------------
    def run_parsing(self):

        print("DEBUG: run_parsing started")

        self.process_button.configure(state="disabled")
        
        if not self.pdf_folder or not self.site_file :
            messagebox.showerror("Error", "Please select all required files.")
            return

        rows = []

        # Select parser
        #parser = parse_electricity_pdf if self.bill_type.get() == "electricity" else parse_mobile_pdf


        #pdf_files = [f for f in os.listdir(self.pdf_folder) if f.lower().endswith(".pdf")]
        #if self.single_pdf_file:
        #    # Mobile: single PDF file
        #    pdf_files = [os.path.basename(self.single_pdf_file)]
        #else:
        #    # Electricity: folder of PDFs
        #    pdf_files = [f for f in os.listdir(self.pdf_folder) if f.lower().endswith(".pdf")]

        # Determine which PDFs to process
        if self.bill_type.get() == "mobile" and hasattr(self, "single_pdf_file") and self.single_pdf_file:
            # Mobile → only one file
            print(f"DEBUG: Processing Mobile file")
            pdf_files = [os.path.basename(self.single_pdf_file)]
        else:
            # Electricity → all PDFs in folder
            print(f"DEBUG: Processing Electricity folder")
            pdf_files = [f for f in os.listdir(self.pdf_folder) if f.lower().endswith(".pdf")]

        total_files = len(pdf_files)

        if total_files == 0:
            messagebox.showerror("Error", "No PDF files found in the selected folder.")
            return

        for index, filename in enumerate(pdf_files, start=1):
            print(f"DEBUG: Processing file: {filename}")
            pdf_path = os.path.join(self.pdf_folder, filename)
            
            #progress = (index / total_files) * 100
            base_progress = ((index - 1) / total_files) * 100

            try:
                # Select parser based on bill type
                if self.bill_type.get() == "mobile":
                    def mobile_progress_callback(internal_percent):
                        # Combine file-level + internal-level progress
                        combined_progress = base_progress + (internal_percent / total_files)
                        self.progress_queue.put((
                            combined_progress,
                            f"Processing {filename}..."
                        ))

                    data = parse_mobile_pdf(
                        pdf_path,
                        mapping_path=self.site_file,
                        ui_callback=mobile_progress_callback
                    )
                else:
                    data = parse_electricity_pdf(pdf_path)
                    file_progress = (index / total_files) * 100
                    self.progress_queue.put((
                        file_progress,
                        f"Processing {filename}..."))

                print("DEBUG: parser returned:", type(data),
                "length:", len(data) if isinstance(data, list) else "single")

                # Append rows safely
                if isinstance(data, list):
                    for row in data:
                        row["source_file"] = filename
                        rows.append(row)
                else:
                    data["source_file"] = filename
                    rows.append(data)

            except Exception as e:
                print("ERROR while parsing:", e)
                continue

        df_output = pd.DataFrame(rows)

        progress = index / total_files
        self.progress_bar.set(progress)
        self.update_idletasks()
        
        #**********************************************
        ## Load site mapping
        if self.site_file.endswith(".xlsx"):
            df_site = pd.read_excel(self.site_file)
        else:
            df_site = pd.read_csv(self.site_file)

        # FIX: Convert both account_no columns to string BEFORE merging

        if self.bill_type.get() == "electricity":
            merge_key = "account_no"
        else:
            merge_key = "subscriber_no"

        # -----------------------------
        # VALIDATION 1: Mapping file must contain merge key
        # -----------------------------
        if merge_key not in df_site.columns:
            messagebox.showerror(
                "Invalid Mapping File",
                f"The selected site mapping file does not contain the required column: '{merge_key}'.")
            return

        # -----------------------------
        # VALIDATION 2: Parsed output must contain merge key
        # -----------------------------
        if merge_key not in df_output.columns:
            messagebox.showerror(
                "Parsing Error",
                f"The parsed data does not contain the required field '{merge_key}'. "
                "Please verify the PDF format."
            )
            return
    
        df_output[merge_key] = df_output[merge_key].astype(str).str.strip()
        df_site[merge_key] = df_site[merge_key].astype(str).str.strip()

        # Merge
        df_final = df_output.merge(df_site, on=merge_key, how="left")

        if "site_id_x" in df_final.columns and "site_id_y" in df_final.columns:
            df_final = df_final.drop(columns=["site_id_x"])
            df_final = df_final.rename(columns={"site_id_y": "site_id"})
        
        missing_count = df_final["site_id"].isna().sum() if "site_id" in df_final.columns else 0

        #if missing_count > 0:
        #    messagebox.showwarning(
        #    "Missing Site IDs",
        #    f"{missing_count} rows could not be mapped to a site_id. "
        #    "Please verify the mapping file.")
        
        #**********************************************
        #df_final = df_output  # No mapping applied yet
        # Save
        import datetime

        # Auto-generate output filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        bill_type = self.bill_type.get()
        output_filename = f"{bill_type}_output_{timestamp}.xlsx"
        output_path = os.path.join(self.pdf_folder, output_filename)

        df_final.to_excel(output_path, index=False)

        #messagebox.showinfo("Success", f"Parsing completed successfully.\n\nOutput saved to:\n{output_path}")
        self.after(0, lambda: messagebox.showinfo("Success", f"Process completed successfully.\n\nOutput saved to:\n{output_path}"))

        self.generated_output_path = output_path
        self.view_button.configure(state="normal")

        # Hide progress bar after completion
        #self.progress_bar.pack_forget()
        self.progress_bar.pack_forget()
        self.progress_bar.set(1)
        #self.progress_label.configure(text="")

        self.after(0, lambda: self.status_label.configure(text="Process Complete!"))
        self.after(5000, lambda: self.status_label.configure(text=""))
        self.after(0, lambda: self.progress_label.configure(text=""))
        self.after(0, lambda: self.process_button.configure(state="normal"))
        
        self.update_idletasks()
        

if __name__ == "__main__":
    app = BillParserApp()
    app.mainloop()