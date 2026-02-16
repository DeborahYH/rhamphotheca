import urllib
import tkinter
import customtkinter as ctk
from PIL import Image
from grid import extract_grid
from cards import extract_cards
from urllib.parse import urlparse
from tkinter import filedialog as fd


def radio_event():
    """
    Handles the event when the user selects an option from the radio buttons.
    """

    # Disables the button to select a file if the user chooses to enter a URL
    if data_source.get() == 1:
        entry.configure(state="normal")
        open_button.configure(state="disabled")

    # Disables the URL entry field if the user chooses to upload a CSV file
    elif data_source.get() == 2:
        entry.configure(state="disabled")
        open_button.configure(state="normal")


def select_file():
    """
    Opens a file dialog for the user to select a CSV file. 
    The selected file's name is then displayed on the GUI.
    """

    filetypes = (('csv files', '*.csv'), ('All files', '*.*'))

    # Opens a file dialog
    file_location = fd.askopenfilename(
        title='Open a file',
        initialdir='C:/Users/User/GitHub/rhamphotheca/wikiaves_data',
        filetypes=filetypes)

    # Extracts the selected file's name
    filename = file_location.split("/")[-1]

    # Displays the file's name on the GUI
    if filename:
        filename_lbl.configure(text=f"Selected file: {filename}",
                                font=("Helvetica", 13))


def send_parameters(url):
    """
    Extracts the parameters from the URL given by the user
    The parameters extracted are used to call extract_grid().
    
    Parameters:
    url (str): URL containing the parameters to be extracted.
    """

    dict_url = {}
    
    result = urllib.parse.parse_qs(urlparse(url).query)

    for k,v in result.items():
        dict_url[k] = v[0]

    t=dict_url["t"]
    c=dict_url["c"]

    if "s" in dict_url:
        s=dict_url["s"]
        extract_grid(t=t, c=c, s=s)
    else:
        extract_grid(t=t, c=c)


def send_file():
    """
    Sends the file selected by the user to be processed by extract_cards().
    If no file is selected, prints a message to the console and returns without calling extract_cards.
    """

    if filename_lbl.cget("text") == "":
        print("No file selected.")
        return
    else: 
        file = filename_lbl.cget("text")
        extract_cards(file=file.split(": ")[1])


def submit(data_source):
    """
    Calls 2 distinct functions depending on the data source selected by the user.
    send_parameters() extracts the parameters from the URL and calls extract_grid() 
    send_file() calls extract_cards() to extract data from Wiki Aves based on the data inside this file
    
    Parameters:
    data_source (int): The user's choice, either 1 (URL) or 2 (CSV file).
    """

    if data_source == 1:
        send_parameters(entry.get())
    elif data_source == 2:
        send_file()
    else:
        print("Erro, opção inválida")


# CUSTOM TKINTER GUI

# Creates the main window on the center of the screen
app = ctk.CTk()
app.title("Wiki Aves - Menu")

window_width, window_height = 500, 500
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
app.geometry(f"{window_width}x{window_height}+{x}+{y}")


# MENU ELEMENTS

# Radio button variable
data_source = tkinter.IntVar(value=0)

# Wiki Aves logo
logo = ctk.CTkImage(light_image = Image.open('wiki_aves.png'), dark_image = Image.open('wiki_aves.png'), size=(70,70))
lbl_logo = ctk.CTkLabel(app, text="", image = logo)
lbl_logo.place(relx = 0.5, rely = 0.15, anchor = 'center')

# Radio buttons allow the user to define whether the data will be extracted from a URL or from a CSV file
radio_lbl = ctk.CTkLabel(app, font=("Helvetica", 18, "bold"), text="Choose the data source:")
radio_lbl.place(relx=0.2, rely = 0.3)
radio_btn1 = ctk.CTkRadioButton(app, 
                                radiobutton_width=15,
                                radiobutton_height=15,
                                border_width_unchecked=2,
                                border_width_checked=4,
                                font=("Helvetica", 15),
                                text="URL",
                                variable=data_source, 
                                value=1,
                                command=radio_event)
radio_btn1.place(relx=0.2, rely = 0.37)

# URL entry field
entry = ctk.CTkEntry(app, 
                    width=300,
                    font=("Helvetica", 15),
                    state="disabled")
entry.place(relx=0.2, rely = 0.42)

radio_btn2 = ctk.CTkRadioButton(app,
                                radiobutton_width=15,
                                radiobutton_height=15,
                                border_width_unchecked=2,
                                border_width_checked=4,
                                font=("Helvetica", 15),
                                text="CSV File",
                                variable=data_source,
                                value=2,
                                command=radio_event)
radio_btn2.place(relx=0.2, rely = 0.52)

# Button opens a file dialog where the user can select a file
open_button = ctk.CTkButton(app,
                            height=30,
                            text='Choose a File',
                            text_color="white",
                            font=("Helvetica", 16, "bold"), 
                            state="disabled",
                            command=select_file
                        )
open_button.place(relx=0.2, rely = 0.57)

# Displays the selected file's name once the user selects a file
filename_lbl = ctk.CTkLabel(app, text="")
filename_lbl.place(relx=0.2, rely = 0.63)

# Calls the function to extract data based on the user's choices
submit_btn = ctk.CTkButton(app, 
                            height=30,
                            text="Enviar",
                            font=("Helvetica", 16, "bold"),
                            text_color="white",
                            command=lambda: submit(data_source.get()))
submit_btn.place(relx=0.5, rely = 0.8, anchor = 'center')

app.mainloop()
