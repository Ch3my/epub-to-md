#!/usr/bin/env python3
"""
EPUB to Markdown Converter - GUI Version
Converts EPUB files to clean Markdown format with a graphical interface
"""

import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

# Import converter functions from shared module
from epub_converter import convert_epub_to_md


class EPUBConverterGUI:
    """GUI Application for EPUB to Markdown conversion"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB to Markdown Converter")
        self.root.geometry("700x620")
        self.root.minsize(500, 500)
        
        # Variables
        self.epub_files = []
        self.output_folder = tk.StringVar(value="")
        self.use_source_folder = tk.BooleanVar(value=True)
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="EPUB to Markdown Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(1, weight=1)
        
        # Select files button
        select_btn = ttk.Button(file_frame, text="Select EPUB Files", 
                               command=self.select_files)
        select_btn.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # File list
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.file_listbox = tk.Listbox(list_frame, height=8, 
                                       yscrollcommand=scrollbar.set)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.file_listbox.yview)
        
        # Clear button
        clear_btn = ttk.Button(file_frame, text="Clear List", 
                              command=self.clear_files)
        clear_btn.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # Output folder section
        output_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        # Use source folder checkbox
        source_check = ttk.Checkbutton(output_frame, 
                                      text="Save to source folder (same location as EPUB files)",
                                      variable=self.use_source_folder,
                                      command=self.toggle_output_folder)
        source_check.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Output folder selection
        ttk.Label(output_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_folder, 
                                state='disabled')
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.output_btn = ttk.Button(output_frame, text="Browse", 
                                    command=self.select_output_folder,
                                    state='disabled')
        self.output_btn.grid(row=1, column=2, sticky=tk.W)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready to convert")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert Files",
                                     command=self.start_conversion,
                                     style='Accent.TButton')
        self.convert_btn.grid(row=5, column=0, columnspan=3, pady=(10, 10))
        
        # Configure button style
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
    def select_files(self):
        """Open file dialog to select EPUB files"""
        files = filedialog.askopenfilenames(
            title="Select EPUB Files",
            filetypes=[("EPUB files", "*.epub"), ("All files", "*.*")]
        )
        
        if files:
            self.epub_files.extend(files)
            # Remove duplicates
            self.epub_files = list(set(self.epub_files))
            self.update_file_list()
            self.log(f"Added {len(files)} file(s)")
            
    def clear_files(self):
        """Clear the file list"""
        self.epub_files = []
        self.update_file_list()
        self.log("File list cleared")
        
    def update_file_list(self):
        """Update the listbox with current files"""
        self.file_listbox.delete(0, tk.END)
        for file in self.epub_files:
            filename = os.path.basename(file)
            self.file_listbox.insert(tk.END, filename)
            
    def toggle_output_folder(self):
        """Enable/disable output folder selection"""
        if self.use_source_folder.get():
            self.output_btn.config(state='disabled')
            self.output_folder.set("")
        else:
            self.output_btn.config(state='normal')
            
    def select_output_folder(self):
        """Open folder dialog to select output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            self.log(f"Output folder: {folder}")
            
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if not self.epub_files:
            messagebox.showwarning("No Files", "Please select EPUB files to convert")
            return
            
        if not self.use_source_folder.get() and not self.output_folder.get():
            messagebox.showwarning("No Output Folder", 
                                 "Please select an output folder or use source folder option")
            return
        
        # Disable convert button during conversion
        self.convert_btn.config(state='disabled')
        
        # Start conversion in thread
        thread = threading.Thread(target=self.convert_files, daemon=True)
        thread.start()
        
    def convert_files(self):
        """Convert all selected files"""
        total = len(self.epub_files)
        success_count = 0
        failed_files = []
        
        self.progress['maximum'] = total
        self.progress['value'] = 0
        
        self.log(f"\n{'='*60}")
        self.log(f"Starting conversion of {total} file(s)...")
        self.log(f"{'='*60}\n")
        
        for i, epub_file in enumerate(self.epub_files, 1):
            filename = os.path.basename(epub_file)
            self.status_label.config(text=f"Converting {i}/{total}: {filename}")
            self.log(f"[{i}/{total}] Processing: {filename}")
            
            try:
                # Determine output path
                if self.use_source_folder.get():
                    output_path = Path(epub_file).with_suffix('.md')
                else:
                    output_dir = Path(self.output_folder.get())
                    output_path = output_dir / Path(epub_file).with_suffix('.md').name
                
                # Convert file
                result_path, char_count = convert_epub_to_md(epub_file, str(output_path))
                
                self.log(f"  ✓ Success: {output_path.name}")
                self.log(f"    Size: {char_count:,} characters\n")
                success_count += 1
                
            except Exception as e:
                self.log(f"  ✗ Failed: {str(e)}\n")
                failed_files.append(filename)
            
            self.progress['value'] = i
            self.root.update_idletasks()
        
        # Summary
        self.log(f"{'='*60}")
        self.log(f"Conversion Complete!")
        self.log(f"  Successfully converted: {success_count}/{total}")
        self.log(f"  Failed: {len(failed_files)}/{total}")
        
        if failed_files:
            self.log(f"\nFailed files:")
            for file in failed_files:
                self.log(f"  - {file}")
        
        self.log(f"{'='*60}\n")
        
        # Update status
        self.status_label.config(text=f"Complete: {success_count} converted, {len(failed_files)} failed")
        
        # Re-enable convert button
        self.convert_btn.config(state='normal')
        
        # Show completion message
        if failed_files:
            messagebox.showinfo("Conversion Complete", 
                              f"Converted {success_count} of {total} files.\n{len(failed_files)} failed.")
        else:
            messagebox.showinfo("Conversion Complete", 
                              f"Successfully converted all {total} files!")


def main():
    root = tk.Tk()
    app = EPUBConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
