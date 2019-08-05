import numpy as np
from features import mfcc
from features import logfbank
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, freqz
from scipy.stats import norm

# Functions for low-pass filter
def butter_lowpass(cutoff, fs, order=5):
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	b, a = butter(order, normal_cutoff, btype='low', analog=False)
	return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
	b, a = butter_lowpass(cutoff, fs, order=order)
	y = lfilter(b, a, data)
	return y

# Compute ACC
def compute_ACC(sig, rate, gold):
	Gamma_mu_0 = np.zeros([len(sig)])
	Gamma_mu_1 = np.zeros([len(sig)])
	Gamma_rho_kappa = np.zeros([len(sig)])
	kappa_tau = np.zeros([len(sig)])
	rho_0 = 1.0/rate
	#print "rho_0:", rho_0, np.log(rho_0)

	for n in range(1,len(sig)):
		Gamma_mu_0[n] = np.abs(sig[n]-sig[n-1])
		if (Gamma_mu_0[n] == 0):
			Gamma_mu_0[n] = 0.0001
	#Gamma_mu_0[0] = sig[0]
	for n in range(1,len(sig)-1):
		Gamma_mu_1[n] = np.abs(sig[n]-sig[n-1]) + np.abs(sig[n+1] - sig[n])
		if (Gamma_mu_1[n] == 0):
			Gamma_mu_1[n] = 0.0001
	#Gamma_mu_1[0] = 0.0001
	#Gamma_mu_1[(len(sig)-1)] = 0.0001
	for n in range(1,len(sig)-1):
		kappa_tau[n] = np.sqrt(np.divide(Gamma_mu_1[n],Gamma_mu_0[n]))
		if (kappa_tau[n] == 0):
			kappa_tau[n] = 0.0001

	Gamma_rho_kappa = np.multiply(kappa_tau,Gamma_mu_0)
	Gamma_rho_kappa = Gamma_rho_kappa[1:len(sig)-1]

	temp = np.average(Gamma_mu_0)

	h = np.zeros([len(Gamma_rho_kappa)])
	h = (np.log(Gamma_rho_kappa) - np.log(temp)) / np.log(rho_0)

	
	x = np.arange(1,len(sig)-1)
	plt.subplot(2, 1, 1)
	plt.plot(x,h)
	for g in gold:
		plt.axvline(g,color='r')
	h_bar = np.average(h)
	#print h_bar
	h_help = h - h_bar
	#print h_help[:10]
	ACC = np.zeros([len(h)-1])
	for n in range(1,len(h)):
		ACC[n-1] = np.sum(h_help[:n])
	
	#print len(x), len(h), len(ACC)
	# Normalise ACC to unity
	ACC = ACC / np.max(ACC)
	
	# Plot ACC
	plt.subplot(2, 1, 2)
	plt.plot(x[1:],ACC)
	for g in gold:
		plt.axvline(g,color='r')
	plt.show()
	return (h,ACC)

# function to compute MSE
def MSE(sig,x1,x2):
	if len(sig)>0:
		y1 = sig[0]
		y2 = sig[-1]
		slope = float(y2-y1)/float(x2-x1+1)
		#print len(sig), x1, y1, x2, y2, y1-slope*x1, slope
		xs = np.arange(x1,x2)
		lin = slope * xs - slope*x1 + y1
		dif = sig - lin
		return np.mean(np.power(dif,2))
	else:
		return 0.0

# second way to compute MSE
def MSE2(sig,x1,x2):
	x = np.array([x1,x2])
	y = np.array([sig[0],sig[-1]])
	z = np.polyfit(x,y,1)
	#print z
	xs = np.arange(x1,x2)
	lin = z[1]*xs + z[0]
	dif = sig - lin
	return np.mean(np.power(dif,2))

# PLA algorithm for boundary detection
def PLA(ACC, epsilon):
	N = len(ACC)
	i = 1
	c = [1]
	k1 = 3
	prev = 0
	while (k1 < N):
		#print MSE(ACC[c[i-1]:k1], c[i-1], k1)
		if (MSE(ACC[c[i-1]:k1], c[i-1], k1) > epsilon):
			#print MSE(ACC[c[i-1]:k1], c[i-1], k1)
			#print k1
			ni = k1
			l = ni - c[i-1]
			E2 = np.empty([l])
			for k2 in range(l):
				E2[k2] = MSE(ACC[c[i-1]:c[i-1]+k2], c[i-1], c[i-1]+k2) + MSE(ACC[c[i-1]+k2:k1], c[i-1]+k2, k1)
			ci = np.argmin(E2) + c[i-1]
			c.append(ci)
			#print c
			#prev = k1
			k1 = c[i]
			i += 1
		k1 += 1
		#if (prev == k1):
		#	break
	return c

# Function fo compute the partial performance measures
def partial(bounds, gold, tolerance, rate):
	NR = float(len(gold))
	NT = float(len(bounds))
	window = tolerance * rate / 1000.0 #tolerance is given in ms
	NH = 0.0
	gold2 = list(gold)
	for b in bounds:
		#print b
		for g in gold2[:]:
			if (np.abs(g-b) < window):
				gold2.remove(g)
				NH += 1.0
				print "Correct boundary:", b, "(gold: ", g, ")"
				break
	# Measures
	HR = NH / NR
	OS = (NT - NR) / NR
	FA = (NT - NH) / NT

	return (HR,OS,FA)

# Function to compute LLRT
def LLRT(Z, X, Y):
	
	H0 = np.sum(norm.pdf(Z,np.mean(Z),np.std(Z)))
	print "H0:", H0
	H1 = np.sum(norm.pdf(X,np.mean(X),np.std(X))) + np.sum(norm.pdf(Y,np.mean(Y),np.std(Y)))
	print "H1:", H1
	Ratio = np.log(H0 / H1)
	print "Ratio:", Ratio
	if Ratio > -0.1:
		return False
	else:
		return True

def refineBoundaries(bounds, SE):
	c = list(bounds)
	c.sort()
	print c
	candidates = [c[0]]
	i = 8
	while (i < len(c)-1):
		if LLRT(SE[c[i-1]:c[i+1]], SE[c[i-1]:c[i]], SE[c[i]:c[i+1]]):
			candidates.append(c[i])
			i += 1
		else:
			# LLR test showed there shouldn't be a boundary here, do nothing
			c.remove(c[i])
		print len(c), c
	return candidates



def main():
	# Read the .wav file
	(rate,sig) = wav.read("0540.wav")
	print "rate: ", rate
	# Read the mfcc features (not needed now)
	#mfcc = np.loadtxt("0540.mfc.txt")
	# Get gold boundaries
	#goldtwo = np.loadtxt("0540.phones", usecols=[0])
	#print len(goldtwo)

	#gold = np.loadtxt("0540.phones", usecols=[0])
	# Jackie's data are stripped off initial silence
	#gold = gold[:-1]
	#gold -= gold[0] 
	# Make it a list for easier manipulation later
	#gold = list(gold)
	#print gold
	goldf = open("khanaga.train.results")
	goldv=goldf.readlines()
	gold2 = goldv[539].split()
	gold = []
	for g in gold2:
		gold.append(int(g))
	print len(gold)

	resf = open("timit.train.goldbounds")
	resv = resf.readlines()
	res2 = resv[539].split()
	res = []
	for r in res2:
		res.append(int(r))
	print len(res)
	# Jackie's data are stripped off initial silence
	#gold = gold[1:]
	#gold -= gold[0] 
	# Make it a list for easier manipulation later
	#gold = list(gold)
	
	#print "Signal shape:",sig.shape
	#print "Sampling frequency:",rate
	# Find mfcc sliding window (for future reference)
	#print "Features shape:", mfcc.shape
	#print "MFCC sample:", np.floor(sig.shape[0] / (mfcc.shape[0] * (rate/1000.0)))
	
	'''
	# Compute ACC on original signal
	(SE1,ACC1) = compute_ACC(sig,rate, gold)
	
	
	# Use Lowpass filter
	order = 6
	cutoff = 1800  # desired cutoff frequency of the filter, Hz
	lowsig = butter_lowpass_filter(sig, cutoff, rate, order)

	# Compute ACC on filtered version
	(SE2,ACC2) = compute_ACC(lowsig,rate)
	
	'''
	# Evaluate against gold for full and low-pass filtered signal
	'''
	(HR1,OS1,FA1) = partial(bounds1, gold, tolerance, rate)
	(HR2,OS2,FA2) = partial(bounds2, gold, tolerance, rate)
	print "full: (HR,OS,FA) = ", (HR1,OS1,FA1)
	print "low-pass (HR,OS,FA) = ", (HR2,OS2,FA2)

	F1_1 = 2*(1-FA1)*HR1 / ((1-FA1+HR1))
	F1_2 = 2*(1-FA2)*HR2 / ((1-FA2+HR2))
	print "full: F1 =", F1_1, "low-pass: F1 =", F1_2
	
	
		

	# Show unfiltered and filtered data
	#t = np.linspace(0,len(sig),1,endpoint=False)
	plt.subplot(1, 1, 1)
	t = np.arange(len(sig))
	print len(t), len(sig)
	plt.plot(t, sig, 'b-', label='data')
	#for g in gold:
	#	plt.axvline(g,color='r')
	for r in res:
		plt.axvline(r,color='r')
	
	#plt.plot(t, lowsig[:0.2*rate], 'g-', linewidth=2, label='filtered data')
	plt.xlabel('Frames')
	plt.grid()
	plt.legend()
	plt.show()
	'''
if __name__ == "__main__":
    main()
