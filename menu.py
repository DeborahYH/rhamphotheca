import urllib
import tkinter
import logging
import customtkinter as ctk
from PIL import Image
from grid import extract_grid
from cards import extract_cards
from urllib.parse import urlparse
from tkinter import filedialog as fd
from CTkMessagebox import CTkMessagebox

logging.basicConfig(level = logging.INFO, 
                    format = "{asctime} {levelname} - {message}",
                    style = "{", 
                    datefmt = "%d/%m/%Y %H:%M",
                    filename = "wiki_aves.log",
                    encoding = "utf-8",
                    filemode = "a")


def radio_event():
    """
    Handles the event when the user selects an option from the radio buttons.

    Option 1 = URL: Enables the URL entry field and disables the button to select a file.
    Option 2 = CSV file: Enables the button to select a file and disables the URL entry field.
    """

    # Disables the button to select a file if the user chooses to enter a URL
    if data_source.get() == 1:
        entry.configure(state = "normal")
        open_button.configure(state = "disabled")

    # Disables the URL entry field if the user chooses to upload a CSV file
    elif data_source.get() == 2:
        entry.configure(state = "disabled")
        open_button.configure(state = "normal")

def select_file():
    """
    Opens a file dialog for the user to select a CSV file. 
    The selected file's name is then displayed on the GUI.
    """

    # Opens a file dialog
    global file_location
    file_location = fd.askopenfilename(
        title = 'Open a file',
        filetypes = (('csv files', '*.csv'),))

    # Extracts the selected file's name
    filename = file_location.split("/")[-1]

    # Displays the file's name on the GUI
    if filename:
        filename_lbl.configure(text=f"Arquivo: {filename}",
                                font = ("Helvetica", 13))

def send_parameters(url):
    """
    Extracts the parameters from the URL given by the user and uses them to call extract_grid().

    Parameters
    ----------
    url : str
        URL containing the parameters to be extracted.
    """

    if url == "":
        messagebox_config["message"] = "Por favor, insira uma URL."
        CTkMessagebox(**messagebox_config)
        return
    
    dict_url = {}
    
    result = urllib.parse.parse_qs(urlparse(url).query)

    for k,v in result.items():
        dict_url[k] = v[0]
    
    if "t" not in dict_url or "c" not in dict_url:
        messagebox_config["message"] = "A URL deve conter os parâmetros 't' e 'c'."
        CTkMessagebox(**messagebox_config)
        return
    else:
        t = dict_url["t"]
        c = dict_url["c"]

    if "s" in dict_url:
        s = dict_url["s"]
        extract_grid(t = t, c = c, s = s)
    else:
        extract_grid(t = t, c = c)

    logging.info(f"Extraction - URL requested: {url}")

def send_file():
    """
    Validates and sends the file selected by the user to be processed by extract_cards().
    If no file is selected, shows an error message and returns without calling extract_cards.
    """

    if filename_lbl.cget("text") == "":
        messagebox_config["message"] = "Por favor, selecione um arquivo .csv."
        CTkMessagebox(**messagebox_config)
        return
    else: 
        extract_cards(file_location)
    
    logging.info(f"Extraction - File requested: {filename_lbl.cget('text')}")

def submit(data_source):
    """
    Calls 2 distinct functions depending on the data source selected by the user.
    
    send_parameters() extracts the parameters from the URL and calls extract_grid() 
    send_file() calls extract_cards() to extract individual records from Wiki Aves

    Parameters
    ----------
    data_source : int
        The user's choice, referring to either:
        - 1 = URL
        - 2 = .csv file
    """

    if data_source == 1:
        send_parameters(entry.get())
    elif data_source == 2:
        send_file()
    else:
        messagebox_config["message"] = "Por favor, selecione uma fonte de dados."
        CTkMessagebox(**messagebox_config)
        return


# CUSTOM TKINTER GUI

button_color = "#1F2D99"
button_hover = "#2D40D3"
radio_border = "#525252"
radio_hover = "#1F2D99"
radio_select = "#2D40D3"
font_title = ("Helvetica", 18, "bold")
font_button = ("Helvetica", 16, "bold")
font_text = ("Helvetica", 15)
msg_window = "#E9E9E9"

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
data_source = tkinter.IntVar(value = 0)

# Radio button configuration
radio_config = {
    "radiobutton_width": 15,
    "radiobutton_height": 15,
    "border_color": radio_border,
    "fg_color": radio_hover,
    "hover_color": radio_select,
    "border_width_unchecked": 2,
    "border_width_checked": 3,
    "font": font_text,
    "variable": data_source,
    "command": radio_event
}

# CTkMessagebox configuration
messagebox_config = {"master": app,
                    "width": 330,
                    "bg_color": msg_window,
                    "fg_color": msg_window,
                    "title": "Erro",
                    "font": font_button,
                    "message": "",
                    "justify": "center",
                    "icon": "cancel",
                    "icon_size": (30, 30),
                    "button_width": 50,
                    "button_color": button_color,
                    "button_hover_color": button_hover,
                    "border_width": 2,
                    "corner_radius": 5}

# Wiki Aves logo
logo = ctk.CTkImage(light_image = Image.open('wiki_aves.png'), dark_image = Image.open('wiki_aves.png'), size = (70,70))
lbl_logo = ctk.CTkLabel(app, text="", image = logo)
lbl_logo.place(relx = 0.5, rely = 0.15, anchor = 'center')

# Radio buttons let the user define whether the data will be extracted from a URL or from a .csv file
radio_lbl = ctk.CTkLabel(app, 
                        font = font_title,
                        text = "Fonte de Dados:")
radio_lbl.place(relx=0.2, rely = 0.3)

radio_btn1 = ctk.CTkRadioButton(app, 
                                text = "URL",
                                value = 1,
                                **radio_config)
radio_btn1.place(relx = 0.2, rely = 0.37)

# URL entry field
entry = ctk.CTkEntry(app, 
                    width=300,
                    font=font_text,
                    state="disabled")
entry.place(relx = 0.2, rely = 0.42)

radio_btn2 = ctk.CTkRadioButton(app,
                                text = "Arquivo CSV",
                                value = 2,
                                **radio_config)
radio_btn2.place(relx = 0.2, rely = 0.52)

# Button lets the user select a .csv file
open_button = ctk.CTkButton(app,
                            height = 30,
                            fg_color = button_color,
                            hover_color = button_hover,
                            text = 'Selecione um arquivo',
                            text_color = "white",
                            text_color_disabled = "#E4E4E4",
                            font = font_button, 
                            state = "disabled",
                            command = select_file
                        )
open_button.place(relx = 0.2, rely = 0.57)

# Displays the selected file's name
filename_lbl = ctk.CTkLabel(app, text="")
filename_lbl.place(relx = 0.2, rely = 0.63)

# Button calls the function to extract data based on the user's choices
submit_btn = ctk.CTkButton(app, 
                            height = 35,
                            width = 80,
                            fg_color = button_color,
                            hover_color = button_hover,
                            text = "Enviar",
                            font = font_button,
                            text_color = "white",
                            command = lambda: submit(data_source.get()))
submit_btn.place(relx=0.5, rely = 0.8, anchor = 'center')

app.mainloop()
