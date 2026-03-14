import socket                

s = socket.socket() 
port = 12348           
s.connect(('localhost', port)) 

def math():
    s.send(b'1')
    data = input("Enter mathematical operation :")
    s.send(str(data).encode())
    r = s.recv(1024).decode()
    print("Result is :", r) 
    s.close()

def ftp():
    s.send(b'2')
    
    fname = input("Enter Filename :")
    f = open (fname, "rb")
    l = f.read(1024)
    while (l):
        print("sending....")
        s.send(l)
        l = f.read(1024)
    f.close()
    s.close()

def ftp2():
    s.send(b'3')
    
    f = open("server2client.txt",'wb')
    l = s.recv(1024)
    while (l):
        f.write(l)
        l = s.recv(1024)
    f.close()
    print("Success")
    s.close()

while True :

    opt = int(input("1. Mathematical Operation - press 1\n2. Send File - press 2\n3. Recieve file - press 3\n4. Quit - press 4\n----> "))
    if opt == 1 :
       math()
       break
    elif opt == 2:
       ftp()
       break
    elif opt == 3:
       ftp2()
       break
    else :
        break
        s.close()

    


   