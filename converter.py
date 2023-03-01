import csv
import logging
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


class Converter(tk.Tk):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.WARNING)
        self._conversion_in_progress = False
        self._psq_file_directories_selected = False
        self._output_directory_selected = False
        self._conversion_thread = None
        self._file_selection_thread = None
        self._output_directory = None
        self._number_of_selected_psq_file_directories = 0
        self._psq_file_directories = []
        self._home_directory = os.path.expanduser('~')
        self.title("psq2csv converter")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_closing())
        self._generate_gui()

    def _generate_gui(self):
        self._main_frame = tk.Frame(self)
        self._head_frame = tk.Frame(self._main_frame)
        self._select_files_button = tk.Button(self._head_frame, text="Select files",
                                              command=self._select_and_load_file_directories_thr)
        self._select_directory_button = tk.Button(self._head_frame, text="Select output directory",
                                                  command=self._select_output_directory)
        self._number_of_selected_psq_file_directories_label = \
            tk.Label(self._head_frame,
                     text=f"selected: {self._number_of_selected_psq_file_directories}")
        self._select_files_button.grid(row=0, column=0, sticky="w")
        self._select_directory_button.grid(row=0, column=1, sticky="w", padx=5)
        self._number_of_selected_psq_file_directories_label.grid(row=0, column=2, sticky="e")
        self._head_frame.columnconfigure(1, weight=1)
        self._head_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        self._files_list_frame = tk.Frame(self._main_frame)
        self._vertical_files_list_scrollbar = tk.Scrollbar(self._files_list_frame, orient=tk.VERTICAL)
        self._horizontal_files_list_scrollbar = tk.Scrollbar(self._files_list_frame, orient=tk.HORIZONTAL)
        self._psq_file_directories_listbox = tk.Listbox(self._files_list_frame,
                                                        yscrollcommand=self._vertical_files_list_scrollbar.set,
                                                        xscrollcommand=self._horizontal_files_list_scrollbar.set,
                                                        height=8,
                                                        state=tk.DISABLED)
        self._vertical_files_list_scrollbar.config(command=self._psq_file_directories_listbox.yview)
        self._horizontal_files_list_scrollbar.config(command=self._psq_file_directories_listbox.xview)
        self._psq_file_directories_listbox.grid(row=0, column=0, sticky="ew")
        self._vertical_files_list_scrollbar.grid(row=0, column=1, sticky="ns")
        self._horizontal_files_list_scrollbar.grid(row=1, column=0, sticky="ew")
        self._files_list_frame.columnconfigure(0, weight=1)
        self._files_list_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        self._output_directory_frame = tk.Frame(self._main_frame)
        self._output_directory_label = tk.Label(self._output_directory_frame, text="output directory:")
        self._horizontal_output_directory_scrollbar = tk.Scrollbar(self._output_directory_frame, orient=tk.HORIZONTAL)
        self._output_directory_listbox = tk.Listbox(self._output_directory_frame,
                                                    xscrollcommand=self._horizontal_output_directory_scrollbar.set,
                                                    height=1, state=tk.DISABLED)
        self._horizontal_output_directory_scrollbar.config(command=self._output_directory_listbox.xview)
        self._output_directory_label.grid(row=0, column=0, sticky="w")
        self._output_directory_listbox.grid(row=1, column=0, sticky="ew")
        self._horizontal_output_directory_scrollbar.grid(row=2, column=0, sticky="ew")
        self._output_directory_frame.columnconfigure(0, weight=1)
        self._output_directory_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        self._footer_frame = tk.Frame(self._main_frame)
        self._conversion_progress_bar = ttk.Progressbar(self._footer_frame, orient=tk.HORIZONTAL, mode="determinate")
        self._convert_button = tk.Button(self._footer_frame, text="Convert files",
                                         command=self._convert_psq_files_to_binary_csv_thr, state=tk.DISABLED)
        self._conversion_progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self._convert_button.grid(row=1, column=0)
        self._footer_frame.columnconfigure(0, weight=1)
        self._footer_frame.pack(fill=tk.X, expand=False)
        self._main_frame.pack(padx=5, pady=5)

    def _on_closing(self):
        if not self._conversion_in_progress or \
                messagebox.askquestion("The conversion is in progress",
                                       "Do you really want to exit? The conversion is in progress!") == "yes":
            self.destroy()

    def _select_and_load_file_directories(self):
        filedialog_result_tuple = filedialog.askopenfilenames(initialdir=self._home_directory, title="Select PSQ files",
                                                              filetypes=(("PSQ files", "*.psq"),))
        if not filedialog_result_tuple:
            return
        self._psq_file_directories = [Path(psq_file_directory) for psq_file_directory in filedialog_result_tuple]
        self._psq_file_directories_listbox.config(state=tk.NORMAL)
        self._psq_file_directories_listbox.delete(0, tk.END)
        self._psq_file_directories_listbox.insert(tk.END, *self._psq_file_directories)
        self._psq_file_directories_listbox.config(state=tk.DISABLED)
        self._number_of_selected_psq_file_directories = len(self._psq_file_directories)
        self._number_of_selected_psq_file_directories_label.config(
            text=f"selected: {self._number_of_selected_psq_file_directories}")
        if self._number_of_selected_psq_file_directories != 0:
            self._psq_file_directories_selected = True
        self._change_buttons_state()

    def _select_and_load_file_directories_thr(self):
        self._file_selection_thread = threading.Thread(target=self._select_and_load_file_directories)
        self._file_selection_thread.daemon = True
        self._file_selection_thread.start()

    def _select_output_directory(self):
        filedialog_result = filedialog.askdirectory(initialdir=self._home_directory, title="Select output directory")
        if not filedialog_result:
            return
        self._output_directory = Path(filedialog_result)
        self._output_directory_listbox.config(state=tk.NORMAL)
        self._output_directory_listbox.delete(0, tk.END)
        self._output_directory_listbox.insert(tk.END, self._output_directory)
        self._output_directory_listbox.config(state=tk.DISABLED)
        self._output_directory_selected = True
        self._setup_logger(self._output_directory)
        self._change_buttons_state()

    def _setup_logger(self, output_directory):
        self._logger.handlers.clear()
        formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        file_handler = logging.FileHandler(output_directory.joinpath("conversion.log"), mode="w")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def _change_buttons_state(self):
        if self._conversion_in_progress:
            self._select_files_button.config(state=tk.DISABLED)
            self._select_directory_button.config(state=tk.DISABLED)
            self._convert_button.config(state=tk.DISABLED)
        else:
            self._select_files_button.config(state=tk.NORMAL)
            self._select_directory_button.config(state=tk.NORMAL)
            if self._psq_file_directories_selected and self._output_directory_selected:
                self._convert_button.config(state=tk.NORMAL)

    def _convert_psq_files_to_binary_csv(self):
        self._conversion_in_progress = True
        self._change_buttons_state()
        successfully_converted_files = 0
        for file_directory in self._psq_file_directories:
            board_size, moves = (None, None)
            psq_data = self._get_data_from_psq_file(file_directory)
            if psq_data:
                board_size, moves = self._get_board_size_and_moves_from_psq_data(psq_data, file_directory)
            if board_size and moves and self._create_csv_file(board_size, moves, file_directory):
                successfully_converted_files += 1
            self._conversion_progress_bar["value"] += (100 / self._number_of_selected_psq_file_directories)
        messagebox.showinfo("Conversion complete",
                            f"Successfully converted {successfully_converted_files} of "
                            f"{len(self._psq_file_directories)} files. Errors can be found in the "
                            f"conversion.log file in the output directory.")
        self._conversion_in_progress = False
        self._conversion_progress_bar["value"] = 0
        self._change_buttons_state()

    def _convert_psq_files_to_binary_csv_thr(self):
        self._conversion_thread = threading.Thread(target=self._convert_psq_files_to_binary_csv)
        self._conversion_thread.daemon = True
        self._conversion_thread.start()

    def _get_data_from_psq_file(self, file_directory):
        psq_data = None
        try:
            with open(file_directory, "r") as file:
                psq_data = [line.rstrip('\n') for line in file]
            if not psq_data:
                raise ValueError
        except FileNotFoundError:
            self._logger.error(f"File {file_directory} not found")
        except ValueError:
            self._logger.error(f"File {file_directory} is empty")
        return psq_data

    def _get_board_size_and_moves_from_psq_data(self, psq_data, file_directory):
        board_size = None
        moves = []
        try:
            board_sizes = psq_data[0].split(",")[0].split()[1].split("x")
            if board_sizes[0] == board_sizes[1]:
                board_size = int(board_sizes[0])
            else:
                raise ValueError
        except (IndexError, ValueError):
            self._logger.error(f"Missing or wrong board size format in file {file_directory}")
        else:
            for i in range(1, len(psq_data)):
                line = psq_data[i].split(",")
                if len(line) == 3 and line[0].isdigit() and line[1].isdigit() and line[2].isdigit():
                    if 0 < int(line[0]) <= board_size and 0 < int(line[1]) <= board_size:
                        moves.append((line[0], line[1]))
                    else:
                        self._logger.error(f"Moves outside the scope of the board in file {file_directory}")
                        moves = None
                        break
            if moves and len(moves) != len(set(moves)):
                self._logger.error(f"Duplicate moves encountered in file {file_directory}")
                moves = None
            if not moves and isinstance(moves, list):
                self._logger.error(f"Missing moves in file {file_directory}")
        return board_size, moves

    def _create_csv_file(self, board_size, moves, filename):
        creation_result = False
        csv_directory = self._output_directory.joinpath(f"{filename.stem}.csv")
        if not os.path.exists(csv_directory):
            csv_header = self._create_csv_header_row(board_size)
            csv_data_rows = self._create_csv_data_rows(moves, board_size)
            csv_directory.parent.mkdir(exist_ok=True, parents=True)
            with open(csv_directory, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(csv_header)
                writer.writerows(csv_data_rows)
                creation_result = True
        else:
            self._logger.warning(f"File {csv_directory} already exists")
        return creation_result

    def _create_csv_header_row(self, board_size):
        csv_header_row = ["player"]
        for i in range(1, board_size ** 2 + 1):
            csv_header_row.append(f"0player_field_{i}")
            csv_header_row.append(f"1player_field_{i}")
        for i in range(1, board_size ** 2 + 1):
            csv_header_row.append(f"player_decision_{i}")
        return csv_header_row

    def _create_csv_data_rows(self, moves, board_size):
        csv_data_rows = []
        current_playing_player = None
        performed_moves = []
        moving_decision = []

        def update_moving_decision():
            moving_decision.clear()
            for j in range(1, board_size ** 2 + 1):
                if j == ((board_size * int(moves[i][1])) - (board_size - int(moves[i][0]))):
                    moving_decision.append(1)
                else:
                    moving_decision.append(0)

        def update_performed_moves():
            previous_playing_player = 1 if current_playing_player == 0 else 0
            for j in range(len(performed_moves)):
                if ((board_size * int(moves[i - 1][1])) - (board_size - int(moves[i - 1][0]))) == (j + 1):
                    performed_moves[j * 2 + previous_playing_player] = 1

        for i in range(len(moves) + 1):
            current_playing_player = 0 if i % 2 == 0 else 1
            if i == 0:
                [performed_moves.append(0) for _ in range(board_size ** 2 * 2)]
                update_moving_decision()
            elif i == len(moves):
                update_performed_moves()
                moving_decision.clear()
                [moving_decision.append(0) for _ in range(board_size ** 2)]
            else:
                update_performed_moves()
                update_moving_decision()
            csv_data_rows.append([current_playing_player, *performed_moves, *moving_decision])
        return csv_data_rows


if __name__ == "__main__":
    conv = Converter()
    conv.mainloop()
