import tkinter as tk
from tkinter import Text, ttk, StringVar, OptionMenu, filedialog, messagebox
import subprocess
from subprocess import Popen, PIPE
import os

LARGEFONT = ("Verdana", 35)
runningCmd = False
updateStatus = 'incomplete'

# Keymaps
keymapList = []
# Left Hand
leftHand_verticalSwing = 0
# Controller
controller_buttonX = 1
# Left Leg
leftLeg_stepping = 2
# Right Leg
rightLeg_stepping = 3

def writeDefaultConfig():	#Write default mappings to config.txt
	with open('config.txt', 'w') as file:
		file.write('LeftHand_VerticalSwing: ' + 'X' + '\n')
		file.write('Controller_ButtonX: ' + 'Y' + '\n')
		file.write('LeftLeg_Stepping: ' + 'W' + '\n')
		file.write('RightLeg_Stepping: ' + 'S' + '\n')

if (os.path.isfile('config.txt') == False):	#if config.txt does not exist, create one with default config
	writeDefaultConfig()

def readConfig():	#read config from config.txt and save to keymapList[]
	global keymapList
	with open('config.txt', 'r') as file:
		temp = file.read().splitlines()
		for x in range(len(temp)):
			temp[x] = temp[x].split(': ')
		keymapList.clear()
		for x in range(len(temp)):
			keymapList.append(temp[x][1])

	if (not keymapList):
		tk.messagebox.showerror(title="Error", message="config.txt Is Corrupted")

readConfig()

def updateConfigFile():	#Save config from keymapList[] to config.txt
	with open('config.txt', 'w') as file:
		file.write('LeftHand_VerticalSwing: ' + keymapList[leftHand_verticalSwing] + '\n')
		file.write('Controller_ButtonX: ' + keymapList[controller_buttonX] + '\n')
		file.write('LeftLeg_Stepping: ' + keymapList[leftLeg_stepping] + '\n')
		file.write('RightLeg_Stepping: ' + keymapList[rightLeg_stepping] + '\n')

def restoreDefault():
	writeDefaultConfig()
	readConfig()

class tkinterApp(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		container = tk.Frame(self)
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight=1)
		
		self.frames = {}
		for F in (MainPage, leftHandSettings, controllerSettings, leftLegSettings, rightLegSettings, gameProfiles):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky ="nsew")
		self.show_frame(MainPage)

	def show_frame(self, cont):
		if cont == MainPage:
			global updateStatus
			updateStatus = 'incomplete'
		# if (self == '.'):
		leftHandSettings.updateUI(self.get_page("leftHandSettings"))
		controllerSettings.updateUI(self.get_page("controllerSettings"))
		leftLegSettings.updateUI(self.get_page("leftLegSettings"))
		rightLegSettings.updateUI(self.get_page("rightLegSettings"))
		MainPage.updateStatusLabel(self.get_page("MainPage"))

		frame = self.frames[cont]
		frame.tkraise()

	def get_page(self, page_name):	#return page object to interact with widgets
		for page in self.frames.values():
			if str(page.__class__.__name__) == page_name:
				return page
		return None
	

# first window frame MainPage
class MainPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.make_widget(controller)

		title_label = tk.Label(self, text ="MainPage", font = LARGEFONT)
		title_label.grid(row=0, column=0, padx=10, pady=10)
		self.statusLabel = tk.Label(self, text = "")
		self.statusLabel.grid(row=3, column=4, padx=10, pady=10)
		
	def make_widget(self, controller):
		leftHand_btn = ttk.Button(self, text ="Left Hand Settings",command = lambda : controller.show_frame(leftHandSettings))
		leftHand_btn.grid(row = 1, column = 0, padx = 10, pady = 10)

		controller_btn = ttk.Button(self, text ="Controller Settings",command = lambda : controller.show_frame(controllerSettings))
		controller_btn.grid(row = 1, column = 1, padx = 10, pady = 10)

		leftLeg_btn = ttk.Button(self, text ="Left Leg Settings",command = lambda : controller.show_frame(leftLegSettings))
		leftLeg_btn.grid(row = 2, column = 0, padx = 10, pady = 10)

		rightLeg_btn = ttk.Button(self, text ="Right Leg Settings",command = lambda : controller.show_frame(rightLegSettings))
		rightLeg_btn.grid(row = 2, column = 1, padx = 10, pady = 10)

		profiles_btn = tk.Button(self, text="Game Profiles", borderwidth= 5, command = lambda : controller.show_frame(gameProfiles))
		profiles_btn.grid(row=3, column=0, padx=10, pady=10)

		confirm_btn = tk.Button(self, text="Confirm Settings", borderwidth= 5, command = lambda : self.updateSettingsOnPi())
		confirm_btn.grid(row=3, column=1, padx=10, pady=10)
		
		undo_btn = tk.Button(self, text="Undo Changes", borderwidth= 5, command = lambda : [self.statusLabel.config(text="Config Restored!", bg = 'pale green'), readConfig()])
		undo_btn.grid(row=4, column=0, padx=10, pady=10)

		restore_btn = tk.Button(self, text="Restore Default", borderwidth=5, command=lambda: [self.statusLabel.config(text="Default Restored!", bg='pale green'), restoreDefault()])
		restore_btn.grid(row=4, column=1, padx=10, pady=10)
		
	def updateStatusLabel(self):
		if (updateStatus == 'complete'):
			self.statusLabel.config(text="Update Complete!", bg = 'pale green')
		elif (updateStatus == 'error'):
			self.statusLabel.config(text='Update Error!', bg='brown1')
		else:
			self.statusLabel.config(text='', bg=self.cget("background"))

	def updateSettingsOnPi(self):
		global runningCmd, updateStatus
		timeout = False
		if (runningCmd):
			return
		runningCmd = True

		# print('----- Update Settings -----')
		updateConfigFile()
		updateStatus = 'incomplete'
		self.updateStatusLabel()

		process = subprocess.Popen(['scp', 'config.txt', 'pi@raspberrypi.local:/home/pi/INNOSPORT/new_config.txt'],creationflags=0x08000000)
		# process = subprocess.Popen(['scp', 'pi@raspberrypi.local:/home/pi/INNOSPORT/new_config.txt', 'new_config.txt'])
		try:
			process.wait(10)
		except subprocess.TimeoutExpired:
			process.kill()
			timeout = True
		if (process.returncode != 0):
			# if (timeout):
			# 	# print('Error: Timeout ')
			# else:
			# 	# print('Error: Code ' + str(process.returncode))
			updateStatus = 'error'
			self.updateStatusLabel()
			# print('----- Update Terminated -----\n')
		else:
			# print('----- Update Complete -----\n')
			updateStatus = 'complete'
			self.updateStatusLabel()
		runningCmd = False
					

# second window frame leftHandSettings
class leftHandSettings(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		title_label = ttk.Label(self, text ="Left Hand Settings", font = LARGEFONT)
		title_label.grid(row=0, column=0, pady=10, columnspan = 3)

		save_btn = tk.Button(self, text ="Save and Exit", borderwidth= 5, command = lambda : [self.updateKeymapVar(), controller.show_frame(MainPage)])
		save_btn.grid(row=1, column=0, padx=10, pady=10)
		exit_btn = tk.Button(self, text ="Exit Without Saving",borderwidth= 5, command = lambda : controller.show_frame(MainPage))
		exit_btn.grid(row = 1, column = 1, padx = 10, pady = 10)

		gridFrame1 = tk.Frame(self)
		vertical_swing_label = ttk.Label(gridFrame1, text ="Vertical Swing:")
		vertical_swing_label.grid(row = 0, column = 0, padx = 10)
		self.vertical_swing_entry = ttk.Entry(gridFrame1)
		self.vertical_swing_entry.grid(row=0, column=1)
		gridFrame1.grid(row=4, column=0, columnspan = 2, padx=10, pady=10)
		
	def updateUI(self):
		self.vertical_swing_entry.delete(0, 'end')
		self.vertical_swing_entry.insert('end', keymapList[leftHand_verticalSwing])

	def updateKeymapVar(self):
		global keymapList
		keymapList[leftHand_verticalSwing] = self.controller.get_page("leftHandSettings").vertical_swing_entry.get()


# third window frame controllerSettings
class controllerSettings(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		title_label = ttk.Label(self, text ="Controller Settings", font = LARGEFONT)
		title_label.grid(row=0, column=0, pady=10, columnspan = 3)

		save_btn = tk.Button(self, text ="Save and Exit",borderwidth= 5, command = lambda : [self.updateKeymapVar(), controller.show_frame(MainPage)])
		save_btn.grid(row=1, column=0, padx=10, pady=10)
		exit_btn = tk.Button(self, text ="Exit Without Saving",borderwidth= 5, command = lambda : controller.show_frame(MainPage))
		exit_btn.grid(row = 1, column = 1, padx = 10, pady = 10)

		gridFrame1 = tk.Frame(self)
		buttonX_label = ttk.Label(gridFrame1, text ="Button X:")
		buttonX_label.grid(row = 0, column = 0, padx = 10)
		self.buttonX_entry = ttk.Entry(gridFrame1)
		self.buttonX_entry.grid(row=0, column=1)
		gridFrame1.grid(row=4, column=0, columnspan = 2, padx=10, pady=10)
		
	def updateUI(self):
		self.buttonX_entry.delete(0, 'end')
		self.buttonX_entry.insert('end', keymapList[controller_buttonX])

	def updateKeymapVar(self):
		global keymapList
		keymapList[controller_buttonX] = self.controller.get_page("controllerSettings").buttonX_entry.get()

		
class leftLegSettings(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		title_label = ttk.Label(self, text ="Left Leg Settings", font = LARGEFONT)
		title_label.grid(row=0, column=0, pady=10, columnspan = 3)

		save_btn = tk.Button(self, text ="Save and Exit",borderwidth= 5, command = lambda : [self.updateKeymapVar(), controller.show_frame(MainPage)])
		save_btn.grid(row=1, column=0, padx=10, pady=10)
		exit_btn = tk.Button(self, text ="Exit Without Saving",borderwidth= 5, command = lambda : controller.show_frame(MainPage))
		exit_btn.grid(row = 1, column = 1, padx = 10, pady = 10)

		gridFrame1 = tk.Frame(self)
		stepping_label = ttk.Label(gridFrame1, text ="Stepping:")
		stepping_label.grid(row = 0, column = 0, padx = 10)
		self.stepping_entry = ttk.Entry(gridFrame1)
		self.stepping_entry.grid(row=0, column=1)
		gridFrame1.grid(row=4, column=0, columnspan = 2, padx=10, pady=10)
		
	def updateUI(self):
		self.stepping_entry.delete(0, 'end')
		self.stepping_entry.insert('end', keymapList[leftLeg_stepping])

	def updateKeymapVar(self):
		global keymapList
		keymapList[leftLeg_stepping] = self.controller.get_page("leftLegSettings").stepping_entry.get()


class rightLegSettings(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		title_label = ttk.Label(self, text ="Right Leg Settings", font = LARGEFONT)
		title_label.grid(row=0, column=0, pady=10, columnspan = 3)

		save_btn = tk.Button(self, text ="Save and Exit",borderwidth= 5, command = lambda : [self.updateKeymapVar(), controller.show_frame(MainPage)])
		save_btn.grid(row=1, column=0, padx=10, pady=10)
		exit_btn = tk.Button(self, text ="Exit Without Saving",borderwidth= 5, command = lambda : controller.show_frame(MainPage))
		exit_btn.grid(row = 1, column = 1, padx = 10, pady = 10)

		gridFrame1 = tk.Frame(self)
		stepping_label = ttk.Label(gridFrame1, text ="Stepping:")
		stepping_label.grid(row = 0, column = 0, padx = 10)
		self.stepping_entry = ttk.Entry(gridFrame1)
		self.stepping_entry.grid(row=0, column=1)
		gridFrame1.grid(row=4, column=0, columnspan = 2, padx=10, pady=10)
		
	def updateUI(self):
		self.stepping_entry.delete(0, 'end')
		self.stepping_entry.insert('end', keymapList[rightLeg_stepping])

	def updateKeymapVar(self):
		global keymapList
		keymapList[rightLeg_stepping] = self.controller.get_page("rightLegSettings").stepping_entry.get()

class gameProfiles(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		title_label = ttk.Label(self, text ="Game Profiles", font = LARGEFONT)
		title_label.grid(row=0, column=0, pady=10, columnspan = 3)

		save_btn = tk.Button(self, text ="Load Profile",borderwidth= 5, command = lambda : [self.loadProfile(), controller.show_frame(MainPage)])
		save_btn.grid(row=1, column=0, padx=10, pady=10)

		save_btn = tk.Button(self, text ="Save Profile",borderwidth= 5, command = lambda : [self.saveProfile(), controller.show_frame(MainPage)])
		save_btn.grid(row = 1, column = 1, padx = 10, pady = 10)

		delete_btn = tk.Button(self, text ="Delete Profile",borderwidth= 5, command = lambda : [self.deleteProfile(), controller.show_frame(MainPage)])
		delete_btn.grid(row = 2, column = 0, padx = 10, pady = 10)

	def loadProfile(self):
		profile = filedialog.askopenfilename(title='Select Profile',filetypes=[('Text Files' , '*.txt')])
		with open(profile, 'r') as profiletxt:
			temp = profiletxt.read().splitlines()
			with open('config.txt', 'w') as file:
				for x in range(len(temp)):
					file.write(temp[x] + '\n')
		readConfig()

	def saveProfile(self):
		profile = filedialog.asksaveasfile(title='Save Profile', filetypes = [('Text Files', '*.txt')], defaultextension = ['Text File', '*.txt'], mode='a')
		with open(profile.name, 'w') as file:
			file.write('LeftHand_VerticalSwing: ' + keymapList[leftHand_verticalSwing] + '\n')
			file.write('Controller_ButtonX: ' + keymapList[controller_buttonX] + '\n')
			file.write('LeftLeg_Stepping: ' + keymapList[leftLeg_stepping] + '\n')
			file.write('RightLeg_Stepping: ' + keymapList[rightLeg_stepping] + '\n')
		
	def deleteProfile(self):
		profile = filedialog.askopenfilename(title='Select Profile',filetypes=[('Text Files' , '*.txt')])
		os.remove(profile)


app = tkinterApp()
app.title('INNOSPORT_settingsGUI')
app.mainloop()