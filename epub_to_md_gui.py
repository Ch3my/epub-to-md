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
import ctypes
import winreg

# Fix blurry text on Windows by enabling DPI awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except (AttributeError, OSError):
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older Windows
    except (AttributeError, OSError):
        pass

# Import converter functions from shared module
from epub_converter import convert_epub_to_md


def is_system_dark_mode():
    """Check if Windows is using dark mode"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return value == 0  # 0 = dark mode, 1 = light mode
    except (FileNotFoundError, OSError):
        return False  # Default to light mode if we can't read the registry


class EPUBConverterGUI:
    """GUI Application for EPUB to Markdown conversion"""

    # Color schemes
    LIGHT_THEME = {
        'bg': '#f5f5f7',
        'bg_secondary': '#ffffff',
        'accent': '#6366f1',
        'accent_hover': '#4f46e5',
        'primary': '#6366f1',
        'primary_hover': '#4f46e5',
        'text': '#1f2937',
        'text_muted': '#6b7280',
        'success': '#10b981',
        'border': '#e5e7eb',
        'row_alt': '#f0f0f5',
    }

    DARK_THEME = {
        'bg': '#1a1a2e',
        'bg_secondary': '#16213e',
        'accent': '#818cf8',
        'accent_hover': '#6366f1',
        'primary': '#818cf8',
        'primary_hover': '#6366f1',
        'text': '#e2e8f0',
        'text_muted': '#94a3b8',
        'success': '#34d399',
        'border': '#334155',
        'row_alt': '#1e2a4a',
    }

    def __init__(self, root):
        self.root = root
        self.root.title("EPUB → Markdown")
        self.root.geometry("1050x650")
        self.root.minsize(950, 620)

        # Theme state - use system preference
        self.is_dark_mode = is_system_dark_mode()
        self.COLORS = self.DARK_THEME.copy() if self.is_dark_mode else self.LIGHT_THEME.copy()

        self.root.configure(bg=self.COLORS['bg'])

        # Set app icon
        icon_path = Path(__file__).parent / "app_icon.png"
        if icon_path.exists():
            try:
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon_image)
                self._icon = icon_image  # Keep reference to prevent garbage collection
            except tk.TclError:
                pass  # Icon format not supported on this platform

        # Variables
        self.epub_files = []
        self.output_folder = tk.StringVar(value="")
        self.use_source_folder = tk.BooleanVar(value=True)

        # Widget references for theme updates
        self.tk_frames = []
        self.tk_widgets = []

        # Setup styles
        self.setup_styles()

        # Create UI
        self.create_widgets()

    def setup_styles(self):
        """Configure ttk styles for a modern look"""
        style = ttk.Style()

        # Use clam theme as base (works well for customization)
        style.theme_use('clam')

        # Frame styles
        style.configure('TFrame', background=self.COLORS['bg'])
        style.configure('Card.TFrame', background=self.COLORS['bg_secondary'])

        # Label styles
        style.configure('TLabel',
                       background=self.COLORS['bg'],
                       foreground=self.COLORS['text'],
                       font=('Segoe UI', 10))

        style.configure('Title.TLabel',
                       background=self.COLORS['bg'],
                       foreground=self.COLORS['text'],
                       font=('Segoe UI', 24, 'bold'))

        style.configure('Subtitle.TLabel',
                       background=self.COLORS['bg'],
                       foreground=self.COLORS['text_muted'],
                       font=('Segoe UI', 11))

        style.configure('Section.TLabel',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text'],
                       font=('Segoe UI', 11, 'bold'))

        style.configure('Status.TLabel',
                       background=self.COLORS['bg'],
                       foreground=self.COLORS['success'],
                       font=('Segoe UI', 10))

        # Button styles
        style.configure('TButton',
                       background=self.COLORS['accent'],
                       foreground='white',
                       font=('Segoe UI', 10),
                       padding=(15, 8),
                       borderwidth=0)
        style.map('TButton',
                 background=[('active', self.COLORS['accent_hover']),
                           ('disabled', self.COLORS['border'])],
                 foreground=[('disabled', self.COLORS['text_muted'])])

        style.configure('Primary.TButton',
                       background=self.COLORS['primary'],
                       foreground='white',
                       font=('Segoe UI', 12, 'bold'),
                       padding=(30, 12))
        style.map('Primary.TButton',
                 background=[('active', self.COLORS['primary_hover']),
                           ('disabled', '#555555')])

        # Entry style
        style.configure('TEntry',
                       fieldbackground=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text'],
                       insertcolor=self.COLORS['text'],
                       padding=8)

        # Checkbutton style
        style.configure('TCheckbutton',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text'],
                       font=('Segoe UI', 10))
        style.map('TCheckbutton',
                 background=[('active', self.COLORS['bg_secondary'])])

        # Progressbar style
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.COLORS['primary'],
                       troughcolor=self.COLORS['bg_secondary'],
                       borderwidth=0,
                       lightcolor=self.COLORS['primary'],
                       darkcolor=self.COLORS['primary'])

        # LabelFrame style
        style.configure('Card.TLabelframe',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text'],
                       borderwidth=0,
                       relief='flat')
        style.configure('Card.TLabelframe.Label',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text'],
                       font=('Segoe UI', 11, 'bold'))

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=25, pady=20)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1, uniform='cols')
        main_frame.columnconfigure(1, weight=1, uniform='cols')
        main_frame.rowconfigure(2, weight=1)  # Log section expands

        # ===== HEADER SECTION =====
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame,
                               text="EPUB → Markdown",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky='w')

        subtitle_label = ttk.Label(header_frame,
                                  text="Convert your ebooks to clean, readable Markdown",
                                  style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, sticky='w', pady=(5, 0))

        # Theme toggle button
        theme_btn_text = "Light Mode" if self.is_dark_mode else "Dark Mode"
        self.theme_btn = ttk.Button(header_frame, text=theme_btn_text,
                                   command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=1, sticky='e', padx=(10, 0))

        # ===== LEFT COLUMN: INPUT FILES =====
        self.file_card = tk.Frame(main_frame, bg=self.COLORS['bg_secondary'],
                            highlightthickness=1, highlightbackground=self.COLORS['border'])
        self.file_card.grid(row=1, column=0, sticky='nsew', padx=(0, 8), pady=(0, 15))
        self.file_card.columnconfigure(0, weight=1)
        self.file_card.rowconfigure(2, weight=1)

        # Section header
        file_header = ttk.Frame(self.file_card, style='Card.TFrame')
        file_header.grid(row=0, column=0, sticky='ew', padx=15, pady=(15, 10))
        file_header.columnconfigure(0, weight=1)

        ttk.Label(file_header, text="Input Files",
                 style='Section.TLabel').grid(row=0, column=0, sticky='w')

        # Buttons row
        btn_frame = ttk.Frame(self.file_card, style='Card.TFrame')
        btn_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=(0, 10))

        select_btn = ttk.Button(btn_frame, text="+ Add EPUB Files",
                               command=self.select_files)
        select_btn.grid(row=0, column=0, sticky='w', padx=(0, 10))

        clear_btn = ttk.Button(btn_frame, text="Clear All",
                              command=self.clear_files)
        clear_btn.grid(row=0, column=1, sticky='w')

        # File listbox with custom styling
        self.list_container = tk.Frame(self.file_card, bg=self.COLORS['bg_secondary'])
        self.list_container.grid(row=2, column=0, sticky='nsew', padx=15, pady=(0, 10))
        self.list_container.columnconfigure(0, weight=1)
        self.list_container.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(self.list_container,
                                       height=8,
                                       bg=self.COLORS['bg_secondary'],
                                       fg=self.COLORS['text'],
                                       selectbackground=self.COLORS['primary'],
                                       selectforeground='white',
                                       font=('Segoe UI', 10),
                                       borderwidth=0,
                                       highlightthickness=1,
                                       highlightbackground=self.COLORS['border'],
                                       highlightcolor=self.COLORS['primary'],
                                       activestyle='none')
        self.file_listbox.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(self.list_container, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # File count label
        self.file_count_label = ttk.Label(self.file_card, text="No files selected",
                                         style='Subtitle.TLabel')
        self.file_count_label.configure(background=self.COLORS['bg_secondary'])
        self.file_count_label.grid(row=3, column=0, sticky='w', padx=15, pady=(0, 15))

        # ===== RIGHT COLUMN: OUTPUT OPTIONS + CONVERT =====
        right_column = ttk.Frame(main_frame, style='TFrame')
        right_column.grid(row=1, column=1, sticky='nsew', padx=(8, 0), pady=(0, 15))
        right_column.columnconfigure(0, weight=1)

        # Output options card
        self.output_card = tk.Frame(right_column, bg=self.COLORS['bg_secondary'],
                              highlightthickness=1, highlightbackground=self.COLORS['border'])
        self.output_card.grid(row=0, column=0, sticky='new')
        self.output_card.columnconfigure(0, weight=1)

        # Section header
        ttk.Label(self.output_card, text="Output Options",
                 style='Section.TLabel').grid(row=0, column=0, sticky='w',
                                              padx=15, pady=(15, 10))

        # Checkbox
        source_check = ttk.Checkbutton(self.output_card,
                                      text="Save to same folder as source files",
                                      variable=self.use_source_folder,
                                      command=self.toggle_output_folder,
                                      style='TCheckbutton')
        source_check.grid(row=1, column=0, sticky='w', padx=15, pady=(0, 10))

        # Output folder row
        folder_frame = ttk.Frame(self.output_card, style='Card.TFrame')
        folder_frame.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 15))
        folder_frame.columnconfigure(1, weight=1)

        self.folder_label = ttk.Label(folder_frame, text="Custom folder:")
        self.folder_label.configure(background=self.COLORS['bg_secondary'])
        self.folder_label.grid(row=0, column=0, sticky='w', padx=(0, 10))

        self.output_entry = ttk.Entry(folder_frame, textvariable=self.output_folder,
                                     state='disabled')
        self.output_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10))

        self.output_btn = ttk.Button(folder_frame, text="Browse",
                                    command=self.select_output_folder,
                                    state='disabled')
        self.output_btn.grid(row=0, column=2, sticky='e')

        # Progress section
        self.progress_card = tk.Frame(right_column, bg=self.COLORS['bg_secondary'],
                                highlightthickness=1, highlightbackground=self.COLORS['border'])
        self.progress_card.grid(row=1, column=0, sticky='new', pady=(15, 0))
        self.progress_card.columnconfigure(0, weight=1)

        ttk.Label(self.progress_card, text="Progress",
                 style='Section.TLabel').grid(row=0, column=0, sticky='w',
                                              padx=15, pady=(15, 10))

        self.progress = ttk.Progressbar(self.progress_card,
                                       mode='determinate',
                                       style='Custom.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, sticky='ew', padx=15, pady=(0, 8))

        # Status label container to prevent text from expanding the card
        status_container = ttk.Frame(self.progress_card, style='Card.TFrame')
        status_container.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 15))
        status_container.columnconfigure(0, weight=1)
        status_container.grid_propagate(False)
        status_container.configure(height=25)

        self.status_label = ttk.Label(status_container,
                                     text="Ready to convert",
                                     style='Status.TLabel')
        self.status_label.configure(background=self.COLORS['bg_secondary'])
        self.status_label.grid(row=0, column=0, sticky='w')

        # Convert button
        self.convert_btn = ttk.Button(right_column,
                                     text="Convert Files",
                                     command=self.start_conversion,
                                     style='Primary.TButton')
        self.convert_btn.grid(row=2, column=0, sticky='ew', pady=(15, 0))

        # ===== BOTTOM: LOG SECTION (full width) =====
        self.log_card = tk.Frame(main_frame, bg=self.COLORS['bg_secondary'],
                           highlightthickness=1, highlightbackground=self.COLORS['border'])
        self.log_card.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(0, 0))
        self.log_card.columnconfigure(0, weight=1)
        self.log_card.rowconfigure(1, weight=1)

        ttk.Label(self.log_card, text="Activity Log",
                 style='Section.TLabel').grid(row=0, column=0, sticky='w',
                                              padx=15, pady=(15, 10))

        self.log_text = scrolledtext.ScrolledText(self.log_card,
                                                  height=5,
                                                  wrap=tk.WORD,
                                                  bg=self.COLORS['bg_secondary'],
                                                  fg=self.COLORS['text_muted'],
                                                  font=('Consolas', 9),
                                                  borderwidth=0,
                                                  highlightthickness=0,
                                                  insertbackground=self.COLORS['text'])
        self.log_text.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        
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
        for i, file in enumerate(self.epub_files):
            filename = os.path.basename(file)
            # Remove .epub extension for cleaner display
            display_name = filename[:-5] if filename.lower().endswith('.epub') else filename
            self.file_listbox.insert(tk.END, f"   {i + 1}.  {display_name}")
            # Apply alternating row colors
            if i % 2 == 1:
                self.file_listbox.itemconfig(i, bg=self.COLORS['row_alt'])

        # Update file count
        count = len(self.epub_files)
        if count == 0:
            self.file_count_label.config(text="No files selected")
        elif count == 1:
            self.file_count_label.config(text="1 file selected")
        else:
            self.file_count_label.config(text=f"{count} files selected")
            
    def toggle_output_folder(self):
        """Enable/disable output folder selection"""
        if self.use_source_folder.get():
            self.output_btn.config(state='disabled')
            self.output_entry.config(state='disabled')
            self.output_folder.set("")
        else:
            self.output_btn.config(state='normal')
            self.output_entry.config(state='normal')
            
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

    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.COLORS = self.DARK_THEME.copy() if self.is_dark_mode else self.LIGHT_THEME.copy()
        self.theme_btn.config(text="Light Mode" if self.is_dark_mode else "Dark Mode")
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to all widgets"""
        # Update root
        self.root.configure(bg=self.COLORS['bg'])

        # Update ttk styles
        style = ttk.Style()
        style.configure('TFrame', background=self.COLORS['bg'])
        style.configure('Card.TFrame', background=self.COLORS['bg_secondary'])
        style.configure('TLabel', background=self.COLORS['bg'], foreground=self.COLORS['text'])
        style.configure('Title.TLabel', background=self.COLORS['bg'], foreground=self.COLORS['text'])
        style.configure('Subtitle.TLabel', background=self.COLORS['bg'], foreground=self.COLORS['text_muted'])
        style.configure('Section.TLabel', background=self.COLORS['bg_secondary'], foreground=self.COLORS['text'])
        style.configure('Status.TLabel', background=self.COLORS['bg_secondary'], foreground=self.COLORS['success'])
        style.configure('TButton', background=self.COLORS['accent'], foreground='white')
        style.map('TButton',
                 background=[('active', self.COLORS['accent_hover']), ('disabled', self.COLORS['border'])],
                 foreground=[('disabled', self.COLORS['text_muted'])])
        style.configure('Primary.TButton', background=self.COLORS['primary'], foreground='white')
        style.map('Primary.TButton',
                 background=[('active', self.COLORS['primary_hover']), ('disabled', self.COLORS['border'])])
        style.configure('TCheckbutton', background=self.COLORS['bg_secondary'], foreground=self.COLORS['text'])
        style.map('TCheckbutton', background=[('active', self.COLORS['bg_secondary'])])
        style.configure('TEntry', fieldbackground=self.COLORS['bg_secondary'], foreground=self.COLORS['text'])
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.COLORS['primary'],
                       troughcolor=self.COLORS['bg_secondary'])

        # Update tk.Frame cards
        for card in [self.file_card, self.output_card, self.progress_card, self.log_card, self.list_container]:
            card.configure(bg=self.COLORS['bg_secondary'], highlightbackground=self.COLORS['border'])

        # Update listbox
        self.file_listbox.configure(
            bg=self.COLORS['bg_secondary'],
            fg=self.COLORS['text'],
            selectbackground=self.COLORS['primary'],
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['primary']
        )

        # Update log text
        self.log_text.configure(
            bg=self.COLORS['bg_secondary'],
            fg=self.COLORS['text_muted'],
            insertbackground=self.COLORS['text']
        )

        # Update labels with bg_secondary background
        self.file_count_label.configure(background=self.COLORS['bg_secondary'])
        self.folder_label.configure(background=self.COLORS['bg_secondary'])
        self.status_label.configure(background=self.COLORS['bg_secondary'])

        # Refresh file list to update alternating colors
        self.update_file_list()

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
            # Truncate long filenames for status display
            display_name = filename[:30] + '...' if len(filename) > 33 else filename
            self.status_label.config(text=f"Converting {i}/{total}: {display_name}")
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
