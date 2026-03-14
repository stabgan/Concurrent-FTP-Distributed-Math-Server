import socket
from _thread import *
import threading


def calc(s):
		if '+' in s :
			a,b = s.split('+')
			return float(a)+float(b)
		elif '-' in s:
			a,b = s.split('-')
			return float(a)-float(b)
		elif '*' in s:
			a,b = s.split('*')
			return float(a)*float(b)
		elif '/' in s:
			a,b = s.split('/')
			return float(a)/float(b)
		elif '^' in s:
			a,b = s.split('^')
			return float(a)**float(b)
		else :
			return 0

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('localhost', 12348))
s.listen(7) 
print("Socket is listening...")

def thread_func(c):
	print('Got connection from', addr)
	opt = int(str(c.recv(1024).decode()))
	print(opt)
	while True :
		if opt == 1:
			msg = str(c.recv(1024).decode())
			k = calc(msg)
			c.send(str(k).encode())
		if opt == 2:
			f = open("client2server.txt",'wb')
			l = c.recv(1024)
			while (l):
				f.write(l)
				l = c.recv(1024)
			f.close()
			print("Success")
			break
		if opt ==  3:
		    fname = input("Enter Filename :")
		    f = open (fname, "rb")
		    l = f.read(1024)
		    while (l):
		        print("sending....")
		        c.send(l)
		        l = f.read(1024)
		    f.close()
		    print("Success....\nListening Again.....")
		    break
		else :
			break
	c.close() 
while True: 
	c, addr = s.accept()  
	start_new_thread(thread_func, (c,))     
	
s.close()
