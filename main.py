import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
import keyboard
import pygame
import os
import json
import time

RESPONSES_CSV = 'responses.csv'
CUSTOM_JOB_BOARDS_CSV = 'custom_job_boards.csv'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
ERROR_SOUND = 'error_sound.mp3'
SUCCESS_SOUND = 'success_sound.mp3'
AUDIO_FOLDER = 'audios'
success_sounds = [f'{AUDIO_FOLDER}/{i}.mp3' for i in range(1, 6)]
response_counter = 0
streak_counter = 0

def play_success_sound():
    global response_counter, streak_counter
    if response_counter < 5:
        sound_to_play = SUCCESS_SOUND
    else:
        sound_to_play = success_sounds[response_counter % 5]
    
    response_counter = (response_counter + 1) % 10
    streak_counter = (streak_counter + 1) % 5
    
    pygame.mixer.music.load(sound_to_play)
    pygame.mixer.music.play()

def update_progress_label(data, self):
    today = datetime.now().date()
    today_responses = sum(1 for _, timestamp in data if datetime.strptime(timestamp, DATE_FORMAT).date() == today)
    streak = streak_counter
    self.progress_label.config(text=f"Today progress: {today_responses}\nStreak: {streak}/5")
class JobTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Job Application Response Tracker')
        self.configure(background='#272822')
        self.init_pygame()  
        self.setup_styles()
        self.create_widgets()
        self.load_data()       
        self._selection_made = False

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("Treeview",
                        background="#252526",
                        fieldbackground="#1e1e1e",
                        foreground="#d4d4d4",
                        rowheight=25,
                        font=('Helvetica', 10))
        style.configure("Treeview.Heading",
                        font=('Helvetica', 10, 'bold'),
                        background="#3c3c3c",
                        foreground="#9cdcfe")
        style.map("Treeview",
                background=[('selected', '#094771')],
                foreground=[('selected', '#FFFFFF')])
        style.configure("TButton",
                        background="#3c3c3c",
                        foreground="#d4d4d4",
                        borderwidth=1,
                        font=('Helvetica', 10))
        style.map("TButton",
                background=[('active', '#007acc')],
                foreground=[('active', '#FFFFFF')])
        style.configure("TLabel", background="#1e1e1e", foreground="#d4d4d4")
        style.configure("TCombobox", fieldbackground="#1e1e1e", background="#252526", foreground="#d4d4d4", arrowcolor="#d4d4d4")
        style.map("TCombobox", fieldbackground=[('readonly', '#1e1e1e')], selectbackground=[('readonly', '#1e1e1e')],
                selectforeground=[('readonly', '#d4d4d4')])
        style.configure('Large.TCombobox', font=('Helvetica', 36)) 
        style.configure("Progress.TLabel", font=("Helvetica", 14, "bold"), background="#3c3c3c", foreground="#9cdcfe", padding=10)

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        self.tab1 = ttk.Frame(tab_control, style="TFrame")
        self.tab2 = ttk.Frame(tab_control, style="TFrame")
        tab_control.add(self.tab1, text="Recent Responses", padding=0)
        tab_control.add(self.tab2, text="Summary", padding=0)
        tab_control.pack(expand=1, fill="both")
        tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.tree = ttk.Treeview(self.tab1, columns=('Job Board', 'Timestamp'), show='headings')
        self.tree.heading('Job Board', text='Job Board')
        self.tree.heading('Timestamp', text='Timestamp')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.summary_tree = ttk.Treeview(self.tab2, columns=('Job Board', 'Responses Today', 'Total Responses'), show='headings')
        self.summary_tree.heading('Job Board', text='Job Board')
        self.summary_tree.heading('Responses Today', text='Responses Today')
        self.summary_tree.heading('Total Responses', text='Total Responses')
        self.summary_tree.pack(fill=tk.BOTH, expand=True)

        self.job_board_entry = ttk.Combobox(self, style='Large.TCombobox', values=[row[0] for row in self.load_custom_job_boards()], width=50)
        self.job_board_entry.pack(fill=tk.X, pady=(20, 0))
        self.job_board_entry.bind('<KeyRelease>', self.handle_keyrelease_debounced)
        self.job_board_entry.bind('<<ComboboxSelected>>', self.on_selection)

        update_button = ttk.Button(self, text='Update Counter', command=self.update_response)
        update_button.pack(fill=tk.X, pady=(0, 10))

        delete_button = ttk.Button(self, text="Delete Selected", command=self.delete_selected)
        delete_button.pack(fill=tk.X, pady=(0, 10))

        clear_today_button = ttk.Button(self, text="Clear Today's Data", command=self.clear_today)
        clear_today_button.pack(fill=tk.X, pady=(0, 10))

        keyboard.add_hotkey('f9', self.update_response)

        export_json_button = ttk.Button(self, text="Export to JSON", command=self.export_to_json)
        export_json_button.pack(fill=tk.X, pady=(0, 10))
        import_json_button = ttk.Button(self, text="Import from JSON", command=self.import_from_json)
        import_json_button.pack(fill=tk.X, pady=(0, 10))

        refresh_button = ttk.Button(self, text="Refresh View", command=self.load_data)
        refresh_button.pack(fill=tk.X, pady=(0, 10))

        self.progress_label = ttk.Label(self, text="Today progress: 0\nStreak: 0/5", style="Progress.TLabel", anchor="center")
        self.progress_label.pack(pady=(0, 10))



    def init_pygame(self):
        pygame.mixer.init()

    def play_sound(self, sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    
    def read_data(self, filepath):
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r', newline='', encoding='utf-8') as file:
            return list(csv.reader(file))

    def write_data(self, data, filepath):
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            csv.writer(file).writerows(data)

    def update_response(self):
        job_board = self.job_board_entry.get()
        if not job_board:
            self.job_board_entry.config(foreground='red')
            self.play_sound(ERROR_SOUND)
            return
        self.job_board_entry.config(foreground='white')
        data = self.read_data(RESPONSES_CSV)
        data.append([job_board, datetime.now().strftime(DATE_FORMAT)])
        self.write_data(data, RESPONSES_CSV)
        play_success_sound()
        self.load_data()

    def load_custom_job_boards(self):
        return self.read_data(CUSTOM_JOB_BOARDS_CSV) + [
            ['hh.kz'], ['career.habr.com'], ['dou.ua'], ['getmatch.ru'],
            ['djinni.co'], ['indeed.com'], ['jobs.devby.io'],
            ['djinni.co/jobs'], ['glassdoor.com/Job'], ['wellfound.com/jobs'],
            ['linkedin.com']
        ]

    def load_data(self):    
        self.tree.delete(*self.tree.get_children())
        self.summary_tree.delete(*self.summary_tree.get_children())
        data = self.read_data(RESPONSES_CSV)
        today = datetime.now().date()
        summary = {}
        for job_board, timestamp in data:
            self.tree.insert('', 'end', values=(job_board, timestamp))
            date = datetime.strptime(timestamp, DATE_FORMAT).date()
            if job_board not in summary:
                summary[job_board] = {'today': 0, 'total': 0}
            summary[job_board]['total'] += 1
            if date == today:
                summary[job_board]['today'] += 1
        for job_board, counts in summary.items():
            self.summary_tree.insert('', 'end', values=(job_board, counts['today'], counts['total']))

        update_progress_label(data,self)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            response = messagebox.askyesno("Confirm Deletion", f"Delete this entry?\n{item_values}")
            if response:
                data = self.read_data(RESPONSES_CSV)
                data = [item for item in data if item != list(item_values)]
                self.write_data(data, RESPONSES_CSV)
                self.load_data()

    def clear_today(self):
        today = datetime.now().date().strftime(DATE_FORMAT.split(' ')[0])
        data = self.read_data(RESPONSES_CSV)
        data = [entry for entry in data if not entry[1].startswith(today)]
        self.write_data(data, RESPONSES_CSV)
        self.load_data()

    def on_tab_change(self, event):
        self.load_data()

    def export_to_json(self):
        data = self.read_data(RESPONSES_CSV)
        json_data = [{"Job Board": entry[0], "Timestamp": entry[1]} for entry in data]
        file_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Export Successful", "Data has been exported to " + file_path)

    def import_from_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            csv_data = [[entry['Job Board'], entry['Timestamp']] for entry in data]
            self.write_data(csv_data, RESPONSES_CSV)
            unique_boards = list(set([entry['Job Board'] for entry in data]))
            custom_boards = self.read_data(CUSTOM_JOB_BOARDS_CSV)
            custom_boards_set = set(row[0] for row in custom_boards)
            updated_boards = custom_boards + [[board] for board in unique_boards if board not in custom_boards_set]
            self.write_data(updated_boards, CUSTOM_JOB_BOARDS_CSV)
            self.load_data()
            messagebox.showinfo("Import Successful", "Data has been imported from " + file_path)

    def handle_keyrelease_debounced(self, event):
        if hasattr(self, '_last_key_event_time') and time.time() - self._last_key_event_time < 0.3:
            return
        self._last_key_event_time = time.time()
        self.after(300, lambda: self.update_job_board_values(event))

    def update_job_board_values(self, event):
        value = self.job_board_entry.get()
        data = [row[0] for row in self.load_custom_job_boards()]
        if value:
            filtered_data = [item for item in data if item.lower().startswith(value.lower())]
        else:
            filtered_data = data
        self.job_board_entry['values'] = filtered_data
        if filtered_data:
            self.job_board_entry.event_generate('<Down>')


    def on_selection(self, event):
        self._selection_made = True  
        self.after(500, self.reset_selection_flag)  

    def reset_selection_flag(self):
        self._selection_made = False 

    

if __name__ == '__main__':
    app = JobTrackerApp()
    app.mainloop()
