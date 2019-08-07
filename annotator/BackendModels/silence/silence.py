#!/usr/bin/env

import numpy as np
import scipy.io.wavfile as wav
import argparse


def get_silence(wavfilename, threshold=0.02):
	# Read the .wav file
	(rate,sig) = wav.read(wavfilename)
	print(f"rate: {rate}")
	print(f"signal shape: {sig.shape}")

	if sig.shape==2:
		# This means we have two channels
		# Make the necessary adjustments
		channels = 2
		sig = np.average(sig, axis=1)
		threshold *= 1.5
	else:
		channels = 1

	# Get envelope with abs and moving average
	print(f"singal length: {sig.shape}")
	ab = np.abs(sig)
	K = int(rate/100) # was 160
	env = np.empty([len(ab)-K])
	for i in range(K,len(ab)):
		env[i-K] = np.average(ab[i-K:i])

	#Detect
	av = np.average(env)
	t = env < av * threshold
	bs = []
	for i,tt in enumerate(t[1:]):
		if tt != t[i-1]:
			bs.append(i)

	bounds = np.array(bs)
	result = [0]
	for b in bounds:
		if b > result[-1] + 2:
			result.append(b/float(rate))
	result.append(len(sig)/float(rate))

	# Return the list of the outputs
	return result

def main():
	parser = argparse.ArgumentParser(description='Produce a segmentation of the given .wav speech file based on silences.')

	parser.add_argument('-f', nargs=1, required=True, type=str, help='The filename of the .wav (assume a one channel speech signal).')
	parser.add_argument('-c', nargs=1, default=[1], type=int, help='The number of channels in the wav file.')
	parser.add_argument('-t', nargs=1, default=[0.02], type=float, help='The threshold for silence detection.')
	parser.add_argument('-o', nargs=1, type=str, help='The output file to store the found boundaries.')
	parser.add_argument('-m', action='store_true', help='Return results in the MFCC range (default, false: use time range).')

	args = parser.parse_args()
	wavfilename = args.f[0]
	if not(args.c is None):
		ch = float(args.c[0])

	threshold = float(args.t[0])
	
	pr = True
	if not(args.o is None):
		pr = False
        

	# Read the .wav file
	(rate,sig) = wav.read(wavfilename)
	if ch==2:
		sig = np.average(sig, axis=1)
		threshold *= 1.5

	# Get envelope with abs and moving average
	ab = np.abs(sig)
	env = np.empty([len(ab)-160])
	for i in range(160,len(ab)):
		env[i-160] = np.average(ab[i-160:i])

	#Detect
	av = np.average(env)
	t = env < av * threshold
	bs = []
	for i,tt in enumerate(t[1:]):
		if tt != t[i-1]:
			bs.append(i)

	bounds = np.array(bs)
	# Go to mfcc range
	if args.m:
		bounds = bounds/80
		#Refine
		result = [0]
		for b in bounds:
			if b > result[-1] + 2:
				result.append(b)
		result.append(len(sig)/80 - 1)
	else:
		result = [0]
		for b in bounds:
			if b > result[-1] + 2:
				result.append(b/float(rate))
		result.append(len(sig)/float(rate))


	# Get string list of the found boundaries
	st = ' '.join(map(str, result))
	if (pr):
		print(st)
	else:
		outf = open(args.o[0], 'w')
		outf.write(st)
		outf.close()


if __name__ == "__main__":
    main()