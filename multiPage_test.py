import os
import tkinter as tk
from tkinter import Text, ttk, StringVar, OptionMenu
import paramiko
import threading
import time

LARGEFONT = ("Verdana", 35)

# SSH param
SSHparam = {
	"port" : "22",
	"hostname" : '192.168.1.131',
	# "hostname" : 'raspberrypi.local',
	"username" : 'pi',
	"password" : 'raspberry'
}
runningCmd = False

#Pre-defined Motion List
handMovements = [
	"Swing",
	"Slash",
	"Horizontal",
	"Vertical"
]
kegMovements = [
	"Stepping",
	"Running"
]

def sshConnectionTest():
	try:
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		print('Paramiko: Test SSH Connection')
		client.connect(**SSHparam)
	except:
		print('Paramiko: Error')
	finally:
		print('Paramiko: Test Complete')
		client.close()
	# print('Paramiko: Test SSH Connection')

def paramikoSendCmd(command):
	global runningCmd
	if (runningCmd):
		return
	try:
		runningCmd = True
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		print('Paramiko: Initiate SSH Connection')
		print("SSH Command: " + command)
		client.connect(**SSHparam)
		(stdin, stdout, stderr) = client.exec_command(command)
		cmd_output = stdout.read()		
		with open('paramiko_log.txt', 'w+') as file:
			file.write(str(cmd_output))
		return 'paramiko_log.txt'
	except:
		print('Paramiko: Error')
	finally:
		print('Paramiko: Close SSH Connection')
		client.close()
		runningCmd = False

class tkinterApp(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		
		container = tk.Frame(self)
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		self.frames = {}

		for F in (MainPage, Page1, Page2):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky ="nsew")

		self.show_frame(MainPage)

	def show_frame(self, cont):
		with open('test.txt', 'a') as f:
			if cont == MainPage:
				f.write('Main Page,\n')
			elif cont == Page1:
				f.write('Page 1,\n')
			elif cont == Page2:
				f.write('Page 2,\n')
		frame = self.frames[cont]
		frame.tkraise()
	
# first window frame MainPage
class MainPage(tk.Frame):
	def __init__(self, parent, controller):
		with open('test.txt', 'w') as f:
			f.write('test txt created\n')

		tk.Frame.__init__(self, parent)

		testVar = StringVar(self)
		testVar.set(handMovements[0])  # default value

		label = ttk.Label(self, text ="MainPage", font = LARGEFONT)
		label.grid(row = 0, column = 4, padx = 10, pady = 10)

		button1 = ttk.Button(self, text ="Settings Page 1",command = lambda : controller.show_frame(Page1))
		button1.grid(row = 1, column = 1, padx = 10, pady = 10)

		button2 = ttk.Button(self, text ="Settings Page 2",command = lambda : controller.show_frame(Page2))
		button2.grid(row=2, column=1, padx=10, pady=10)

		button2 = ttk.Button(self, text="SSH Test", command = lambda : threading.Thread(target=paramikoSendCmd, args=("cd ~",), daemon=True).start())
		button2.grid(row = 3, column = 2, padx = 10, pady = 10)

		gridFrame = tk.Frame(self)
		label = ttk.Label(gridFrame, text ="Motion:")
		dropDownMenu1 = OptionMenu(gridFrame, testVar, *handMovements)
		label.grid(row = 0, column = 0)
		dropDownMenu1.grid(row=0, column=1)
		gridFrame.grid(row = 4, column = 2, padx = 10, pady = 10)
		

# second window frame page1
class Page1(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = ttk.Label(self, text ="Settings Page 1", font = LARGEFONT)
		label.grid(row = 0, column = 4, padx = 10, pady = 10)

		button1 = ttk.Button(self, text ="MainPage",command = lambda : controller.show_frame(MainPage))
		button1.grid(row = 1, column = 1, padx = 10, pady = 10)

		button2 = ttk.Button(self, text ="Settings Page 2",command = lambda : controller.show_frame(Page2))
		button2.grid(row = 2, column = 1, padx = 10, pady = 10)


# third window frame page2
class Page2(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = ttk.Label(self, text ="Settings Page 2", font = LARGEFONT)
		label.grid(row = 0, column = 4, padx = 10, pady = 10)

		button1 = ttk.Button(self, text ="Settings Page 1",command = lambda : controller.show_frame(Page1))
		button1.grid(row = 1, column = 1, padx = 10, pady = 10)

		button2 = ttk.Button(self, text ="MainPage",command = lambda : controller.show_frame(MainPage))
		button2.grid(row = 2, column = 1, padx = 10, pady = 10)


app = tkinterApp()
app.after(2000, threading.Thread(target=sshConnectionTest, daemon=True).start)
app.mainloop()

# scp ${SSH_CLIENT%% *}:D:/HKUST/Year 2/ISDN2002/GUI/test.txt home/pi 