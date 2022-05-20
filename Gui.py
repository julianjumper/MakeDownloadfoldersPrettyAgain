import getpass
import os
import pathlib
from tkinter import *
import tkinter as tk
from tkinter import IntVar, StringVar, filedialog
from tkinter.simpledialog import askstring
import tkinter.ttk
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageTk
from downloadOrganizer import File_Handler
from win32api import GetSystemMetrics

global runner

width = int ( GetSystemMetrics(0) / 2 )
height = int ( GetSystemMetrics(1) / 1.8 )  

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Make your Download-Folder great again!')
        self.geometry(f'{width}x{height}')
        self.iconbitmap('./img/icon.ico')
        # self.resizable(False, False)
        self.download_folder = runner.get_download_directory()
        self.destination_folder = runner.get_destination_directory()
        self.categories_dict = runner.get_categories_extensions()
        self.interval = runner.get_interval()
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.grid_columnconfigure(2, weight=1)
        self.setup_gui()
    def update_values(self, current_cat):
        to_add = askstring(f'Add extension', f'Add an extension to category: "{current_cat}"')
        print(f'add {to_add} to {current_cat}')
    def index_categories(self, grid):
        row = 0
        btn_list = []
        for k, v in runner.get_categories_extensions().items():
            tk.Label(grid, text=f'{k}:', font=('Arial', int ( 10 ), 'bold')).grid(column=0, row=row, padx=(20, 0), pady=(0, 1), sticky='w')
            if v is not None:
                values = ''
                for i in v:
                    if values == '':
                        values = i
                    else:
                        values += f', {i}' 
                tk.Label(grid, text=f'{values},', font=('Arial', int ( 10 ), 'bold')).grid(column=1, row=row, padx=(20, 0), pady=(0, 1), sticky='w')
            else:
                tk.Label(grid, text=f'none', font=('Arial', int ( 10 ), 'italic')).grid(column=1, row=row, padx=(20, 0), pady=(0, 1), sticky='w')
            row += 1
    def activate_autostart(self):
        file_path = os.path.dirname(os.path.realpath(__file__))
        ext = os.fsdecode(os.path.realpath(__file__))
        USER_NAME = getpass.getuser()
        bat_path = r'C:/Users/%s/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup' % USER_NAME
        print(ext)
        with open(bat_path + '/' + "DownloadsOrganizer.bat", "w+") as bat_file:
            bat_file.write(f'start "" "{file_path}{ext}"')
    def deactivate_autostart(self):
        USER_NAME = getpass.getuser()
        bat_path = r'C:/Users/%s/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup' % USER_NAME
        if os.path.exists(bat_path + '/' + "DownloadsOrganizer.bat"):
            os.remove(bat_path + '/' + "DownloadsOrganizer.bat")
    def done(self):
        runner.set_download_directory(self.download_folder)
        runner.set_destination_directory(self.destination_folder)
    def save(self, interval, autostart):
        self.interval = interval
        runner.set_interval(interval)
        if autostart:
            self.activate_autostart()
        else:
            self.deactivate_autostart()
        self.done()
        tk.messagebox.showinfo(title='Saved', message='Saved all settings. Click on \'start\' to start the program.')
    def start(self):
        runner.start()
        tk.messagebox.showinfo(title='Starting...', message='Started the program.')
    def stop(self):
        runner.stop()
        tk.messagebox.showinfo(title='Stopping...', message='Successfully stopped the program.')
    def init_settings(self, grid):
        interval_lbl = tk.Label(grid, text='Interval: ', font=('Arial', int ( 10 ), 'bold'))
        interval_lbl.grid(column=0, row=0, padx=(20, 0))
        
        placeholder_spinbox = StringVar(self)
        placeholder_spinbox.set(int(self.interval))
        spinbox = tk.Spinbox(grid, from_=1, to=1000, width=5, textvariable=placeholder_spinbox)
        spinbox.grid(column=1, row=0, padx=(5, 0))
        
        is_autostart = tk.IntVar()
        opt_autostart = tk.Checkbutton(grid, text='Autostart', variable=is_autostart)
        opt_autostart.grid(row=0, column=2, padx=(20,0))
        
        save_btn = tk.Button(grid, text='Save', command=lambda : self.save(spinbox.get(), is_autostart.get()))
        save_btn.grid(column=0, row=1, sticky='w', padx=(20,0), pady=(10,0))
        
        start_btn = tk.Button(grid, text='Start', command=self.start)
        start_btn.grid(column=1, row=1, sticky='w', padx=(40,0), pady=(10,0))
        
        stop_btn = tk.Button(grid, text='Stop', command=self.stop)
        stop_btn.grid(column=2, row=1, sticky='w', padx=(20,0), pady=(10,0))
    def select_download_folder(self, lbl):
        self.download_folder = filedialog.askdirectory()
        lbl['text'] = f'{self.download_folder}'
    def select_destination_folder(self, lbl):
        self.destination_folder = filedialog.askdirectory()
        lbl['text'] = f'{self.destination_folder}'
    def help(self):
        tk.messagebox.showinfo(title='Extensions', message='Please navigate to the installation folder and find the \'settings.ini\' file.\nTo add a category, append a new line at the bottom. To add an extension, append them to the according line, separated by a comma. Please find the included examples.')
    def quit_window(self, icon, item):
        icon.stop()
        runner.stop()
        self.destroy()
    def show_window(self, icon, item):
        icon.stop()
        self.after(0, self.deiconify())
    def hide_window(self):
        self.withdraw()
        image = Image.open('./img/icon.ico')
        menu = (item('Show', self.show_window), item('Quit', self.quit_window))
        icon=pystray.Icon('Downloadfolder Organizer', image, 'Organizer', menu)
        icon.run()
    def setup_gui(self):
        # --------- MAIN GRID ---------
        grid = tk.Frame(self, bd=2)
        grid.pack(fill='x')
        
        # --------- FIRST ROW ---------
        grid1 = tk.Frame(grid, bd=2)
        grid1.grid(column=0, row=0, padx=0, pady=(10, 5), sticky='w')
        
        grid1.grid_columnconfigure(1, weight=1)
        
        foldersetting_lbl = tk.Label(grid1, text='Folder-Settings', font=('Arial', 20, 'bold'))
        foldersetting_lbl.grid(column=0, row=0, padx=20, sticky='w')

        downloadfolder_lbl = tk.Label(grid1, text='Select your Download-Folder...', font=('Arial', int ( 10 ), 'bold'))
        downloadfolder_lbl.grid(column=0, row=1, padx=20, pady=(10,0), sticky='w')
        current_downloadfolder = tk.Label(grid1, text=f'Auswahl:  {self.download_folder}', font=('Arial', int ( 10 ), 'italic'))
        current_downloadfolder.grid(column=0, row=2, padx=20, sticky='w')
        select_download_button = tk.Button(grid1, text='Select...', width=10, command=lambda:self.select_download_folder(current_downloadfolder))
        select_download_button.grid(column=1, row=2)
        
        destinationfolder_lbl = tk.Label(grid1, text='Select your Destination-Folder...', font=('Arial', int ( 10 ), 'bold'))
        destinationfolder_lbl.grid(column=0, row=3, padx=20, pady=(10,0), sticky='w')
        current_destinationfolder = tk.Label(grid1, text=f'Auswahl:  {self.destination_folder}', font=('Arial', int ( 10 ), 'italic'))
        current_destinationfolder.grid(column=0, row=4, padx=20, sticky='w')
        select_destination_button = tk.Button(grid1, text='Select...', width=10, command=lambda:self.select_destination_folder(current_destinationfolder))
        select_destination_button.grid(column=1, row=4)
           
        
        
        # --------- SECOND ROW ---------
        grid2 = tk.Frame(grid, bd=2)
        grid2.grid(column=0, row=1, padx=0, sticky='w')
        
        extensionsetting_lbl = tk.Label(grid2, text='Extensions', font=('Arial', int ( 20 ), 'bold'))
        extensionsetting_lbl.grid(column=0, row=0, padx=20, pady=(10, 0), sticky='w')
        
        extensionsetting_btn = tk.Button(grid2, text='?', width=5, command=self.help)
        extensionsetting_btn.grid(column=1, row=0, padx=20, pady=(10, 0))
        
        sub_grid2 = tk.Frame(grid2, bd=2)
        sub_grid2.grid(column=0, row=1, padx=0, sticky='w')
        
        self.index_categories(sub_grid2)        
        
        
        # --------- THIRD ROW ---------
        grid3 = tk.Frame(grid, bd=2)
        grid3.grid(column=0, row=2, padx=0, sticky='w')
        
        miscsettings_lbl = tk.Label(grid3, text='Settings', font=('Arial', int ( 20 ), 'bold'))
        miscsettings_lbl.grid(column=0, row=0, padx=20, pady=(10, 0), sticky='w')
        
        sub_grid3 = tk.Frame(grid3, bd=2)
        sub_grid3.grid(column=0, row=1, padx=0, sticky='w')
        
        self.init_settings(sub_grid3)

if __name__ == '__main__':
    runner = File_Handler()
    root = GUI()
    root.mainloop()