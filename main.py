#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from apptext import AppText
from os.path import dirname, basename, join, normpath, isdir, splitext
from os import makedirs
from screenplay import ScreenPlay
from sonification import Sonification
import libs.audiomixer as amix
from Tkinter import Tk, RIGHT, LEFT, BOTH, RAISED, W, N, S, E, CENTER, StringVar, IntVar, BooleanVar
from ttk import Frame, Button, Style, Label, Entry, Combobox, Menubutton, Radiobutton, Progressbar
from tkFileDialog import askopenfilename
import tkFont


txt = AppText()

class Page(Frame):
	def __init__(self, parent, index=0):
		Frame.__init__(self, parent, height=530, relief=RAISED, borderwidth=1)
		self.parent = parent
		if index == 0:
			self.loadScriptPage()
		elif index == 1:
			self.scriptProcessPage()
		elif index == 2:
			self.sonifyProcessPage()
		elif index == 3:
			self.finishedPage()
		else:
			print "No Page here!"

		
	def loadScriptPage(self):
		
		# Button States
		self.parent.prevButton.config(state='disabled')
		if self.parent.scriptname != '':
			self.parent.nextButton.config(state='normal')

		explain = Label(self, text=txt.selectscript, justify=CENTER, font=root.fontH1)
		explain.pack(pady=50)

		self.loadedscript = Label(self, text=self.parent.scriptname, justify=CENTER, font=root.fontH1)
		self.loadedscript.pack()

		loadscriptBtn = Button(self, text="Load Script", command=self.getScript)
		loadscriptBtn.pack(pady=10)

	def scriptProcessPage(self):
		self.parent.prevButton.config(state='normal')
		self.parent.nextButton.config(state='normal')

		explain = Label(self, text="Character Selection", justify=CENTER, font=root.fontH1)
		explain.grid(row=0, columnspan=3, pady=20)

		# Instance Script
		self.parent.Script = ScreenPlay(normpath(self.parent.scriptpath))

		actorNames = self.parent.Script.topcharacters
		self.actorActive = []
		self.actorGender = []

		for i in range(6):
			Label(self, text=actorNames[i], width=20).grid(row=i+1, padx=10, pady=8)
			participateFrame = Frame(self ,relief=RAISED, borderwidth=1)
			participateFrame.grid(row=i+1,column=1, padx=10, ipady=2, ipadx=5)
			
			participate = BooleanVar()
			self.actorActive.append(participate)
			self.actorActive[i].set(True)

			Radiobutton(participateFrame, text="ON", variable=self.actorActive[i], value=True, command=self.updateVars).pack(side=LEFT)
			Radiobutton(participateFrame, text="OFF",  variable=self.actorActive[i], value=False, command=self.updateVars).pack(side=LEFT)

			genderFrame = Frame(self, relief=RAISED, borderwidth=1)
			genderFrame.grid(row=i+1,column=2, padx=30, ipady=2)
			
			gender = StringVar()
			self.actorGender.append(gender)
			self.actorGender[i].set('F')

			Label(genderFrame, text="Gender:").pack(side=LEFT, padx=10)

			Radiobutton(genderFrame, text="Female", variable=self.actorGender[i], value='F', command=self.updateVars).pack(side=LEFT, padx=5)
			Radiobutton(genderFrame, text="Male",  variable=self.actorGender[i], value='M', command=self.updateVars).pack(side=LEFT, padx=5)

		Label(self, text="______________________", justify=CENTER, state='disabled').grid(row=8, columnspan=3, pady=10)
		Label(self, text="Sonification Settings", justify=CENTER, font=root.fontH1).grid(row=9, columnspan=3, pady=10)

		sonificationFrame = Frame(self)
		sonificationFrame.grid(row=10, columnspan=3)

		Label(sonificationFrame, text="Tone Length", width=22).grid(row=0, column=0)
		self.tonelen = Combobox(sonificationFrame, state='readonly', values=['1/1','1/2','1/4', '1/8'])
		self.tonelen.bind("<<ComboboxSelected>>", self.updateCombobox)
		self.tonelen.current(1)
		self.tonelen.grid(row=0, column=1, padx=10, pady=5)

		Label(sonificationFrame, text="Sonification BPM", width=22).grid(row=1, column=0)
		self.bpm = Combobox(sonificationFrame, state='readonly', values=[100, 120, 140, 160, 180, 200, 220, 240, 260])
		self.bpm.bind("<<ComboboxSelected>>", self.updateCombobox)
		self.bpm.current(4)
		self.bpm.grid(row=1, column=1, padx=10, pady=5)

		Label(sonificationFrame, text="Dialogue Length per Tone", justify=LEFT).grid(row=2, column=0)
		self.dpt = Combobox(sonificationFrame, state='readonly', values=[1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000])
		self.dpt.bind("<<ComboboxSelected>>", self.updateCombobox)
		self.dpt.current(4)
		self.dpt.grid(row=2, column=1, padx=10, pady=5)

		self.submitSettings()

	def submitSettings(self):
		actorSelections = []
		sonifySettings = []

		for i in range(6):
			selected = self.actorActive[i].get()
			gender = self.actorGender[i].get()

			actorSelections.append( [selected , gender ] )

		sonifySettings.append(self.tonelen.get())
		sonifySettings.append(self.bpm.get())
		sonifySettings.append(self.dpt.get())

		self.parent.actorSelections = actorSelections
		self.parent.sonifySettings = sonifySettings
		# print actorSelections
		# print sonifySettings

	def finishedPage(self):
		Label(self, text="Sonification Complete!", justify=CENTER, font=root.fontH1).pack(pady=200)



	def sonifyProcessPage(self):

		Label(self, text="Processing", justify=CENTER, font=root.fontH1).pack(pady=20)

		self.processing = Label(self, text="", justify=CENTER)
		self.processing.pack(pady=20)

		self.pbar = Progressbar(self, orient='horizontal', mode='indeterminate')
		self.pbar.start(10)
		self.pbar.pack()

		self.after(100, self.sonifyProcess)


	def sonifyProcess(self):
		# Create Output Directory
		path = dirname(normpath(self.parent.scriptpath))

		self.outdir = join(path, 'output_' + str(self.parent.movietitle))

		self.tempdir = join(self.outdir, 'temp')
		self.tempdir = join(self.tempdir, '')

		if not isdir(self.tempdir):
			makedirs(self.tempdir)

		notelen = self.parent.sonifySettings[0]
		notelen = int( notelen[-1:] )
		bpm = int( self.parent.sonifySettings[1] )
		cutoff = int( self.parent.sonifySettings[2] )

		# Create dictionary based on settings
		self.parent.Script.createSceneDictionary(cutoff=cutoff)
		sceneAmount = len(self.parent.Script.scenedictionary)

		for index, character in enumerate(self.parent.Script.topcharacters):
			selected = self.parent.actorSelections[index][0]
			gender = self.parent.actorSelections[index][1]

			if selected:
				charSong = Sonification(character, gender, index)

				for scene in range(sceneAmount-1):

					if character in self.parent.Script.sceneComposition(scene):
						textamount = self.parent.Script.sceneComposition(scene)[character]
						participation = ( float(textamount) / float(cutoff) ) * 100
					else:
						participation = None

					self.processing.config(text= 'Creating Audio for ' + character.title())
					self.update()
					charSong.songBrick(participation, length=notelen)

				charSong.make_song(self.update, bpm=bpm, path=self.tempdir)

		self.mergeAudiotracks()
		

	def mergeAudiotracks(self):

		self.processing.config(text='Creating Multichannel Audiofile\nThis can take a while!')
		self.update()

		outfile = join(self.outdir, 'output.wav')
		
		filearray = []

		for index, character in enumerate(self.parent.Script.topcharacters):
			filename = character.lower() + str(index) + '.wav'
			filearray.append( join(self.tempdir, filename) )

		amix.mix_audiofiles(filearray, outfile, self.update)

		self.parent.nextPage()



	def getScript(self):
		scriptpath = askopenfilename(parent=self.parent, filetypes=[('Fountain Script File','.fountain')], title='Select Script')
		self.parent.scriptpath = scriptpath
		self.parent.scriptname = basename(self.parent.scriptpath)
		self.parent.movietitle = splitext(self.parent.scriptname)[0]

		self.loadedscript.config(text=self.parent.scriptname)
		self.parent.nextButton.config(state='normal')


	def updateVars(self):
		self.submitSettings()

	def updateCombobox(self, event):
		self.submitSettings()



class Application(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		self.scriptpath = ''
		self.scriptname = ''

		self.actorSelections = []
		self.sonifySettings = []

		self.activePage = 0
		self.lastPage = 3

		self.initUI(self.activePage)

	def initUI(self, index):

		self.prevButton = Button(self, text="Back", state='disabled', command=self.prevPage)
		self.prevButton.place(x=20,y=550)
		self.nextButton = Button(self, text="Next", state='disabled', command=self.nextPage)
		self.nextButton.place(x=400,y=550)

		self.frame = Page(self, index)
		self.frame.pack(fill=BOTH, expand=False)
		self.frame.pack_propagate(0)
		self.frame.grid_propagate(0)	
	
	def prevPage(self):
		if self.activePage > 0:
			self.activePage -= 1
			self.frame.destroy()
			self.initUI(self.activePage)


	def nextPage(self):
		if self.activePage < self.lastPage:
			self.activePage += 1
			self.frame.destroy()
			self.initUI(self.activePage)

		
if __name__ == "__main__":
	root = Tk()
	root.style = Style()
	root.style.theme_use('clam')

	root.fontH1 = tkFont.Font(size=15)

	root.resizable(width=False, height=False)
	root.title('Gender Sonification')
	root.geometry('500x600')

	app = Application(root)
	app.pack(expand=True, fill=BOTH)

	root.mainloop()