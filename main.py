import os
import sys

class MemoryFreeSpaceHandling: #name , satrt , end of free space in wich seqment of memory
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

class Binding: # There is a lot of important info about a process and address binding
               #(where is a process , where is end of process , use vm or not , etc)
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
            for i in range(1,self.num_frame):
                self.page_table.append([i, 0])
    
    def address_binding(self, j):
        if j < self.limit:
            if self.vm:
                if self.page_table[j // self.frame_size][1]:
                    return my_memory[self.seq][self.base+(j % self.frame_size)]
                else:
                    num = j // self.frame_size
                    base = num * self.frame_size
                    limit = self.frame_size
                    with open(self.filename, 'rb') as f:
                        file_data = f.read()
                        if j >= len(file_data):
                            raise Exception("Trap")
                        for i in range(limit):
                            if base + i < len(file_data):
                                my_memory[self.seq][self.base + i] = file_data[base + i]
                    return my_memory[self.seq][self.base+(j % self.frame_size)]
            else:
                if j >= self.limit:
                    raise Exception("There is a wrong address binding")
                return my_memory[self.seq][self.base + j]
        else:
            print("Unauthorized access to memory")
            sys.exit(1)
    
    def get_name(self):
        return self.filename

free_memory = []  # list of MemoryFreeSpaceHandling objects
my_memory = [] # memory (the datas move in this list)
memory_management_algorithm = None 
name_base_limit_reg = [] #list of binding objects there is some important information about a process
last_alloc_index = 0  # Pointer for Next Fit algorithm

def get_arr():
    print('Please input the number of free spaces:')
    try:
        n = int(input())
    except ValueError:
        print("Your input was wrong")
        sys.exit(1)
    if n < 0:
        print("The program takes 0 or positive numbers as the number of free spaces.")
        print("Please try again.")
        get_arr()
        return
    for i in range(n):
        print(f'Please input the {i}th space size(bytes):')
        try:
            x = int(input())
        except ValueError:
            print("Your input was wrong")
            sys.exit(1)
        if x < 0:
            print("The program takes 0 or positive numbers as space size.")
            sys.exit(1)
        free_memory.append(MemoryFreeSpaceHandling(i, 0, x))
    
    for i in free_memory:
        my_memory.append([0x00] * i.length())

def set_algorithm():
    global memory_management_algorithm
    print("Choose your algorithm:")
    print("1 - First fit\n2 - Worst fit\n3 - Best fit\n4 - Next fit")
    try:
        choice = int(input())
    except ValueError:
        print("Your input was wrong")
        sys.exit(1)
    if choice == 1:
        memory_management_algorithm = 'First fit'
    elif choice == 2:
        memory_management_algorithm = 'Worst fit'
    elif choice == 3:
        memory_management_algorithm = 'Best fit'
    elif choice == 4:
        memory_management_algorithm = 'Next fit'
    else:
        print("Your choice was wrong")
        set_algorithm()
        

def is_free(): # Are there a free space in memory?
    flag = False
    for i in free_memory:
        if i.length() != 0:
            flag = True
            break
    return flag


def find_space(size, algorithm): # Find free space wicth the process can come there
    global last_alloc_index
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

    elif algorithm == "Next fit":
        start_index = last_alloc_index
        for i in range(start_index, len(free_memory)):
            if free_memory[i].length() >= size:
                last_alloc_index = i
                return i
        for i in range(start_index):
            if free_memory[i].length() >= size:
                last_alloc_index = i
                return i
        return find_space(size, "Worst fit")

    else:
        raise Exception("There is a problem. Try again.")

def store(i, name): #store process name to i th seqment of memory
    global my_memory
    with open(name, 'rb') as f:
        file_data = f.read()
        for j in range(len(file_data)):
            if free_memory[i].length() > j:
                my_memory[i][j+free_memory[i].get_start()] = file_data[j]

def update_free_memory(i, size): #update of free_memmory list this fun is useful after store a process
    if size <= free_memory[i].get_end():
        free_memory[i].set_start(free_memory[i].get_start()+size)
    else:
        free_memory[i].set_start(free_memory[i].get_end())
        
def show_memory_state():
    for i in free_memory:
        if i is not free_memory[-1]:
            print(i.length(),end=' ,')
        else:
            print(i.length())

def get_file(): # get a file frome user an call store fun
    global name_base_limit_reg
    print("Number of files:")
    try:
        n = int(input())
    except ValueError:
        print("Your input was wrong")
        sys.exit(1)
    if n < 0:
        print("The program takes 0 or positive numbers as the number of files.")
        print("Please try again.")
        get_file()
        return
    for i in range(n):
        print(f"Name of file {i}:")
        name = input()
        try:
            size = os.path.getsize(name)
            print(f"{name}'s size is {size} bytes")
            flag = is_free()
            if flag: #There are some free space
                space_index = find_space(size, memory_management_algorithm)
                print(f"{name} should be stored in {space_index}th free space.")
                if free_memory[space_index].length() >= size:
                    name_base_limit_reg.append(Binding(name, free_memory[space_index].get_start(), size, space_index))
                else:
                    name_base_limit_reg.append(Binding(name, free_memory[space_index].get_start(), size, space_index, True))
                    print(f"Virtual memory is being used for file {name}.")
                store(space_index, name)
                update_free_memory(space_index, size)
                print(f"{name} stored successfully")
                print("The state of free memory space is as follows:")
                show_memory_state()
            else: # There is not any free space
                print("Your memory is full, and you can't move any file to memory.")
                run()
                return
        except: # Can't find the file
            print("There is a problem with your file; maybe your file is not in the path.")
            sys.exit(1)

def run(): 
    print("Do you want to run a program?")
    print("1 - Yes\n2 - No")
    try:
        num = int(input())
    except ValueError:
        print("Your input was wrong")
        sys.exit(1)
    if num == 1:
        print("Input file name:")
        name = input()
        print("Input the line which you want to read:")
        j = int(input())
        flag = False
        for i in name_base_limit_reg:
            if i.get_name() == name:
                print(f"Output: {i.address_binding(j)}")
                flag = True
                break
        if flag:
            run()
        else:
            print(f"{name} is not in memory.")
            run()
    elif num == 2:
        print("Do you want to add any file?")
        print("1 - Yes \n2 - No")
        try:
            n = int(input())
        except ValueError:
            print("Your input was wrong")
            sys.exit(1)
        if n == 1:
            get_file()
        else:
            print("The program finished.")
    else:
        print("There is a problem.")
        print("Please try again.")
        run()

if __name__ == "__main__":
    print("Welcome to the Memory Management System")
    get_arr()  #get free memmory 
    set_algorithm() #set memory mangment algorithm
    get_file() #get files
    run()  # read files which in memory


