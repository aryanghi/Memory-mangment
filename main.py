import os

free_memory=[] #list of object class
my_memory=[]
memory_mangment_algorithm=None
name_base_limit_reg=[]

class memory_free_space_handling:
    def __init__(self,name,s,e):
        self.name=name
        self.start=s
        self.end=e
    
    def get_start(self):
        return self.start
   
    def set_start(self,size):
        self.start=size
    
    def get_end(self):
        return self.end
    
    def set_end(self , e):
        self.end=e
    
    def lenght(self):
        return (self.end-self.start)
    
    
class binding:
    def __init__(self,filename,base,limit,seq,virtual_memory_state=False):
        self.filename=filename
        self.base=base
        self.limit=limit
        self.seq=seq
        self.vm=virtual_memory_state
        if virtual_memory_state:
            self.frame_size=free_memory[seq].lenght()
            self.num_frame=int(limit/self.frame_size + 0.999)
            self.page_table=[[0,1]]
            for i in range(self.num_frame-1):
                self.page_table.append([i,0])
    
    
    def address_binding(self,j):
        if self.vm:
            if self.page_table [j//self.frame_size][1]:
                return my_memory[self.seq][j % self.frame_size]
            else:
                num=j//self.frame_size
                base=num*self.frame_size
                limit=self.frame_size
                with open(self.filename ,'rb') as f:
                    filee=f.read()
                    if j>=len(filee):
                        raise("trap")
                    for i in range(limit):
                        if base+i<len(filee):
                            my_memory[self.seq][self.base+i]=filee[base+i]
                return my_memory[self.seq][j % self.frame_size]
        else:
            if j>=self.limit:
                raise("There is a wrong in addres binding")
            return my_memory[self.seq][self.base+j]
    
    def get_name(self):
        return self.filename
    
    
        
def get_arr():
    global free_memory
    global my_memory
    
    n=int(input('please input the number of free space'))
    for i in range(n):
        x=int(input(f'please input the {i}th space:'))
        free_memory.append(memory_free_space_handling(i,0,x))
    
    for i in free_memory:
        my_memory.append([0x00]*i.lenght())
    

def set_algorithm():
    global memory_mangment_algorithm
    print("choice your algorithm")
    print("1-Frist fit\n2-Worst fit\n3-Best fit")
    x=int(input())
    if x==1:
        memory_mangment_algorithm='First fit'
    elif x==2:
        memory_mangment_algorithm="Worst fit"
    elif x==3:
        memory_mangment_algorithm='Best fit'
    else:
        print("your choice was wrionge")
        set_algorithm()
        
        
"return ith of free_memory"
def find_space(size,algorithm):
    if algorithm=="First fit":
        for i in range(len(free_memory)):
            if free_memory[i].lenght()>=size:
                return i
        return(find_space(size , "Worst fit"))
        
            
    elif algorithm=="Worst fit":
        w=0
        for i in range(len(free_memory)):
            if free_memory[i].lenght()>free_memory[w].lenght():
                w=i
        return w
    
    elif algorithm=="Best fit":
        b=0
        flag=False
        for i in range(len(free_memory)):
            if free_memory[i].lenght()<free_memory[b].lenght() and free_memory[i].lenght()>=size:
                b=i
                flag=True
        if flag:
            return b
        else:
            return(find_space(size , "Worst fit"))
    else:
        raise "There is a problem\nTry again"
    
    
def store(i , name ):
    global my_memory
    with open(name,'rb') as f:
        filee=f.read()
        
        for j in range(len(filee)):
            if free_memory[i].lenght()>j:
                my_memory[i][j]=filee[j]
                
        
def update_free_memory(i , size):
    if size<=free_memory[i].get_end():
        free_memory[i].set_start(size)
    else:
        free_memory[i].set_start(free_memory[i].get_end())
    

def get_file():
    global name_base_limit_reg
    n=int(input("number of files:"))
    
    for i in range(n):
        name=input(f"name{i}")
        size=os.path.getsize(name)
        i=find_space(size,memory_mangment_algorithm)
        print(f"{name} should store in {i}th free space")
        if free_memory[i].lenght()>=size:
            name_base_limit_reg.append(binding(name,free_memory[i].get_start(),size,i))
        else:
            name_base_limit_reg.append(binding(name,free_memory[i].get_start(),size,i,True))
            
        store(i , name)
        update_free_memory(i , size)
        

def run():
    print("Do you want to run a program?")
    print("1- Yes \n2- No")
    num=int(input())
    if num==1:
        name=input("input file name:")
        j=int(input("input the line wich you want to read:"))
        for i in name_base_limit_reg:
            if i.get_name()==name:
                print(i.address_binding(j))
                break
    elif num==2:
        print("The program finished")
    else:
        print("There is a problem")

        
if __name__=="__main__":
    get_arr()
    set_algorithm()
    get_file()   
    run()
    
            
            

