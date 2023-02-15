from tkinter import *
from tkinter import ttk

number_of_selected_files = 0

if __name__ == "__main__":
    root = Tk()
    root.title("psq2csv converter")
    root.resizable(False, False)
    main_frame = Frame(root)

    head_frame = Frame(main_frame)
    select_files_button = Button(head_frame, text="Select files")
    select_directory_button = Button(
        head_frame, text="Select output directory")
    number_of_selected_files_label = Label(
        head_frame, text="selected: " + str(number_of_selected_files))
    select_files_button.grid(row=0, column=0, sticky="w")
    select_directory_button.grid(row=0, column=1, sticky="w", padx=5)
    number_of_selected_files_label.grid(
        row=0, column=2, sticky="e")
    head_frame.columnconfigure(1, weight=1)
    head_frame.pack(fill=X, expand=False, pady=(0, 5))

    files_list_frame = Frame(main_frame)
    vertical_files_list_scrollbar = Scrollbar(
        files_list_frame, orient=VERTICAL)
    horizontal_files_list_scrollbar = Scrollbar(
        files_list_frame, orient=HORIZONTAL)
    files_listbox = Listbox(files_list_frame, yscrollcommand=vertical_files_list_scrollbar.set,
                            xscrollcommand=horizontal_files_list_scrollbar.set, height=8, state=DISABLED)
    vertical_files_list_scrollbar.config(command=files_listbox.yview)
    horizontal_files_list_scrollbar.config(command=files_listbox.xview)
    files_listbox.grid(row=0, column=0, sticky="ew")
    vertical_files_list_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_files_list_scrollbar.grid(row=1, column=0, sticky="ew")
    files_list_frame.columnconfigure(0, weight=1)
    files_list_frame.pack(fill=X, expand=False, pady=(0, 5))

    output_directory_frame = Frame(main_frame)
    output_directory_label = Label(
        output_directory_frame, text="output directory:")
    horizontal_output_directory_scrollbar = Scrollbar(
        output_directory_frame, orient=HORIZONTAL)
    output_directory_listbox = Listbox(
        output_directory_frame, xscrollcommand=horizontal_output_directory_scrollbar.set, height=1, state=DISABLED)
    horizontal_output_directory_scrollbar.config(
        command=output_directory_listbox.xview)
    output_directory_label.grid(row=0, column=0, sticky="w")
    output_directory_listbox.grid(row=1, column=0, sticky="ew")
    horizontal_output_directory_scrollbar.grid(row=2, column=0, sticky="ew")
    output_directory_frame.columnconfigure(0, weight=1)
    output_directory_frame.pack(fill=X, expand=False, pady=(0, 5))

    footer_frame = Frame(main_frame)
    conversion_progress_bar = ttk.Progressbar(
        footer_frame, orient=HORIZONTAL, mode="determinate")
    convert_button = Button(footer_frame, text="Convert files")
    conversion_progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    convert_button.grid(row=1, column=0)
    footer_frame.columnconfigure(0, weight=1)
    footer_frame.pack(fill=X, expand=False)

    main_frame.pack(padx=5, pady=5)
    root.mainloop()
