#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys, wave, struct

def mix_audiofiles(inarray, out, callback):

	f1 = wave.open(inarray[0],'r')
	f2 = wave.open(inarray[1],'r')
	f3 = wave.open(inarray[2],'r')
	f4 = wave.open(inarray[3],'r')
	f5 = wave.open(inarray[4],'r')
	f6 = wave.open(inarray[5],'r')

	fout = wave.open(out,'w')
	fout.setnchannels(6)
	fout.setsampwidth(2)
	fout.setframerate(44100)
	fout.setcomptype('NONE','Not Compressed')
	frames = min(f1.getnframes(), f2.getnframes(), f3.getnframes())

	print "Mixing files, total length %.2f s..." % (frames / 44100.)
	d1 = f1.readframes(frames)
	d2 = f2.readframes(frames)
	d3 = f3.readframes(frames)
	d4 = f4.readframes(frames)
	d5 = f5.readframes(frames)
	d6 = f6.readframes(frames)

	for n in range(frames):
		if not n%(5*44100): print n // 44100, 's'

		callback()

		dout = struct.pack('h', struct.unpack('h', d1[2*n:2*n+2])[0] ) \
		+ struct.pack('h', struct.unpack('h', d2[2*n:2*n+2])[0] ) \
		+ struct.pack('h', struct.unpack('h', d3[2*n:2*n+2])[0] ) \
		+ struct.pack('h', struct.unpack('h', d4[2*n:2*n+2])[0] ) \
		+ struct.pack('h', struct.unpack('h', d5[2*n:2*n+2])[0] ) \
		+ struct.pack('h', struct.unpack('h', d6[2*n:2*n+2])[0] ) 

		fout.writeframesraw(dout)
	fout.close()



