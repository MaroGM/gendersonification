from libs.fountain import Fountain
import pandas as pd
import os

class ScreenPlay(Fountain):
	characters = None		# Character Dictionary { Character : Contentlength Integer }
	topcharacters = []	# Sorted List of characters [ Char_mostContent, Char_2nd-mostContent , ... ]
	rawscript = None		# Script broken up in array of Character and Action [ Type , Content ][ Type , Content ] ...
	scriptlength = None		# Total string length of the loaded script
	scenedictionary = None	# 

	def __init__(self, path=None):
		try:
			Fountain.__init__(self, string=None, path=path)
			self.createObjectElements()
			self.createSceneMeta(self.rawscript)
			#self.createSceneDictionary(cutoff)

		except:
			self.throwError('init')


	def throwError(self, errtype):
		if errtype is 'init':
			print "Could not Initialize :("
		elif errtype is 'range':
			print "Requested index is out of range :("


	def createSceneMeta(self, scenelist):
		'''
		Process the script to create meta information
		'''
		scriptlength = 0

		for scene in scenelist:
			scriptlength += len( scene[1] )

		self.scriptlength = scriptlength


	def createObjectElements(self, maxcharacters=6):
		'''
		Processing of Fountain elements to create characters{}, topcharacters[]
		and rawscript[[_][_]]
		'''
		simple_script = []

		for element in self.elements:
			if element.element_type in ['Dialogue', 'Action', 'Character']:
				simple_script.append([element.element_type, element.element_text])

		# Offsetting by one - assumption is that character is followed by dialogue
		offset_list = simple_script[1:]

		output = []
		characters = {}
		for i in range(len(offset_list)):
			if simple_script[i][0] is 'Action':
				output.append([ 'ScriptAction' , simple_script[i][1] ])

			elif simple_script[i][0] is 'Character' and offset_list[i][0] is 'Dialogue':
				character = str(simple_script[i][1])
				# Getting rid of everything that happens after bracket start e.g. (V.O.)
				character = character.split('  (')[0]	# sometimes double space
				character = character.split(' (')[0]	# sometimes single space
				character = character.strip()

				output.append([ character , offset_list[i][1] ])

				if character in characters:
					characters[character] = characters[character] + len( offset_list[i][1] )
				else:
					characters[character] = len( offset_list[i][1] )

		# Get characters with most text
		dfCharacters = pd.DataFrame(list(characters.iteritems()), columns=['character','stringlength'])
		charlist = dfCharacters.sort('stringlength', ascending=False).head(maxcharacters).character.tolist()

		# Set object variables
		self.characters = characters
		self.topcharacters = charlist
		self.rawscript = output




	def createSceneDictionary(self, cutoff):
		scenelist = self.rawscript
		currentscene = 0		# What scene index are we processing?
		
		scenes = []
		while currentscene < len(scenelist):

			scenedict = {}
			count = 0		# How far are we in the progress to the cutoff

			# Loop through until the cutoff has been reached
			while count < cutoff:

				# Stop loop if the currentscene is going out of range
				if currentscene >= len(scenelist): break;

				key = scenelist[currentscene][0]
				entry = len( scenelist[currentscene][1] )

				# Does the whole entry fit into what is left before the cutoff?
				if entry < cutoff - count:
					addcount = entry
					currentscene += 1  # We can increase the scene - all done here
				else:
					addcount = cutoff - count
					scenelist[currentscene][1] = 'x' * (entry - addcount) # Reduce what remains in the current scene

				if key in scenedict:
					scenedict[key] = scenedict[key] + addcount
				else:
					scenedict[key] = addcount
				
				count += addcount

			scenes.append(scenedict)

		self.scenedictionary = scenes

	def sceneComposition(self, sceneindex, toponly=True):
		'''
		Returns a dictionary of components of the requested scene index
		'''
		try:
			# Get the list of top characters and add ScriptAction for Action events
			charlist = self.topcharacters
			#charlist.append('ScriptAction')

			dfSceneComp = pd.DataFrame(list(self.scenedictionary[sceneindex].iteritems()), columns=['character','stringlength'])

			if toponly:
				_charMask = dfSceneComp['character'].map(lambda x: x in charlist )
				dfSceneComp_filtered = dfSceneComp[_charMask]
				out_dictionary = pd.Series(dfSceneComp_filtered.stringlength.values,index=dfSceneComp_filtered.character).to_dict()
			else:
				out_dictionary = pd.Series(dfSceneComp.stringlength.values,index=dfSceneComp.character).to_dict()

			return out_dictionary

		except:
			self.throwError('range')
			return None


	def setMaxCharacters(self, setting):
		dfCharacters = pd.DataFrame(list(self.characters.iteritems()), columns=['character','stringlength'])
		charlist = dfCharacters.sort('stringlength', ascending=False).head(setting).character.tolist()
		self.topcharacters = charlist


	def getTopCharacterName(self, topchar):
		
		try:
			return str(self.topcharacters[topchar])
		except:
			return None


