from __future__ import division
import numpy as np
import uproot
import sys
import matplotlib.pyplot as plt
import os
import pickle
from tqdm import tqdm
from prettytable import PrettyTable

from Utils.combXS import *
from Datasets.Signal.Wto3l import *
from Datasets.Run2017.Data import *
from Datasets.Run2017.Background import *
from Skimmer.AnalysisSkimmer import *
from Skimmer.FakeSkimmer import *
from Skimmer.ZSelector import *
from Plotter.Plot import *
from FakeRate.Fake_calc import *
from FakeRate.Fake_weight import *

#Define parameters from plotting
#samples = background_samples + data_samples
samples = ["WZTo3LNu","ZZTo4L","data"]
files = combFiles(signal_samples, background_samples, data_samples, signal_files, background_files, data_files)

lumi = 41.4*1000
error_on_MC = False
pt_bins = [5,10,15,20,30,60]
#pt_bins = [5,10,15,20,30,40,60]
#pt_bins = [5,10,15,20,30,45,60,80,100]

out_dir = "FakeRate_newOpt_5"
if not os.path.exists("/orange/avery/nikmenendez/Output/%s/"%(out_dir)): os.makedirs("/orange/avery/nikmenendez/Output/%s/"%(out_dir))
if not os.path.exists("/orange/avery/nikmenendez/pickle/%s/"%(out_dir)): os.makedirs("/orange/avery/nikmenendez/pickle/%s/"%(out_dir))

# CALCULATE FAKERATE

plots = [

# 1D Plots
#[Title,save name,variable plotted,nBins,low,high,unit,plot data]
["3 Lep Invariant Mass","calc_m3l","m3l",100,0,200,"GeV",True],
["Electron Pair Mass","calc_mass1","M1",100,0,200,"GeV",True],
["Muon pT","calc_pTL3","pTL3",30,0,60,"GeV",True],
["Pass pT","calc_passpT","pTL3",pt_bins,0,60,"GeV",True,"pass"],
["Fail pT","calc_failpT","pTL3",pt_bins,0,60,"GeV",True,"fail"],
["3 Lep + MET Transverse Mass","calc_mt","mt",100,0,300,"GeV",True],
["Transverse Missing Energy","calc_met","met",50,0,250,"GeV",True],
["Transver Missing Energy Phi","calc_met_phi","met_phi",40,-4,4,"phi",True],
["Electron Pair Transverse Mass","calc_M1T","M1T",100,0,200,"GeV",True],
["Number of Electrons","calc_nElec","nElectrons",6,0,6,"n",True],
["Number of Leptons","calc_nLep","nLeptons",6,0,6,"n",True],
["Number of Good Leptons","calc_nGoodLep","nGoodLeptons",6,0,6,"n",True],
["3 Mu pT","calc_m3l_pt","m3l_pt",150,0,150,"GeV",True],
["dR Between Leading and Subleading","calc_dR12","dR12",100,0,6,"dR",True],
["dR Between Leading and Muon","calc_dR13","dR13",100,0,6,"dR",True],
["dR Between Subleading and Muon","calc_dR23","dR23",100,0,6,"dR",True],
["Muon eta","calc_etaL3","etaL3",60,-3.,3.,"eta",True], 
["Muon phi","calc_phiL3","phiL3",40,-4.,4.,"phi",True], 
["Muon Isolation","calc_IsoL3","IsoL3",50,0.,0.2,"pfRelIso03_all",True], 
["Muon 3D Impact Parameter","calc_ip3dL3","ip3dL3",25,0.,0.05,"IP3D",True], 
["Muon Significance of 3D Impact Parameter","calc_sip3dL3","sip3dL3",40,0.,4.,"SIP3D",True], 

]

print("Calculating Fake Rate and Fake Weight")
xs, sumW = combXS(xs_sig,sumW_sig,xs_bkg,sumW_bkg)
effs = {}
for i in range(len(samples)):
	if "data" not in samples[i]:
		weight = xs[samples[i]]/sumW[samples[i]]*lumi
	else:
		weight = xs[samples[i]]/sumW[samples[i]]
	if "Wto3l" in samples[i]: sType = "sig"
	elif "data" in samples[i]: sType = "data"
	else: sType = "MC"	

	file = uproot.open(files[samples[i]])
	events = file["passedEvents"]

	vars_in = signal_vars
	temp = events.arrays(vars_in)

	data = {}
	for key in temp: data[key.decode("utf-8")] = temp[key]
	del temp
	data["weight"] = weight
	data["sType"] = sType
	if "data" not in samples[i]:
		data["pileupWeight"] = data["pileupWeight"]/32
	print("Processing %s with %i events"%(samples[i],len(data["nMuons"])))

	# Select other variables
	print(data["nLeptons"])
	data = select(data)

	# Perform Cuts
	data["selection"],effs[samples[i]] = skim(data)

	data["selection_pass"], data["selection_fail"] = fake_skim(data)

	# Save resulting data
	with open("/orange/avery/nikmenendez/pickle/%s/%s.p"%(out_dir,samples[i]),'wb') as handle:
		pickle.dump(data, handle)

data = {}
for i in range(len(samples)):
	with open("/orange/avery/nikmenendez/pickle/%s/%s.p"%(out_dir,samples[i]),'rb') as handle:
		data[samples[i]] = pickle.load(handle)

print("Efficiencies of each cut:")
cuts = ["Sample"]
for key in effs[samples[0]]:
	cuts.append(key)
x = PrettyTable(cuts)
for key in effs:
	row = [key]
	for key2 in effs[key]:
		row.append("%.2f%%"%(effs[key][key2]))
	x.add_row(row)
table = open("/orange/avery/nikmenendez/Output/%s/Efficiency_Table.txt"%(out_dir),"w")
table.write(x.get_string())
table.close()
print(x)

fake_weight_b, fake_weight_e = fake_calc(data,samples,pt_bins,out_dir)
print("pT bins:")
print(pt_bins)
print("Fake Weight in barrel:")
print(fake_weight_b)
print("Fake Weight in endcap:")
print(fake_weight_e)

# Make Plots
print("Generating Plots")
for p in tqdm(plots):
	plot(data,p,samples,error_on_MC,out_dir)


# APPLY AND VALIDATE FAKE RATE

print("")
print("Applying and Validating Fake Weight")

samples = ["WZTo3LNu","ZZTo4L","fake","data"]
files = combFiles(signal_samples, background_samples, data_samples, signal_files, background_files, data_files)

plots = [

# 1D Plots
#[Title,save name,variable plotted,nBins,low,high,unit,plot data]
["3 Lep Invariant Mass","val_m3l","m3l",100,0,200,"GeV",True],
["Electron Pair Mass","val_mass1","M1",100,0,200,"GeV",True],
["Muon pT","val_pTL3","pTL3",30,0,60,"GeV",True],
["Muon eta","val_etaL3","etaL3",60,-3.,3.,"eta",True], 
["Muon phi","val_phiL3","phiL3",40,-4.,4.,"phi",True], 
["Muon Isolation","val_IsoL3","IsoL3",50,0.,0.2,"pfRelIso03_all",True], 
["Muon 3D Impact Parameter","val_ip3dL3","ip3dL3",25,0.,0.05,"IP3D",True], 
["Muon Significance of 3D Impact Parameter","val_sip3dL3","sip3dL3",40,0.,4.,"SIP3D",True], 
["3 Lep + MET Transverse Mass","val_mt","mt",100,0,300,"GeV",True],
["Transverse Missing Energy","val_met","met",50,0,250,"GeV",True],
["Transver Missing Energy Phi","val_met_phi","met_phi",40,-4,4,"phi",True],
["Electron Pair Transverse Mass","val_M1T","M1T",100,0,200,"GeV",True],
["Number of Electrons","val_nElec","nElectrons",6,0,6,"n",True],
["Number of Leptons","val_nLep","nLeptons",6,0,6,"n",True],
["Number of Good Leptons","val_nGoodLep","nGoodLeptons",6,0,6,"n",True],
["3 Mu pT","val_m3l_pt","m3l_pt",150,0,150,"GeV",True],
["dR Between Leading and Subleading","val_dR12","dR12",100,0,6,"dR",True],
["dR Between Leading and Muon","val_dR13","dR13",100,0,6,"dR",True],
["dR Between Subleading and Muon","val_dR23","dR23",100,0,6,"dR",True],

]

xs, sumW = combXS(xs_sig,sumW_sig,xs_bkg,sumW_bkg)
effs = {}
for i in range(len(samples)):
	if ("data" in samples[i]) or ("fake" in samples[i]):
		weight = xs[samples[i]]/sumW[samples[i]]
	else:
		weight = xs[samples[i]]/sumW[samples[i]]*lumi
	if "Wto3l" in samples[i]: sType = "sig"
	elif "data" in samples[i]: sType = "data"
	else: sType = "MC"	

	file = uproot.open(files[samples[i]])
	events = file["passedEvents"]

	vars_in = signal_vars
	temp = events.arrays(vars_in)

	data = {}
	for key in temp: data[key.decode("utf-8")] = temp[key]
	del temp
	data["weight"] = weight
	data["sType"] = sType
	if not (("data" in samples[i]) or ("fake" in samples[i])):
		data["pileupWeight"] = data["pileupWeight"]/32
	print("Processing %s with %i events"%(samples[i],len(data["nMuons"])))

	# Select other variables
	data = select(data)

	# Perform Cuts
	data["selection"],effs[samples[i]] = skim_val(data)
	data["selection"],effs[samples[i]],data["fail"] = skim_flip(data,effs[samples[i]],samples[i])

	data["fake_weight"] = Fake_weight(data,samples[i],fake_weight_b,fake_weight_e,pt_bins)
	if "fake" in samples[i]: data["genWeight"] = data["genWeight"]*data["fake_weight"]

	# Save resulting data
	with open("/orange/avery/nikmenendez/pickle/%s/%s.p"%(out_dir,samples[i]),'wb') as handle:
		pickle.dump(data, handle)

data = {}
for i in range(len(samples)):
	with open("/orange/avery/nikmenendez/pickle/%s/%s.p"%(out_dir,samples[i]),'rb') as handle:
		data[samples[i]] = pickle.load(handle)

print("Efficiencies of each cut:")
cuts = ["Sample"]
for key in effs[samples[0]]:
	cuts.append(key)
x = PrettyTable(cuts)
for key in effs:
	row = [key]
	for key2 in effs[key]:
		row.append("%.2f%%"%(effs[key][key2]))
	x.add_row(row)
table = open("/orange/avery/nikmenendez/Output/%s/Efficiency_Table.txt"%(out_dir),"w")
table.write(x.get_string())
table.close()
print(x)

# Make Plots
print("Generating Plots")
for p in tqdm(plots):
	plot(data,p,samples,error_on_MC,out_dir)




print("")
print('\a')
print("Uploading plots to web")
import subprocess
subprocess.run(["scp","-r","/orange/avery/nikmenendez/Output/%s/"%(out_dir),"nimenend@lxplus.cern.ch:/eos/user/n/nimenend/www/Wto3l/SR_Selection/ZpX/"])