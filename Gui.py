import os
import tkinter as tk
from tkinter import filedialog, messagebox

class MemoryFreeSpaceHandling:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end
    
    def get_start(self):
        return self.start
   
    def set_start(self, size):
        self.start = size
    
    def get_end(self):
        return self.end
    
    def set_end(self, end):
        self.end = end
    
    def length(self):
        return self.end - self.start

class Binding:
    def __init__(self, filename, base, limit, seq, virtual_memory_state=False):
        self.filename = filename
        self.base = base
        self.limit = limit
        self.seq = seq
        self.vm = virtual_memory_state
        if virtual_memory_state:
            self.frame_size = free_memory[seq].length()
            self.num_frame = int(limit / self.frame_size + 0.999)
            self.page_table = [[0, 1]]
            for i in range(self.num_frame - 1):
                self.page_table.append([i, 0])
    
    def address_binding(self, j):
        if self.vm:
            if self.page_table[j // self.frame_size][1]:
                return my_memory[self.seq][j % self.frame_size]
            else:
                num = j // self.frame_size
                base = num * self.frame_size
                limit = self.frame_size
                with open(self.filename, 'rb') as f:
                    file_data = f.read()
                    if j >= len(file_data):
                        raise Exception("trap")
                    for i in range(limit):
                        if base + i < len(file_data):
                            my_memory[self.seq][self.base + i] = file_data[base + i]
                return my_memory[self.seq][j % self.frame_size]
        else:
            if j >= self.limit:
                raise Exception("There is a wrong address binding")
            return my_memory[self.seq][self.base + j]
    
    def get_name(self):
        return self.filename

free_memory = []  # list of MemoryFreeSpaceHandling objects
my_memory = []
memory_management_algorithm = None
name_base_limit_reg = []

def get_arr(num_spaces, spaces):
    global free_memory, my_memory
    for i in range(num_spaces):
        free_memory.append(MemoryFreeSpaceHandling(i, 0, spaces[i]))
    
    for i in free_memory:
        my_memory.append([0x00] * i.length())

def set_algorithm(choice):
    global memory_management_algorithm
    if choice == 1:
        memory_management_algorithm = 'First fit'
    elif choice == 2:
        memory_management_algorithm = 'Worst fit'
    elif choice == 3:
        memory_management_algorithm = 'Best fit'
    else:
        raise ValueError("Invalid choice for algorithm")

def find_space(size, algorithm):
    if algorithm == "First fit":
        for i in range(len(free_memory)):
            if free_memory[i].length() >= size:
                return i
        return find_space(size, "Worst fit")
        
    elif algorithm == "Worst fit":
        w = 0
        for i in range(len(free_memory)):
            if free_memory[i].length() > free_memory[w].length():
                w = i
        return w
    
    elif algorithm == "Best fit":
        b = 0
        flag = False
        for i in range(len(free_memory)):
            if free_memory[i].length() < free_memory[b].length() and free_memory[i].length() >= size:
                b = i
                flag = True
        if flag:
            return b
        else:
            return find_space(size, "Worst fit")
    else:
        raise Exception("There is a problem. Try again.")

def store(i, name):
    global my_memory
    with open(name, 'rb') as f:
        file_data = f.read()
        for j in range(len(file_data)):
            if free_memory[i].length() > j:
                my_memory[i][j] = file_data[j]

def update_free_memory(i, size):
    if size <= free_memory[i].get_end():
        free_memory[i].set_start(size)
    else:
        free_memory[i].set_start(free_memory[i].get_end())

def get_file(files):
    global name_base_limit_reg
    for name in files:
        size = os.path.getsize(name)
        space_index = find_space(size, memory_management_algorithm)
        if free_memory[space_index].length() >= size:
            name_base_limit_reg.append(Binding(name, free_memory[space_index].get_start(), size, space_index))
        else:
            name_base_limit_reg.append(Binding(name, free_memory[space_index].get_start(), size, space_index, True))
        store(space_index, name)
        update_free_memory(space_index, size)

def run_program(file_name, line):
    for i in name_base_limit_reg:
        if i.get_name() == file_name:
            return i.address_binding(line)
    raise Exception("File not found in bindings")

class MemoryManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Manager")
        self.num_spaces = tk.IntVar()
        self.spaces = []
        self.files = []
        self.algorithm = tk.IntVar()
        
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Number of Free Spaces:").pack()
        tk.Entry(self.root, textvariable=self.num_spaces).pack()
        
        tk.Button(self.root, text="Set Free Spaces", command=self.set_free_spaces).pack()
        
        tk.Label(self.root, text="Choose Algorithm:").pack()
        tk.Radiobutton(self.root, text="First Fit", variable=self.algorithm, value=1).pack()
        tk.Radiobutton(self.root, text="Worst Fit", variable=self.algorithm, value=2).pack()
        tk.Radiobutton(self.root, text="Best Fit", variable=self.algorithm, value=3).pack()
        
        tk.Button(self.root, text="Load Files", command=self.load_files).pack()
        tk.Button(self.root, text="Run Program", command=self.run_program).pack()

    def set_free_spaces(self):
        num_spaces = self.num_spaces.get()
        self.spaces = []
        for i in range(num_spaces):
            size = int(input(f"Please input the {i}th space size: "))
            self.spaces.append(size)
        get_arr(num_spaces, self.spaces)

    def load_files(self):
        self.files = filedialog.askopenfilenames(title="Select Files")
        set_algorithm(self.algorithm.get())
        get_file(self.files)
        messagebox.showinfo("Info", "Files loaded successfully!")

    def run_program(self):
        file_name = filedialog.askopenfilename(title="Select File to Run")
        line = int(input("Input the line which you want to read: "))
        try:
            result = run_program(file_name, line)
            messagebox.showinfo("Output", f"Output: {result}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagerGUI(root)
    root.mainloop()
