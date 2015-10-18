from libs.pysynthmod import *
import numpy as np
from os.path import dirname, basename, join, normpath, isdir
from os import makedirs
# TODO: Create sonification parameters

class Sonification():

	def __init__(self, name, gender, voice):
		self.name = name.lower()
		self.gender = gender.upper()
		self.voice = voice
		self.song = []

	def make_song(self, callback, bpm=150, path=''):
		make_wav(self.song, callback, fn = path + self.name + str(self.voice) + ".wav", bpm = bpm) 

	def songBrick(self, participation, length=2):
		femaletones = ['e5', 'f5', 'c5', 'd5', 'g5', 'a5' ]
		maletones = ['b2', 'a2', 'c3', 'd3', 'e3', 'f3' ]

		if participation == None:
			hex_participation = 'X'
		else: 
			int_participation = int(round(np.interp(participation, [0,100], [0,15])))
			hex_participation = str(hex(int_participation))[-1:].upper()

		note = ''

		if self.gender == 'F':
			note = femaletones[self.voice]
		elif self.gender == 'M':
			note = maletones[self.voice]

		self.song.append( [ note + '*' + hex_participation , length ] )

	def resetSong(self):
		self.song = []

