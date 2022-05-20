import os
import pathlib
from random import randint
import sched, time
import threading
import shutil

from pandas import interval_range

global downloads_directory 
global destination_directory 
global interval 

downloads_directory = f'C:/Users/{os.getlogin}/Downloads'
destination_directory = f'C:/Users/{os.getlogin}/Downloads'
interval = 5

# Directories, categories & extensions are saved in 'settings.conf'
def load_settings():
    global downloads_directory, destination_directory, interval
    categories = {} 
    with open('settings.ini', 'r') as f:
        lines = f.readlines()
        line_counter = 0
        category = ''
        for line in lines:
            if line[0] == '_':
                interval = line.split('_')[1]
                continue
            if line[0] == '#':
                continue
            if line[0] == '<' and not line == '\n': # downloads folder from conf-file
                downloads_directory = line.strip().split('<')[1]
            elif line[0] == '>' and not line == '\n': # destination folder 
                destination_directory = line.strip().split('>')[1]
            elif line == '\n': # in case line is empty
                continue
            elif line_counter % 2 == 0:
                category = line.strip()
            else:    
                extensions = line.split(',')
                extensions[len(extensions) - 1] = extensions[len(extensions) - 1].rstrip() # remove \n from last element in array
                categories[category] = extensions
                category = ''
            line_counter += 1
        categories['Misc'] = None
    return categories

def change_download_dir(dir):
    with open('settings.ini', 'r') as f:
        lines = f.readlines()
        line_counter = 0
        index = 0
        for line in lines:
            index += 1
            if line[0] == '_':
                continue
            if line[0] == '#':
                continue
            if line_counter == 0: 
                lines[index - 1] = '<' + dir + '\n'
            elif line == '\n': 
                continue
            line_counter += 1
    with open('settings.ini', 'w') as f:
        f.writelines(lines)

def change_destination_dir(dir):
    with open('settings.ini', 'r') as f:
        lines = f.readlines()
        line_counter = 0
        index = 0
        for line in lines:
            index += 1
            if line[0] == '_':
                continue
            if line[0] == '#':
                continue
            if line_counter == 0: 
                lines[index] = '>' + dir + '\n'
            elif line == '\n': 
                continue
            line_counter += 1
    with open('settings.ini', 'w') as f:
        f.writelines(lines)

def change_interval(interval):
    with open('settings.ini', 'r') as f:
        lines = f.readlines()
        line_counter = 0
        index = 0
        for line in lines:
            index += 1
            if line[0] == '_':
                lines[index-1] = '_' + interval + '\n'
                continue
            if line[0] == '#':
                continue
            if line == '\n': 
                continue
            line_counter += 1
    with open('settings.ini', 'w') as f:
        f.writelines(lines)

class File_Handler:
    def __init__(self) -> None:
        self.categories_extensions = load_settings()
        self.run = False
        self.check_if_created()
        # self.indexing_files()
    def check_if_created (self) -> None:
        for category in self.categories_extensions.keys():
            if not os.path.exists(f'{destination_directory}/Downloaded {category}'):
                os.makedirs(f'{destination_directory}/Downloaded {category}')
    def indexing_files(self) -> None:
        while self.run:
            self.down_directory = os.fsencode(downloads_directory)
            for file in os.listdir(self.down_directory):
                filename = os.fsdecode(file)
                f = os.path.join(downloads_directory, filename)
                if os.path.isfile(f):
                    self.move_file(filename)
            time.sleep(int(interval))
    def move_file(self, filename) -> None:
        suffix = pathlib.Path(filename).suffix.split('.')[1]
        temp_category = 'Misc'
        # fetch category 
        for k, v in self.categories_extensions.items():
            if v is not None:
                for i in v:
                    if i == suffix:
                        temp_category = k
                        break
        # if still empty:
        if temp_category == '': 
            temp_category = 'Misc'
        # move to desired folder
        if os.path.exists(f'{destination_directory}/Downloaded {temp_category}/{filename}'):
            full_file = filename.split('.')
            fname = full_file[0] + str(randint(10, 100000))
            full_file = fname + '.' + full_file[1]
            shutil.move(f'{downloads_directory}/{filename}', f'{destination_directory}/Downloaded {temp_category}/{full_file}')
        else:
            shutil.move(f'{downloads_directory}/{filename}', f'{destination_directory}/Downloaded {temp_category}/{filename}')
    def get_download_directory(self) -> str:
        return downloads_directory
    def get_destination_directory(self) -> str:
        return destination_directory
    def set_download_directory(self, dir):
        change_download_dir(dir)
    def set_destination_directory(self, dir):
        change_destination_dir(dir)
    def get_categories_extensions(self):
        return self.categories_extensions
    def get_interval(self):
        return interval
    def set_interval(self, interval):
        change_interval(interval)
    def start(self):
        self.run = True
        t = threading.Thread(target=self.indexing_files)
        t.start()
    def stop(self):
        self.run = False



"""
<Ziel> 
> Es soll anfangs in einer GUI ausgewaehlt werden koennen, welche Extensions zu welcher Kategorie gehoeren. <
> Downloads-Ordner soll ebenfalls ausgewaehlt werden koennen < 
> Ziel-Order ebenso <
"""