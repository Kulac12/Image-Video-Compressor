"""
Resim Boyut Küçültücü - Image Size Reducer Tool
Toplu resim boyut küçültme aracı
Desteklenen formatlar: JPEG, PNG, WebP, BMP, TIFF
Web optimizasyonu için hedef boyut özelliği
Türkçe/İngilizce dil desteği
Sürükle-Bırak desteği
"""

import os
import sys
import threading
import io
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Entry, Scale, Listbox, Scrollbar,
    filedialog, messagebox, StringVar, IntVar, BooleanVar,
    Checkbutton, OptionMenu, HORIZONTAL, END, MULTIPLE, EXTENDED, TclError
)
from tkinter.ttk import Progressbar, Style, Combobox
from PIL import Image

# Try to import drag and drop support
try:
    import windnd
    HAS_DND = True
except ImportError:
    HAS_DND = False


# Language dictionaries
LANGUAGES = {
    'tr': {
        'title': 'Resim Boyut Küçült',
        'language': 'Dil:',
        'image_files': 'Resim Dosyaları:',
        'add_files': 'Dosya Ekle',
        'add_folder': 'Klasör Ekle',
        'remove_selected': 'Sil',
        'clear_all': 'Temizle',
        'files_selected': '{} dosya seçili',
        'settings': 'Ayarlar:',
        'quality': 'Kalite:',
        'output_format': 'Format:',
        'original': 'Orijinal',
        'speed': 'Hız:',
        'speed_fast': 'Hızlı',
        'speed_normal': 'Normal',
        'speed_slow': 'Yavaş',
        'speed_info': 'Hızlı=büyük dosya | Yavaş=küçük dosya',
        'target_size': 'Hedef Boyut (KB)',
        'target_size_info': 'Web optimizasyonu',
        'min': 'Min:',
        'max': 'Max:',
        'quality_auto': '(Otomatik kalite)',
        'limit_size': 'Boyut Sınırla:',
        'max_width': 'Max G:',
        'max_height': 'Max Y:',
        'output_settings': 'Çıktı:',
        'save_same_folder': 'Aynı klasöre kaydet',
        'file_suffix': 'Sonek:',
        'output_folder': 'Klasör:',
        'browse': 'Seç...',
        'ready': 'Hazır',
        'start_button': 'BAŞLAT',
        'processing': 'İşleniyor: {}',
        'completed': 'Tamamlandı! {}/{} dosya. Kazanç: {:.1f}% ({} → {})',
        'completed_simple': 'Tamamlandı! {}/{} dosya işlendi.',
        'completed_msg': '{}/{} dosya başarıyla küçültüldü!',
        'warning': 'Uyarı',
        'select_file_warning': 'Lütfen en az bir dosya seçin!',
        'select_folder_warning': 'Lütfen çıktı klasörü seçin!',
        'min_max_warning': 'Min boyut, Max boyuttan küçük olmalı!',
        'select_images': 'Resim Dosyaları Seç',
        'select_folder': 'Klasör Seç',
        'select_output': 'Çıktı Klasörü Seç',
        'image_files_filter': 'Resim Dosyaları',
        'all_files': 'Tüm Dosyalar',
        'drag_drop': 'Dosyaları sürükle-bırak veya butonları kullan',
    },
    'en': {
        'title': 'Image Size Reducer',
        'language': 'Lang:',
        'image_files': 'Image Files:',
        'add_files': 'Add Files',
        'add_folder': 'Add Folder',
        'remove_selected': 'Remove',
        'clear_all': 'Clear',
        'files_selected': '{} files selected',
        'settings': 'Settings:',
        'quality': 'Quality:',
        'output_format': 'Format:',
        'original': 'Original',
        'speed': 'Speed:',
        'speed_fast': 'Fast',
        'speed_normal': 'Normal',
        'speed_slow': 'Slow',
        'speed_info': 'Fast=larger file | Slow=smaller file',
        'target_size': 'Target Size (KB)',
        'target_size_info': 'Web optimization',
        'min': 'Min:',
        'max': 'Max:',
        'quality_auto': '(Auto quality)',
        'limit_size': 'Limit Size:',
        'max_width': 'Max W:',
        'max_height': 'Max H:',
        'output_settings': 'Output:',
        'save_same_folder': 'Save to same folder',
        'file_suffix': 'Suffix:',
        'output_folder': 'Folder:',
        'browse': 'Browse',
        'ready': 'Ready',
        'start_button': 'START',
        'processing': 'Processing: {}',
        'completed': 'Done! {}/{} files. Saved: {:.1f}% ({} → {})',
        'completed_simple': 'Done! {}/{} files processed.',
        'completed_msg': '{}/{} files reduced successfully!',
        'warning': 'Warning',
        'select_file_warning': 'Please select at least one file!',
        'select_folder_warning': 'Please select an output folder!',
        'min_max_warning': 'Min size must be less than Max size!',
        'select_images': 'Select Image Files',
        'select_folder': 'Select Folder',
        'select_output': 'Select Output Folder',
        'image_files_filter': 'Image Files',
        'all_files': 'All Files',
        'drag_drop': 'Drag-drop files or use buttons',
    }
}


class ResimBoyutKucult:
    def __init__(self, root):
        self.root = root
        self.current_lang = 'tr'
        self.lang = LANGUAGES[self.current_lang]

        self.root.title(self.lang['title'])
        self.root.geometry("750x650")
        self.root.minsize(700, 600)

        # Variables
        self.files = []
        self.quality = IntVar(value=85)
        self.output_format = StringVar(value=self.lang['original'])
        self.resize_enabled = BooleanVar(value=False)
        self.max_width = IntVar(value=1920)
        self.max_height = IntVar(value=1080)
        self.output_folder = StringVar(value="")
        self.same_folder = BooleanVar(value=True)
        self.suffix = StringVar(value="_kucultulmus")
        self.language_var = StringVar(value="Türkçe")

        # Target size feature - ENABLED BY DEFAULT
        self.target_size_enabled = BooleanVar(value=True)
        self.min_size_kb = IntVar(value=100)
        self.max_size_kb = IntVar(value=300)

        # Speed setting
        self.speed = StringVar(value=self.lang['speed_normal'])

        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif']

        self.create_ui()
        self.setup_drag_drop()

    def get_text(self, key):
        return LANGUAGES[self.current_lang].get(key, key)

    def change_language(self, *args):
        lang_selection = self.language_var.get()
        if lang_selection == "Türkçe":
            self.current_lang = 'tr'
        else:
            self.current_lang = 'en'

        self.lang = LANGUAGES[self.current_lang]

        # Update texts without destroying widgets
        self.update_texts()

    def update_texts(self):
        """Update all text labels without recreating UI"""
        self.root.title(self.lang['title'])

        # Update all labels and buttons
        self.lbl_files.config(text=self.lang['image_files'])
        self.btn_add_files.config(text=self.lang['add_files'])
        self.btn_add_folder.config(text=self.lang['add_folder'])
        self.btn_remove.config(text=self.lang['remove_selected'])
        self.btn_clear.config(text=self.lang['clear_all'])
        self.file_count_label.config(text=self.lang['files_selected'].format(len(self.files)))

        self.lbl_settings.config(text=self.lang['settings'])
        self.lbl_quality.config(text=self.lang['quality'])
        self.lbl_format.config(text=self.lang['output_format'])
        self.lbl_speed.config(text=self.lang['speed'])
        self.lbl_speed_info.config(text=self.lang['speed_info'])

        self.target_check.config(text=self.lang['target_size'])
        self.lbl_target_info.config(text=f"({self.lang['target_size_info']})")
        self.lbl_min.config(text=self.lang['min'])
        self.lbl_max.config(text=self.lang['max'])
        self.lbl_auto.config(text=self.lang['quality_auto'])

        self.resize_check.config(text=self.lang['limit_size'])
        self.lbl_max_w.config(text=self.lang['max_width'])
        self.lbl_max_h.config(text=self.lang['max_height'])

        self.lbl_output.config(text=self.lang['output_settings'])
        self.same_folder_check.config(text=self.lang['save_same_folder'])
        self.lbl_suffix.config(text=self.lang['file_suffix'])
        self.lbl_folder.config(text=self.lang['output_folder'])
        self.btn_browse.config(text=self.lang['browse'])

        self.status_label.config(text=self.lang['ready'])
        self.start_button.config(text=self.lang['start_button'])

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        if HAS_DND:
            try:
                windnd.hook_dropfiles(self.root, func=self.handle_drop)
            except Exception:
                pass

    def handle_drop(self, files):
        """Handle dropped files"""
        for file in files:
            if isinstance(file, bytes):
                file = file.decode('utf-8')

            file_path = str(file)

            if os.path.isdir(file_path):
                for f in Path(file_path).rglob("*"):
                    if f.suffix.lower() in self.supported_formats:
                        fp = str(f)
                        if fp not in self.files:
                            self.files.append(fp)
                            self.file_listbox.insert(END, f.name)
            elif os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.supported_formats and file_path not in self.files:
                    self.files.append(file_path)
                    self.file_listbox.insert(END, os.path.basename(file_path))

        self.update_file_count()

    def create_ui(self):
        # Main frame
        main_frame = Frame(self.root, padx=10, pady=5)
        main_frame.pack(fill="both", expand=True)

        # Row 0: Language selection
        row0 = Frame(main_frame)
        row0.pack(fill="x", pady=2)

        Label(row0, text=self.lang['language'], font=("Arial", 9)).pack(side="left")
        lang_options = ["Türkçe", "English"]
        self.language_var.set("Türkçe" if self.current_lang == 'tr' else "English")
        lang_menu = OptionMenu(row0, self.language_var, *lang_options, command=self.change_language)
        lang_menu.config(font=("Arial", 9), width=8)
        lang_menu.pack(side="left", padx=5)

        Label(row0, text=self.lang['drag_drop'], font=("Arial", 8), fg="gray").pack(side="right")

        # Row 1: File selection
        row1 = Frame(main_frame)
        row1.pack(fill="both", expand=True, pady=3)

        self.lbl_files = Label(row1, text=self.lang['image_files'], font=("Arial", 9, "bold"))
        self.lbl_files.pack(anchor="w")

        btn_frame = Frame(row1)
        btn_frame.pack(fill="x", pady=2)

        self.btn_add_files = Button(btn_frame, text=self.lang['add_files'], command=self.add_files, width=10)
        self.btn_add_files.pack(side="left", padx=1)
        self.btn_add_folder = Button(btn_frame, text=self.lang['add_folder'], command=self.add_folder, width=10)
        self.btn_add_folder.pack(side="left", padx=1)
        self.btn_remove = Button(btn_frame, text=self.lang['remove_selected'], command=self.remove_selected, width=8)
        self.btn_remove.pack(side="left", padx=1)
        self.btn_clear = Button(btn_frame, text=self.lang['clear_all'], command=self.clear_all, width=8)
        self.btn_clear.pack(side="left", padx=1)

        # File list
        list_frame = Frame(row1)
        list_frame.pack(fill="both", expand=True, pady=2)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = Listbox(list_frame, selectmode=EXTENDED, height=6, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        self.file_count_label = Label(row1, text=self.lang['files_selected'].format(0), font=("Arial", 8))
        self.file_count_label.pack(anchor="w")

        # Row 2: Settings
        row2 = Frame(main_frame)
        row2.pack(fill="x", pady=3)

        self.lbl_settings = Label(row2, text=self.lang['settings'], font=("Arial", 9, "bold"))
        self.lbl_settings.pack(anchor="w")

        settings_inner = Frame(row2)
        settings_inner.pack(fill="x")

        # Quality
        self.lbl_quality = Label(settings_inner, text=self.lang['quality'])
        self.lbl_quality.pack(side="left")
        self.quality_scale = Scale(settings_inner, from_=1, to=100, orient=HORIZONTAL, variable=self.quality, length=120)
        self.quality_scale.pack(side="left", padx=3)
        self.quality_label = Label(settings_inner, text="85%", width=4)
        self.quality_label.pack(side="left")
        self.quality.trace("w", self.update_quality_label)

        # Format
        self.lbl_format = Label(settings_inner, text=self.lang['output_format'])
        self.lbl_format.pack(side="left", padx=(10, 0))
        format_options = [self.lang['original'], "JPEG", "PNG", "WebP"]
        self.format_menu = OptionMenu(settings_inner, self.output_format, *format_options)
        self.format_menu.config(width=8)
        self.format_menu.pack(side="left", padx=3)

        # Speed
        self.lbl_speed = Label(settings_inner, text=self.lang['speed'])
        self.lbl_speed.pack(side="left", padx=(10, 0))
        speed_options = [self.lang['speed_fast'], self.lang['speed_normal'], self.lang['speed_slow']]
        self.speed_menu = OptionMenu(settings_inner, self.speed, *speed_options)
        self.speed_menu.config(width=8)
        self.speed_menu.pack(side="left", padx=3)

        self.lbl_speed_info = Label(settings_inner, text=self.lang['speed_info'], font=("Arial", 7), fg="gray")
        self.lbl_speed_info.pack(side="left", padx=5)

        # Row 3: Target Size
        row3 = Frame(main_frame, relief="groove", bd=1, bg="#e8f5e9")
        row3.pack(fill="x", pady=3)

        target_inner = Frame(row3, bg="#e8f5e9")
        target_inner.pack(fill="x", padx=5, pady=3)

        self.target_check = Checkbutton(target_inner, text=self.lang['target_size'],
                    variable=self.target_size_enabled, command=self.toggle_target_size,
                    font=("Arial", 9, "bold"), bg="#e8f5e9")
        self.target_check.pack(side="left")

        self.lbl_target_info = Label(target_inner, text=f"({self.lang['target_size_info']})",
              font=("Arial", 8), fg="#388e3c", bg="#e8f5e9")
        self.lbl_target_info.pack(side="left", padx=5)

        self.lbl_min = Label(target_inner, text=self.lang['min'], bg="#e8f5e9")
        self.lbl_min.pack(side="left", padx=(10, 0))
        self.min_entry = Entry(target_inner, textvariable=self.min_size_kb, width=6)
        self.min_entry.pack(side="left", padx=2)
        Label(target_inner, text="KB", bg="#e8f5e9").pack(side="left")

        self.lbl_max = Label(target_inner, text=self.lang['max'], bg="#e8f5e9")
        self.lbl_max.pack(side="left", padx=(10, 0))
        self.max_entry = Entry(target_inner, textvariable=self.max_size_kb, width=6)
        self.max_entry.pack(side="left", padx=2)
        Label(target_inner, text="KB", bg="#e8f5e9").pack(side="left")

        self.lbl_auto = Label(target_inner, text=self.lang['quality_auto'], font=("Arial", 7), fg="#388e3c", bg="#e8f5e9")
        self.lbl_auto.pack(side="left", padx=10)

        # Row 4: Resize
        row4 = Frame(main_frame)
        row4.pack(fill="x", pady=2)

        self.resize_check = Checkbutton(row4, text=self.lang['limit_size'], variable=self.resize_enabled, command=self.toggle_resize)
        self.resize_check.pack(side="left")

        self.lbl_max_w = Label(row4, text=self.lang['max_width'])
        self.lbl_max_w.pack(side="left", padx=(10, 0))
        self.width_entry = Entry(row4, textvariable=self.max_width, width=6, state="disabled")
        self.width_entry.pack(side="left", padx=2)

        self.lbl_max_h = Label(row4, text=self.lang['max_height'])
        self.lbl_max_h.pack(side="left", padx=(10, 0))
        self.height_entry = Entry(row4, textvariable=self.max_height, width=6, state="disabled")
        self.height_entry.pack(side="left", padx=2)

        # Row 5: Output
        row5 = Frame(main_frame)
        row5.pack(fill="x", pady=3)

        self.lbl_output = Label(row5, text=self.lang['output_settings'], font=("Arial", 9, "bold"))
        self.lbl_output.pack(anchor="w")

        output_inner = Frame(row5)
        output_inner.pack(fill="x")

        self.same_folder_check = Checkbutton(output_inner, text=self.lang['save_same_folder'],
                    variable=self.same_folder, command=self.toggle_output)
        self.same_folder_check.pack(side="left")

        self.lbl_suffix = Label(output_inner, text=self.lang['file_suffix'])
        self.lbl_suffix.pack(side="left", padx=(15, 0))
        Entry(output_inner, textvariable=self.suffix, width=15).pack(side="left", padx=2)

        output_row2 = Frame(row5)
        output_row2.pack(fill="x", pady=2)

        self.lbl_folder = Label(output_row2, text=self.lang['output_folder'])
        self.lbl_folder.pack(side="left")
        self.output_entry = Entry(output_row2, textvariable=self.output_folder, width=35, state="disabled")
        self.output_entry.pack(side="left", padx=5)
        self.btn_browse = Button(output_row2, text=self.lang['browse'], command=self.select_output_folder, state="disabled")
        self.btn_browse.pack(side="left")

        # Row 6: Progress
        row6 = Frame(main_frame)
        row6.pack(fill="x", pady=3)

        self.progress_label = Label(row6, text="", font=("Arial", 8))
        self.progress_label.pack(anchor="w")

        self.progressbar = Progressbar(row6, length=400, mode='determinate')
        self.progressbar.pack(fill="x", pady=2)

        self.status_label = Label(row6, text=self.lang['ready'], font=("Arial", 8), fg="#666")
        self.status_label.pack(anchor="w")

        # Row 7: Start Button
        row7 = Frame(main_frame)
        row7.pack(fill="x", pady=5)

        self.start_button = Button(
            row7,
            text=self.lang['start_button'],
            command=self.start_compression,
            font=("Arial", 12, "bold"),
            bg="#2e7d32",
            fg="white",
            activebackground="#1b5e20",
            activeforeground="white",
            cursor="hand2"
        )
        self.start_button.pack(fill="x", ipady=8)

    def update_quality_label(self, *args):
        try:
            self.quality_label.config(text=f"{self.quality.get()}%")
        except TclError:
            pass

    def toggle_target_size(self):
        state = "normal" if self.target_size_enabled.get() else "disabled"
        self.min_entry.config(state=state)
        self.max_entry.config(state=state)

    def toggle_resize(self):
        state = "normal" if self.resize_enabled.get() else "disabled"
        self.width_entry.config(state=state)
        self.height_entry.config(state=state)

    def toggle_output(self):
        state = "disabled" if self.same_folder.get() else "normal"
        self.output_entry.config(state=state)
        self.btn_browse.config(state=state)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title=self.lang['select_images'],
            filetypes=[
                (self.lang['image_files_filter'], "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                (self.lang['all_files'], "*.*")
            ]
        )
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(END, os.path.basename(file))
        self.update_file_count()

    def add_folder(self):
        folder = filedialog.askdirectory(title=self.lang['select_folder'])
        if folder:
            for file in Path(folder).rglob("*"):
                if file.suffix.lower() in self.supported_formats:
                    file_path = str(file)
                    if file_path not in self.files:
                        self.files.append(file_path)
                        self.file_listbox.insert(END, file.name)
        self.update_file_count()

    def remove_selected(self):
        selected = list(self.file_listbox.curselection())
        selected.reverse()
        for i in selected:
            self.file_listbox.delete(i)
            if i < len(self.files):
                del self.files[i]
        self.update_file_count()

    def clear_all(self):
        self.file_listbox.delete(0, END)
        self.files.clear()
        self.update_file_count()

    def update_file_count(self):
        self.file_count_label.config(text=self.lang['files_selected'].format(len(self.files)))

    def select_output_folder(self):
        folder = filedialog.askdirectory(title=self.lang['select_output'])
        if folder:
            self.output_folder.set(folder)

    def convert_format(self, filename, format_str):
        name, _ = os.path.splitext(filename)
        if format_str == "JPEG":
            return name + ".jpg"
        elif format_str == "PNG":
            return name + ".png"
        elif format_str == "WebP":
            return name + ".webp"
        return filename

    def get_speed_params(self):
        speed = self.speed.get()
        fast_options = [LANGUAGES['tr']['speed_fast'], LANGUAGES['en']['speed_fast']]
        slow_options = [LANGUAGES['tr']['speed_slow'], LANGUAGES['en']['speed_slow']]

        if speed in fast_options:
            return {'webp_method': 1, 'png_compress': 1, 'jpeg_optimize': False}
        elif speed in slow_options:
            return {'webp_method': 6, 'png_compress': 9, 'jpeg_optimize': True}
        else:
            return {'webp_method': 4, 'png_compress': 6, 'jpeg_optimize': True}

    def get_image_size_at_quality(self, img, format_type, quality):
        buffer = io.BytesIO()
        speed_params = self.get_speed_params()

        save_img = img
        if format_type == 'JPEG' and img.mode in ('RGBA', 'P'):
            save_img = img.convert('RGB')

        if format_type == 'JPEG':
            save_img.save(buffer, format='JPEG', quality=quality, optimize=speed_params['jpeg_optimize'])
        elif format_type == 'WEBP':
            save_img.save(buffer, format='WebP', quality=quality, method=speed_params['webp_method'])
        elif format_type == 'PNG':
            save_img.save(buffer, format='PNG', optimize=True, compress_level=speed_params['png_compress'])
        else:
            save_img.save(buffer, format='JPEG', quality=quality, optimize=speed_params['jpeg_optimize'])

        return buffer.tell()

    def find_optimal_quality(self, img, format_type, min_kb, max_kb):
        min_bytes = min_kb * 1024
        max_bytes = max_kb * 1024

        if format_type == 'PNG':
            format_type = 'JPEG'

        low, high = 5, 100
        best_quality = 50
        best_size = float('inf')

        min_size = self.get_image_size_at_quality(img, format_type, low)
        max_size = self.get_image_size_at_quality(img, format_type, high)

        if min_size > max_bytes:
            return low, format_type

        if max_size <= max_bytes:
            return high, format_type

        iterations = 0
        while low <= high and iterations < 20:
            iterations += 1
            mid = (low + high) // 2
            size = self.get_image_size_at_quality(img, format_type, mid)

            if min_bytes <= size <= max_bytes:
                best_quality = mid
                best_size = size
                low = mid + 1
            elif size > max_bytes:
                high = mid - 1
            else:
                if size > best_size:
                    best_quality = mid
                    best_size = size
                low = mid + 1

        return best_quality, format_type

    def compress_image(self, source, target, quality, max_size=None, target_size=None):
        try:
            img = Image.open(source)

            target_ext = os.path.splitext(target)[1].lower()
            if target_ext in ['.jpg', '.jpeg']:
                target_format = 'JPEG'
            elif target_ext == '.webp':
                target_format = 'WEBP'
            elif target_ext == '.png':
                target_format = 'PNG'
            else:
                target_format = 'JPEG'

            if img.mode == 'RGBA' and target_format == 'JPEG':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ['RGB', 'RGBA'] and target_format == 'JPEG':
                img = img.convert('RGB')

            if max_size:
                max_w, max_h = max_size
                w, h = img.size
                if w > max_w or h > max_h:
                    ratio = min(max_w/w, max_h/h)
                    new_size = (int(w * ratio), int(h * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

            actual_format = target_format
            if target_size:
                min_kb, max_kb = target_size
                quality, actual_format = self.find_optimal_quality(img, target_format, min_kb, max_kb)

                if target_format == 'PNG' and actual_format == 'JPEG':
                    target = os.path.splitext(target)[0] + '.jpg'
                    target_format = 'JPEG'

            speed_params = self.get_speed_params()

            if target_format == 'JPEG' and img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif target_format == 'JPEG' and img.mode != 'RGB':
                img = img.convert('RGB')

            if target_format == 'JPEG':
                img.save(target, format='JPEG', quality=quality, optimize=speed_params['jpeg_optimize'])
            elif target_format == 'PNG':
                img.save(target, format='PNG', optimize=True, compress_level=speed_params['png_compress'])
            elif target_format == 'WEBP':
                img.save(target, format='WebP', quality=quality, method=speed_params['webp_method'])
            else:
                img.save(target, quality=quality)

            original_size = os.path.getsize(source)
            new_size = os.path.getsize(target)
            return True, original_size, new_size, quality

        except Exception as e:
            return False, str(e), 0, 0

    def start_compression(self):
        if not self.files:
            messagebox.showwarning(self.lang['warning'], self.lang['select_file_warning'])
            return

        if not self.same_folder.get() and not self.output_folder.get():
            messagebox.showwarning(self.lang['warning'], self.lang['select_folder_warning'])
            return

        if self.target_size_enabled.get():
            if self.min_size_kb.get() >= self.max_size_kb.get():
                messagebox.showwarning(self.lang['warning'], self.lang['min_max_warning'])
                return

        self.start_button.config(state="disabled", text="...")

        thread = threading.Thread(target=self.compression_process)
        thread.daemon = True
        thread.start()

    def compression_process(self):
        total = len(self.files)
        successful = 0
        total_original = 0
        total_new = 0

        self.progressbar["maximum"] = total

        for i, file in enumerate(self.files):
            filename = os.path.basename(file)
            self.progress_label.config(text=self.lang['processing'].format(filename))

            if self.same_folder.get():
                output_dir = os.path.dirname(file)
            else:
                output_dir = self.output_folder.get()

            name, ext = os.path.splitext(filename)

            original_opts = [LANGUAGES['tr']['original'], LANGUAGES['en']['original']]
            if self.output_format.get() not in original_opts:
                new_name = self.convert_format(filename, self.output_format.get())
            else:
                new_name = filename

            name, ext = os.path.splitext(new_name)
            new_name = name + self.suffix.get() + ext

            target_path = os.path.join(output_dir, new_name)

            max_size = None
            if self.resize_enabled.get():
                max_size = (self.max_width.get(), self.max_height.get())

            target_size = None
            if self.target_size_enabled.get():
                target_size = (self.min_size_kb.get(), self.max_size_kb.get())

            result, original, new, used_quality = self.compress_image(
                file, target_path, self.quality.get(), max_size, target_size
            )

            if result:
                successful += 1
                total_original += original
                total_new += new

            self.progressbar["value"] = i + 1
            self.root.update_idletasks()

        self.start_button.config(state="normal", text=self.lang['start_button'])

        if total_original > 0:
            savings = ((total_original - total_new) / total_original) * 100
            self.status_label.config(
                text=self.lang['completed'].format(
                    successful, total, savings,
                    self.format_size(total_original), self.format_size(total_new)
                ),
                fg="#2e7d32"
            )
        else:
            self.status_label.config(text=self.lang['completed_simple'].format(successful, total), fg="#2e7d32")

        self.progress_label.config(text="")
        messagebox.showinfo("OK", self.lang['completed_msg'].format(successful, total))

    def format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"


def main():
    root = Tk()
    app = ResimBoyutKucult(root)
    root.mainloop()


if __name__ == "__main__":
    main()
