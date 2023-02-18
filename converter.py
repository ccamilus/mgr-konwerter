import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from pathlib import Path
import csv


class Converter(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("psq2csv converter")
        self.parent.resizable(False, False)
        self.parent.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())
        self.conversion_thread = None
        self.is_conversion_in_progress = False
        self.file_selection_thread = None
        self.number_of_selected_files = 0
        self.home_directory = os.path.expanduser('~')
        self.psq_filenames = []
        self.output_directory = None
        self.is_filenames_selected = False
        self.is_output_directory_selected = False
        self.main_frame = tk.Frame(self.parent)
        self.head_frame = tk.Frame(self.main_frame)
        self.select_files_button = tk.Button(
            self.head_frame, text="Select files", command=self.select_and_load_files_thr)
        self.select_directory_button = tk.Button(
            self.head_frame, text="Select output directory", command=self.select_output_directory)
        self.number_of_selected_files_label = tk.Label(
            self.head_frame, text="selected: " + str(self.number_of_selected_files))
        self.select_files_button.grid(row=0, column=0, sticky="w")
        self.select_directory_button.grid(row=0, column=1, sticky="w", padx=5)
        self.number_of_selected_files_label.grid(
            row=0, column=2, sticky="e")
        self.head_frame.columnconfigure(1, weight=1)
        self.head_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        self.files_list_frame = tk.Frame(self.main_frame)
        self.vertical_files_list_scrollbar = tk.Scrollbar(
            self.files_list_frame, orient=tk.VERTICAL)
        self.horizontal_files_list_scrollbar = tk.Scrollbar(
            self.files_list_frame, orient=tk.HORIZONTAL)
        self.files_listbox = tk.Listbox(self.files_list_frame, yscrollcommand=self.vertical_files_list_scrollbar.set,
                                        xscrollcommand=self.horizontal_files_list_scrollbar.set, height=8, state=tk.DISABLED)
        self.vertical_files_list_scrollbar.config(
            command=self.files_listbox.yview)
        self.horizontal_files_list_scrollbar.config(
            command=self.files_listbox.xview)
        self.files_listbox.grid(row=0, column=0, sticky="ew")
        self.vertical_files_list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.horizontal_files_list_scrollbar.grid(row=1, column=0, sticky="ew")
        self.files_list_frame.columnconfigure(0, weight=1)
        self.files_list_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        self.output_directory_frame = tk.Frame(self.main_frame)
        self.output_directory_label = tk.Label(
            self.output_directory_frame, text="output directory:")
        self.horizontal_output_directory_scrollbar = tk.Scrollbar(
            self.output_directory_frame, orient=tk.HORIZONTAL)
        self.output_directory_listbox = tk.Listbox(
            self.output_directory_frame, xscrollcommand=self.horizontal_output_directory_scrollbar.set, height=1, state=tk.DISABLED)
        self.horizontal_output_directory_scrollbar.config(
            command=self.output_directory_listbox.xview)
        self.output_directory_label.grid(row=0, column=0, sticky="w")
        self.output_directory_listbox.grid(row=1, column=0, sticky="ew")
        self.horizontal_output_directory_scrollbar.grid(
            row=2, column=0, sticky="ew")
        self.output_directory_frame.columnconfigure(0, weight=1)
        self.output_directory_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        self.footer_frame = tk.Frame(self.main_frame)
        self.conversion_progress_bar = ttk.Progressbar(
            self.footer_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.convert_button = tk.Button(
            self.footer_frame, text="Convert files", command=self.convert_psq_files_to_binary_csv_thr, state=tk.DISABLED)
        self.conversion_progress_bar.grid(
            row=0, column=0, sticky="ew", pady=(0, 5))
        self.convert_button.grid(row=1, column=0)
        self.footer_frame.columnconfigure(0, weight=1)
        self.footer_frame.pack(fill=tk.X, expand=False)
        self.main_frame.pack(padx=5, pady=5)

    def select_and_load_files(self):
        self.psq_filenames = fd.askopenfilenames(
            initialdir=self.home_directory, title="Select PSQ files", filetypes=(("PSQ files", "*.psq"),))
        if not self.psq_filenames:
            return
        self.files_listbox.config(state=tk.NORMAL)
        self.files_listbox.delete(0, tk.END)
        self.files_listbox.insert(
            tk.END, *[Path(psq_filename) for psq_filename in self.psq_filenames])
        self.files_listbox.config(state=tk.DISABLED)
        self.number_of_selected_files = len(self.psq_filenames)
        self.number_of_selected_files_label.config(
            text="selected: " + str(self.number_of_selected_files))
        if self.number_of_selected_files != 0:
            self.is_filenames_selected = True
        self.check_convertion_possibility()

    def select_and_load_files_thr(self):
        self.file_selection_thread = threading.Thread(
            target=self.select_and_load_files)
        self.file_selection_thread.daemon = True
        self.file_selection_thread.start()

    def select_output_directory(self):
        self.output_directory_listbox.config(state=tk.NORMAL)
        self.output_directory_listbox.delete(0, tk.END)
        output_directory = Path(fd.askdirectory(
            initialdir=self.home_directory, title="Select output directory"))
        if not output_directory:
            return
        self.output_directory = output_directory
        self.output_directory_listbox.insert(tk.END, self.output_directory)
        self.output_directory_listbox.config(state=tk.DISABLED)
        self.is_output_directory_selected = True
        self.check_convertion_possibility()

    def check_convertion_possibility(self):
        if self.is_filenames_selected and self.is_output_directory_selected:
            self.convert_button.config(state=tk.NORMAL)
        else:
            self.convert_button.config(state=tk.DISABLED)

    def convert_psq_files_to_binary_csv(self):
        self.is_conversion_in_progress = True
        self.convert_button.config(state=tk.DISABLED)
        self.select_files_button.config(state=tk.DISABLED)
        self.select_directory_button.config(state=tk.DISABLED)
        successfully_converted_files = 0
        for filename in self.psq_filenames:
            psq_data = self.get_data_from_psq_file(filename)
            board_size, moves = self.get_board_size_and_moves_from_psq_data(
                psq_data, filename)
            if self.create_csv_file(board_size, moves, filename):
                successfully_converted_files += 1
            self.conversion_progress_bar["value"] += (
                100 / self.number_of_selected_files)
        messagebox.showinfo("Conversion complete", "Successfully converted " + str(
            successfully_converted_files) + " of " + str(len(self.psq_filenames)) + " files.")
        self.is_conversion_in_progress = False
        self.conversion_progress_bar["value"] = 0
        self.convert_button.config(state=tk.NORMAL)
        self.select_files_button.config(state=tk.NORMAL)
        self.select_directory_button.config(state=tk.NORMAL)

    def convert_psq_files_to_binary_csv_thr(self):
        self.conversion_thread = threading.Thread(
            target=self.convert_psq_files_to_binary_csv)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def get_data_from_psq_file(self, filename):
        psq_data = None
        if filename:
            try:
                with open(filename, "r") as file:
                    psq_data = [line.rstrip('\n') for line in file]
                if not psq_data:
                    messagebox.showerror(
                        "PSQ file is empty", "The file: " + filename + " is empty!")
            except:
                messagebox.showerror(
                    "File open error", "Cannot open: " + filename)
        return psq_data

    def get_board_size_and_moves_from_psq_data(self, psq_data, filename):
        board_size = None
        moves = []
        if psq_data:
            try:
                board_sizes = psq_data[0].split(",")[0].split()[1].split("x")
                if board_sizes[0] == board_sizes[1]:
                    board_size = int(board_sizes[0])
                else:
                    messagebox.showerror(
                        "Wrong board size", "The board size in the file: " + filename + " is wrong! The length and width of the board must be the same!")
                for i in range(1, len(psq_data)):
                    line = psq_data[i].split(",")
                    if len(line) == 3 and line[0].isdigit() and line[1].isdigit() and line[2].isdigit():
                        moves.append((line[0], line[1]))
            except:
                messagebox.showerror(
                    "Wrong PSQ file", "The data in the file: " + filename + " has wrong format!")
        return board_size, moves

    def create_csv_file(self, board_size, moves, filename):
        creation_result = False
        if board_size and moves and filename:
            csv_directory = Path(self.output_directory).joinpath(
                Path(filename).stem + ".csv")
            if not os.path.exists(csv_directory):
                csv_header = self.create_csv_header(board_size)
                csv_data_rows = self.create_csv_data_rows(
                    moves, board_size, filename)
                if csv_header and csv_data_rows:
                    csv_directory.parent.mkdir(exist_ok=True, parents=True)
                    with open(csv_directory, "w", newline="") as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(csv_header)
                        writer.writerows(csv_data_rows)
                        creation_result = True
            else:
                messagebox.showwarning("CSV file already exists", "The file: " + str(csv_directory) +
                                       " already exists! The conversion for the file: " + str(Path(filename)) + " will be skipped.")
        return creation_result

    def create_csv_header(self, board_size):
        csv_header = ["player"]
        for i in range(1, board_size**2+1):
            csv_header.append("0player_field_" + str(i))
            csv_header.append("1player_field_" + str(i))
        for i in range(1, board_size**2+1):
            csv_header.append("player_decision_" + str(i))
        return csv_header

    def create_csv_data_rows(self, moves, board_size, filename):
        csv_data_rows = []
        current_playing_player = None
        performed_moves = []
        moving_decision = []
        is_data_correct = True

        def check_move_correctness():
            if not 0 < ((board_size * int(moves[i - 1][1])) - (board_size - int(moves[i - 1][0]))) <= board_size**2:
                nonlocal is_data_correct
                is_data_correct = False
                messagebox.showerror(
                    "Wrong coordinates", "Coordinates in the file: " + filename + " are wrong. Conversion of this file will be skipped!")
                return

        def update_moving_decision():
            moving_decision.clear()
            for j in range(1, board_size**2 + 1):
                if j == ((board_size * int(moves[i][1])) - (board_size - int(moves[i][0]))):
                    moving_decision.append(1)
                else:
                    moving_decision.append(0)

        def update_performed_moves():
            for j in range(len(performed_moves)):
                if ((board_size * int(moves[i - 1][1])) - (board_size - int(moves[i - 1][0]))) == (j + 1):
                    if performed_moves[j] == 1:
                        nonlocal is_data_correct
                        is_data_correct = False
                        messagebox.showerror(
                            "Two identical coordinates", "Two identical coordinates found in the file: " + filename + ". Conversion of this file will be skipped!")
                        return
                    performed_moves[j] = 1

        for i in range(len(moves) + 1):
            current_playing_player = 0 if i % 2 == 0 else 1
            if i > 0:
                check_move_correctness()
            if not is_data_correct:
                return None
            if i == 0:
                [performed_moves.append(0) for j in range(board_size**2 * 2)]
                update_moving_decision()
            elif i == len(moves):
                update_performed_moves()
                moving_decision.clear()
                [moving_decision.append(0) for j in range(board_size**2)]
            else:
                update_performed_moves()
                update_moving_decision()
            csv_data_rows.append([current_playing_player] +
                                 performed_moves + moving_decision)
        return csv_data_rows

    def on_closing(self):
        if self.is_conversion_in_progress:
            if messagebox.askquestion("The conversion is in progress", "Do you really want to exit? The conversion is in progress!") == "yes":
                self.parent.destroy()
        else:
            self.parent.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    conv = Converter(root)
    root.mainloop()
