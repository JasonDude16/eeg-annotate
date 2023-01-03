import re
import time
import mne
import os.path as op
from pathlib import Path
import pandas as pd
from pandastable import Table, TableModel
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')

class App:

    def __init__(self, master):

        self.master = master
        menubar = Menu(self.master)
        self.master.option_add('*tearOff', False)
        self.master.config(menu=menubar)

        file = Menu(menubar)
        file.add_command(label='Add Folder', command=self.folder_opts)
        menubar.add_cascade(menu=file, label='File')

        self.info_frame = ttk.Frame(self.master)
        self.info_frame.config(width=600)
        self.info_frame.grid(column=1, row=0)

        self.data = None
        self.table = Table(self.info_frame, dataframe=self.data)
        self.table.show()

        self.file_frame = ttk.Frame(self.master)
        self.file_frame.config(width=450)
        self.file_frame.grid(column=0, row=0)

        self.tree = ttk.Treeview(self.file_frame)
        self.tree.config(selectmode='browse')
        self.tree.pack()
        
        self.tree.config(columns=('Size', 'Modified'))

        self.tree.column('#0', width=200)
        self.tree.column('Size', width=80, anchor='e')
        self.tree.column('Modified', width=170, anchor='e')

        self.tree.heading('#0', text='Subject')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Modified')

        self.tree.bind('<<TreeviewSelect>>', self.read_and_plot_tree_item)


    def folder_opts(self):

        win = Toplevel(self.master)

        win.title('Add folder options')
        win.resizable(False, False)
        win.lift(self.master)

        fp_lab = Label(win, text='Regex of file(s) to include (e.g., *.csv):')
        fp_lab.grid(row=0, column=0)
        
        fp = ttk.Entry(win)
        fp.insert(0, '*.csv')
        fp.grid(row=0, column=1)

        regex_lab = Label(win, text='Regex of the ID component of the file name (e.g., BASE_[0-9]{3}): ')
        regex_lab.grid(row=1, column=0)
        
        regex = ttk.Entry(win)
        regex.insert(0, 'BASE_[0-9]{3}')
        regex.grid(row=1, column=1)

        def callback():
            self.folder_fp = fp.get()
            self.folder_regex = regex.get()
            win.destroy()
            self.add_to_tree()

        ttk.Button(win, text='Confirm', command=callback).grid(row=2, column=1)

    def add_to_tree(self):
        
        file_path = Path(fd.askdirectory())
        files = sorted(file_path.glob(self.folder_fp))

        if len(files) == 0:
            messagebox.showerror(title='Regex Match', message='No files matching regular expression found!')

        for i in range(len(files)):

            bn = op.basename(files[i])
            idx = re.findall(self.folder_regex, bn)            

            if len(idx) == 0:
                messagebox.showwarning(title='Regex Match', message='Cannot organize all files by given regular expression!')
                break 

            idx = idx[0]
                            
            if self.tree.exists(idx) is False: 
                self.tree.insert('', 'end', idx, text=idx)

            if self.tree.exists(files[i]) is False: 
                self.tree.insert(idx, 'end', files[i], text=bn)

            fs = str(round(op.getsize(files[i]) / 1e6, 2)) + ' mB'
            self.tree.set(files[i], 'Size', fs)

            fm = time.ctime(op.getmtime(files[i]))
            self.tree.set(files[i], 'Modified', fm)
            
    def read_and_plot_tree_item(self, event):
        
        item = self.tree.selection()
        ext = Path(item[0]).suffix
        
        if len(item) > 0 and op.exists(item[0]):
            
            if ext in '.csv':
                self.data = pd.read_csv(item[0])
                
            if ext in '.xlsx':
                self.data = pd.read_excel(item[0])
                    
            if ext in '.txt':
                self.data = pd.read_table(item[0])
                    
            if ext in ['.csv', '.xlsx', 'txt']:
                self.table = Table(self.info_frame, dataframe=self.data, showtoolbar=True, showstatusbar=True)
                self.table.show()

            if ext in '.gz':
                self.data = mne.io.read_raw_fif(item[0])
                canvas = FigureCanvasTkAgg(self.data.plot(), master=self.info_frame)
                canvas.get_tk_widget().grid(column=0, row=0)
                canvas.draw()
            
root = Tk()
app = App(root)
root.mainloop()
