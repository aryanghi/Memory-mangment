import os

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
last_alloc_index = 0  # Pointer for Next Fit algorithm

def get_arr():
    print('Please input the number of free spaces:')
    n = int(input())
    for i in range(n):
        print(f'Please input the {i}th space size:')
        x = int(input())
        free_memory.append(MemoryFreeSpaceHandling(i, 0, x))
    
    for i in free_memory:
        my_memory.append([0x00] * i.length())

def set_algorithm():
    global memory_management_algorithm
    print("Choose your algorithm:")
    print("1 - First fit\n2 - Worst fit\n3 - Best fit\n4 - Next fit")
    choice = int(input())
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

def find_space(size, algorithm):
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

def get_file():
    global name_base_limit_reg
    print("Number of files:")
    n = int(input())
    for i in range(n):
        print(f"Name of file {i}:")
        name = input()
        size = os.path.getsize(name)
        space_index = find_space(size, memory_management_algorithm)
        print(f"{name} should be stored in {space_index}th free space")
        if free_memory[space_index].length() >= size:
            name_base_limit_reg.append(Binding(name, free_memory[space_index].get_start(), size, space_index))
        else:
            name_base_limit_reg.append(Binding(name, free_memory[space_index].get_start(), size, space_index, True))
            print(f"Virtual memory is being used for file {name}")
        store(space_index, name)
        update_free_memory(space_index, size)

def run():
    print("Do you want to run a program?")
    print("1 - Yes\n2 - No")
    num = int(input())
    if num == 1:
        print("Input file name:")
        name = input()
        print("Input the line which you want to read:")
        j = int(input())
        for i in name_base_limit_reg:
            if i.get_name() == name:
                print(f"Output: {i.address_binding(j)}")
                break
        run()
    elif num == 2:
        print("The program finished")
    else:
        print("There is a problem")

if __name__ == "__main__":
    print("Welcome to the Memory Management System")
    get_arr()
    set_algorithm()
    get_file()
    run()
