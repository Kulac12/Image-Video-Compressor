"""
Video Boyut Küçültücü - Video Size Reducer Tool
Toplu video boyut küçültme aracı
FFmpeg ile H.264/H.265/VP9 codec desteği
Türkçe/İngilizce dil desteği
"""

import os
import sys
import subprocess
import threading
import json
import re
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Entry, Scale, Listbox, Scrollbar,
    filedialog, messagebox, StringVar, IntVar, BooleanVar,
    Checkbutton, OptionMenu, HORIZONTAL, END, EXTENDED
)
from tkinter.ttk import Progressbar, Combobox


# Language dictionaries
LANGUAGES = {
    'tr': {
        'title': 'Video Boyut Küçült',
        'language': 'Dil:',
        'ffmpeg_warning': 'UYARI: FFmpeg bulunamadı! Lütfen FFmpeg\'i yükleyin ve PATH\'e ekleyin.',
        'video_files': 'Video Dosyaları:',
        'add_files': 'Dosya Ekle',
        'add_folder': 'Klasör Ekle',
        'remove_selected': 'Seçileni Sil',
        'clear_all': 'Tümünü Temizle',
        'files_selected': '{} dosya seçili',
        'video_settings': 'Video Ayarları:',
        'codec': 'Codec:',
        'preset': 'Preset:',
        'quality_crf': 'Kalite (CRF):',
        'quality_high': 'Yüksek',
        'quality_normal': 'Normal',
        'quality_low': 'Düşük',
        'quality_very_low': 'Çok Düşük',
        'crf_info': '(0=kayıpsız, 18=yüksek, 23=normal, 28=düşük)',
        'resolution': 'Çözünürlük:',
        'original': 'Orijinal',
        'audio_settings': 'Ses Ayarları:',
        'keep_audio': 'Sesi koru',
        'audio_bitrate': 'Ses Bitrate:',
        'output_format': 'Çıktı Formatı:',
        'output_settings': 'Çıktı Ayarları:',
        'save_same_folder': 'Aynı klasöre kaydet',
        'file_suffix': 'Dosya Soneki:',
        'output_folder': 'Çıktı Klasörü:',
        'browse': 'Seç...',
        'ready': 'Hazır',
        'start_button': 'BOYUT KÜÇÜLTMEYE BAŞLA',
        'cancel_button': 'İPTAL',
        'processing': 'İşleniyor ({}/{}): {}',
        'completed': 'Tamamlandı! {}/{} video küçültüldü. Kazanç: {:.1f}% ({} -> {})',
        'completed_simple': 'Tamamlandı! {}/{} video işlendi.',
        'completed_msg': '{}/{} video başarıyla küçültüldü!',
        'cancelled': 'İptal edildi!',
        'warning': 'Uyarı',
        'error': 'Hata',
        'ffmpeg_error': 'FFmpeg bulunamadı! Lütfen FFmpeg\'i yükleyin.',
        'select_file_warning': 'Lütfen en az bir dosya seçin!',
        'select_folder_warning': 'Lütfen çıktı klasörü seçin!',
        'select_videos': 'Video Dosyaları Seç',
        'select_folder': 'Klasör Seç',
        'select_output': 'Çıktı Klasörü Seç',
        'video_files_filter': 'Video Dosyaları',
        'all_files': 'Tüm Dosyalar',
    },
    'en': {
        'title': 'Video Size Reducer',
        'language': 'Language:',
        'ffmpeg_warning': 'WARNING: FFmpeg not found! Please install FFmpeg and add it to PATH.',
        'video_files': 'Video Files:',
        'add_files': 'Add Files',
        'add_folder': 'Add Folder',
        'remove_selected': 'Remove Selected',
        'clear_all': 'Clear All',
        'files_selected': '{} files selected',
        'video_settings': 'Video Settings:',
        'codec': 'Codec:',
        'preset': 'Preset:',
        'quality_crf': 'Quality (CRF):',
        'quality_high': 'High',
        'quality_normal': 'Normal',
        'quality_low': 'Low',
        'quality_very_low': 'Very Low',
        'crf_info': '(0=lossless, 18=high, 23=normal, 28=low)',
        'resolution': 'Resolution:',
        'original': 'Original',
        'audio_settings': 'Audio Settings:',
        'keep_audio': 'Keep audio',
        'audio_bitrate': 'Audio Bitrate:',
        'output_format': 'Output Format:',
        'output_settings': 'Output Settings:',
        'save_same_folder': 'Save to same folder',
        'file_suffix': 'File Suffix:',
        'output_folder': 'Output Folder:',
        'browse': 'Browse...',
        'ready': 'Ready',
        'start_button': 'START REDUCING',
        'cancel_button': 'CANCEL',
        'processing': 'Processing ({}/{}): {}',
        'completed': 'Completed! {}/{} videos reduced. Savings: {:.1f}% ({} -> {})',
        'completed_simple': 'Completed! {}/{} videos processed.',
        'completed_msg': '{}/{} videos successfully reduced!',
        'cancelled': 'Cancelled!',
        'warning': 'Warning',
        'error': 'Error',
        'ffmpeg_error': 'FFmpeg not found! Please install FFmpeg.',
        'select_file_warning': 'Please select at least one file!',
        'select_folder_warning': 'Please select an output folder!',
        'select_videos': 'Select Video Files',
        'select_folder': 'Select Folder',
        'select_output': 'Select Output Folder',
        'video_files_filter': 'Video Files',
        'all_files': 'All Files',
    }
}


class VideoBoyutKucult:
    def __init__(self, root):
        self.root = root
        self.current_lang = 'tr'
        self.lang = LANGUAGES[self.current_lang]

        self.root.title(self.lang['title'])
        self.root.geometry("780x700")
        self.root.resizable(True, True)

        # Variables
        self.files = []
        self.codec = StringVar(value="H.264 (libx264)")
        self.crf = IntVar(value=23)
        self.preset = StringVar(value="medium")
        self.resolution = StringVar(value=self.lang['original'])
        self.audio_bitrate = StringVar(value="128k")
        self.output_format = StringVar(value="MP4")
        self.output_folder = StringVar(value="")
        self.same_folder = BooleanVar(value=True)
        self.suffix = StringVar(value="_kucultulmus")
        self.keep_audio = BooleanVar(value=True)
        self.language_var = StringVar(value="Türkçe")

        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg']
        self.cancelled = False
        self.active_process = None

        self.check_ffmpeg()
        self.create_ui()

    def check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            self.ffmpeg_available = True
        except FileNotFoundError:
            self.ffmpeg_available = False

    def change_language(self, *args):
        lang_selection = self.language_var.get()
        if lang_selection == "Türkçe":
            self.current_lang = 'tr'
        else:
            self.current_lang = 'en'

        self.lang = LANGUAGES[self.current_lang]
        self.refresh_ui()

    def refresh_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.resolution.set(self.lang['original'])
        self.root.title(self.lang['title'])
        self.create_ui()

    def create_ui(self):
        main_frame = Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Language selection
        lang_frame = Frame(main_frame)
        lang_frame.pack(fill="x", pady=5)

        Label(lang_frame, text=self.lang['language'], font=("Arial", 10, "bold")).pack(side="left")
        lang_options = ["Türkçe", "English"]
        self.language_var.set("Türkçe" if self.current_lang == 'tr' else "English")
        lang_menu = OptionMenu(lang_frame, self.language_var, *lang_options, command=self.change_language)
        lang_menu.pack(side="left", padx=10)

        # FFmpeg warning
        if not self.ffmpeg_available:
            warning_frame = Frame(main_frame, bg="#FFCCCC")
            warning_frame.pack(fill="x", pady=5)
            Label(warning_frame, text=self.lang['ffmpeg_warning'],
                  bg="#FFCCCC", fg="#CC0000", font=("Arial", 10, "bold")).pack(pady=5)

        # File selection section
        file_frame = Frame(main_frame)
        file_frame.pack(fill="x", pady=5)

        Label(file_frame, text=self.lang['video_files'], font=("Arial", 10, "bold")).pack(anchor="w")

        btn_frame = Frame(file_frame)
        btn_frame.pack(fill="x", pady=5)

        Button(btn_frame, text=self.lang['add_files'], command=self.add_files, width=15).pack(side="left", padx=2)
        Button(btn_frame, text=self.lang['add_folder'], command=self.add_folder, width=15).pack(side="left", padx=2)
        Button(btn_frame, text=self.lang['remove_selected'], command=self.remove_selected, width=15).pack(side="left", padx=2)
        Button(btn_frame, text=self.lang['clear_all'], command=self.clear_all, width=15).pack(side="left", padx=2)

        # File list
        list_frame = Frame(file_frame)
        list_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = Listbox(list_frame, selectmode=EXTENDED, height=5,
                                     yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        for f in self.files:
            self.file_listbox.insert(END, os.path.basename(f))

        self.file_count_label = Label(file_frame, text=self.lang['files_selected'].format(len(self.files)))
        self.file_count_label.pack(anchor="w")

        # Video settings
        settings_frame = Frame(main_frame)
        settings_frame.pack(fill="x", pady=10)

        Label(settings_frame, text=self.lang['video_settings'], font=("Arial", 10, "bold")).pack(anchor="w")

        # Codec selection
        codec_frame = Frame(settings_frame)
        codec_frame.pack(fill="x", pady=5)

        Label(codec_frame, text=self.lang['codec']).pack(side="left")
        codec_options = ["H.264 (libx264)", "H.265 (libx265)", "VP9"]
        OptionMenu(codec_frame, self.codec, *codec_options).pack(side="left", padx=10)

        Label(codec_frame, text=self.lang['preset']).pack(side="left", padx=(20, 5))
        preset_options = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
        OptionMenu(codec_frame, self.preset, *preset_options).pack(side="left")

        # CRF setting
        crf_frame = Frame(settings_frame)
        crf_frame.pack(fill="x", pady=5)

        Label(crf_frame, text=self.lang['quality_crf']).pack(side="left")
        self.crf_scale = Scale(crf_frame, from_=0, to=51, orient=HORIZONTAL,
                                variable=self.crf, length=200)
        self.crf_scale.pack(side="left", padx=10)
        self.crf_label = Label(crf_frame, text=f"23 ({self.lang['quality_normal']})")
        self.crf_label.pack(side="left")
        self.crf.trace("w", self.update_crf_label)

        Label(crf_frame, text=self.lang['crf_info'], font=("Arial", 8)).pack(side="left", padx=10)

        # Resolution
        resolution_frame = Frame(settings_frame)
        resolution_frame.pack(fill="x", pady=5)

        Label(resolution_frame, text=self.lang['resolution']).pack(side="left")
        resolution_options = [self.lang['original'], "1920x1080 (Full HD)", "1280x720 (HD)", "854x480 (SD)", "640x360"]
        OptionMenu(resolution_frame, self.resolution, *resolution_options).pack(side="left", padx=10)

        # Audio settings
        audio_frame = Frame(main_frame)
        audio_frame.pack(fill="x", pady=5)

        Label(audio_frame, text=self.lang['audio_settings'], font=("Arial", 10, "bold")).pack(anchor="w")

        audio_inner_frame = Frame(audio_frame)
        audio_inner_frame.pack(fill="x", pady=5)

        Checkbutton(audio_inner_frame, text=self.lang['keep_audio'], variable=self.keep_audio).pack(side="left")

        Label(audio_inner_frame, text=self.lang['audio_bitrate']).pack(side="left", padx=(20, 5))
        audio_options = ["64k", "96k", "128k", "192k", "256k", "320k", self.lang['original']]
        OptionMenu(audio_inner_frame, self.audio_bitrate, *audio_options).pack(side="left")

        # Output format
        format_frame = Frame(main_frame)
        format_frame.pack(fill="x", pady=5)

        Label(format_frame, text=self.lang['output_format']).pack(side="left")
        format_options = ["MP4", "MKV", "WebM", "AVI"]
        OptionMenu(format_frame, self.output_format, *format_options).pack(side="left", padx=10)

        # Output folder
        output_frame = Frame(main_frame)
        output_frame.pack(fill="x", pady=10)

        Label(output_frame, text=self.lang['output_settings'], font=("Arial", 10, "bold")).pack(anchor="w")

        same_folder_frame = Frame(output_frame)
        same_folder_frame.pack(fill="x", pady=5)

        Checkbutton(same_folder_frame, text=self.lang['save_same_folder'], variable=self.same_folder,
                    command=self.toggle_output).pack(side="left")

        suffix_frame = Frame(output_frame)
        suffix_frame.pack(fill="x", pady=5)

        Label(suffix_frame, text=self.lang['file_suffix']).pack(side="left")
        Entry(suffix_frame, textvariable=self.suffix, width=20).pack(side="left", padx=10)

        folder_select_frame = Frame(output_frame)
        folder_select_frame.pack(fill="x", pady=5)

        Label(folder_select_frame, text=self.lang['output_folder']).pack(side="left")
        self.output_entry = Entry(folder_select_frame, textvariable=self.output_folder, width=40, state="disabled")
        self.output_entry.pack(side="left", padx=10)
        self.output_btn = Button(folder_select_frame, text=self.lang['browse'], command=self.select_output_folder, state="disabled")
        self.output_btn.pack(side="left")

        # Progress bar
        progress_frame = Frame(main_frame)
        progress_frame.pack(fill="x", pady=10)

        self.progress_label = Label(progress_frame, text="")
        self.progress_label.pack(anchor="w")

        self.progressbar = Progressbar(progress_frame, length=400, mode='determinate')
        self.progressbar.pack(fill="x", pady=5)

        self.status_label = Label(progress_frame, text=self.lang['ready'])
        self.status_label.pack(anchor="w")

        # Buttons
        button_frame = Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        self.start_btn = Button(button_frame, text=self.lang['start_button'], command=self.start_compression,
               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", height=2)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=2)

        self.cancel_btn = Button(button_frame, text=self.lang['cancel_button'], command=self.cancel_compression,
               font=("Arial", 12, "bold"), bg="#f44336", fg="white", height=2, state="disabled")
        self.cancel_btn.pack(side="left", fill="x", expand=True, padx=2)

    def update_crf_label(self, *args):
        crf_val = self.crf.get()
        if crf_val <= 18:
            quality = self.lang['quality_high']
        elif crf_val <= 23:
            quality = self.lang['quality_normal']
        elif crf_val <= 28:
            quality = self.lang['quality_low']
        else:
            quality = self.lang['quality_very_low']
        self.crf_label.config(text=f"{crf_val} ({quality})")

    def toggle_output(self):
        state = "disabled" if self.same_folder.get() else "normal"
        self.output_entry.config(state=state)
        self.output_btn.config(state=state)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title=self.lang['select_videos'],
            filetypes=[
                (self.lang['video_files_filter'], "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.mpeg *.mpg"),
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

    def get_video_duration(self, file):
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except:
            return 0

    def get_codec(self):
        codec_map = {
            "H.264 (libx264)": "libx264",
            "H.265 (libx265)": "libx265",
            "VP9": "libvpx-vp9"
        }
        return codec_map.get(self.codec.get(), "libx264")

    def get_resolution(self):
        res = self.resolution.get()
        original_options = [LANGUAGES['tr']['original'], LANGUAGES['en']['original']]
        if res in original_options:
            return None
        res_map = {
            "1920x1080 (Full HD)": "1920:1080",
            "1280x720 (HD)": "1280:720",
            "854x480 (SD)": "854:480",
            "640x360": "640:360"
        }
        return res_map.get(res)

    def get_format_extension(self):
        format_map = {"MP4": ".mp4", "MKV": ".mkv", "WebM": ".webm", "AVI": ".avi"}
        return format_map.get(self.output_format.get(), ".mp4")

    def compress_video(self, source, target, callback=None):
        try:
            cmd = ['ffmpeg', '-y', '-i', source]

            video_codec = self.get_codec()
            cmd.extend(['-c:v', video_codec])

            if video_codec == "libvpx-vp9":
                cmd.extend(['-crf', str(self.crf.get()), '-b:v', '0'])
            else:
                cmd.extend(['-crf', str(self.crf.get())])

            if video_codec != "libvpx-vp9":
                cmd.extend(['-preset', self.preset.get()])

            resolution = self.get_resolution()
            if resolution:
                cmd.extend(['-vf', f'scale={resolution}:force_original_aspect_ratio=decrease'])

            original_options = [LANGUAGES['tr']['original'], LANGUAGES['en']['original']]
            if self.keep_audio.get():
                if self.audio_bitrate.get() in original_options:
                    cmd.extend(['-c:a', 'copy'])
                else:
                    cmd.extend(['-c:a', 'aac', '-b:a', self.audio_bitrate.get()])
            else:
                cmd.extend(['-an'])

            cmd.append(target)

            video_duration = self.get_video_duration(source)

            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            self.active_process = process
            time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.?\d*)')

            for line in process.stderr:
                if self.cancelled:
                    process.terminate()
                    return False, self.lang['cancelled'], 0

                match = time_pattern.search(line)
                if match and video_duration > 0:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    progress = min(100, (current_time / video_duration) * 100)
                    if callback:
                        callback(progress)

            process.wait()

            if process.returncode == 0:
                original_size = os.path.getsize(source)
                new_size = os.path.getsize(target)
                return True, original_size, new_size
            else:
                return False, "FFmpeg error", 0

        except Exception as e:
            return False, str(e), 0
        finally:
            self.active_process = None

    def start_compression(self):
        if not self.ffmpeg_available:
            messagebox.showerror(self.lang['error'], self.lang['ffmpeg_error'])
            return

        if not self.files:
            messagebox.showwarning(self.lang['warning'], self.lang['select_file_warning'])
            return

        if not self.same_folder.get() and not self.output_folder.get():
            messagebox.showwarning(self.lang['warning'], self.lang['select_folder_warning'])
            return

        self.cancelled = False
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

        thread = threading.Thread(target=self.compression_process)
        thread.daemon = True
        thread.start()

    def cancel_compression(self):
        self.cancelled = True
        if self.active_process:
            self.active_process.terminate()

    def compression_process(self):
        total = len(self.files)
        successful = 0
        total_original = 0
        total_new = 0

        for i, file in enumerate(self.files):
            if self.cancelled:
                break

            filename = os.path.basename(file)
            self.progress_label.config(text=self.lang['processing'].format(i+1, total, filename))
            self.progressbar["value"] = 0

            if self.same_folder.get():
                output_dir = os.path.dirname(file)
            else:
                output_dir = self.output_folder.get()

            name, _ = os.path.splitext(filename)
            new_name = name + self.suffix.get() + self.get_format_extension()
            target_path = os.path.join(output_dir, new_name)

            def progress_callback(progress):
                self.progressbar["value"] = progress
                self.root.update_idletasks()

            result, original, new = self.compress_video(file, target_path, progress_callback)

            if result:
                successful += 1
                total_original += original
                total_new += new

        self.start_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

        if self.cancelled:
            self.status_label.config(text=self.lang['cancelled'])
            self.progress_label.config(text="")
            return

        if total_original > 0:
            savings = ((total_original - total_new) / total_original) * 100
            self.status_label.config(
                text=self.lang['completed'].format(
                    successful, total, savings,
                    self.format_size(total_original), self.format_size(total_new)
                )
            )
        else:
            self.status_label.config(text=self.lang['completed_simple'].format(successful, total))

        self.progress_label.config(text="")
        self.progressbar["value"] = 100
        messagebox.showinfo("OK", self.lang['completed_msg'].format(successful, total))

    def format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.2f} GB"


def main():
    root = Tk()
    app = VideoBoyutKucult(root)
    root.mainloop()


if __name__ == "__main__":
    main()
