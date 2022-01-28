import numpy as np
import uproot_methods
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.backend import clear_session

def select(data):

	Lep1 = uproot_methods.classes.TLorentzVector.PtEtaPhiMassLorentzVectorArray(data['pTL1'],data['etaL1'],data['phiL1'],data['massL1'])
	Lep2 = uproot_methods.classes.TLorentzVector.PtEtaPhiMassLorentzVectorArray(data['pTL2'],data['etaL2'],data['phiL2'],data['massL2'])
	Lep3 = uproot_methods.classes.TLorentzVector.PtEtaPhiMassLorentzVectorArray(data['pTL3'],data['etaL3'],data['phiL3'],data['massL3'])
	
	# Define 3 possible Zp combinations
	P1 = Lep1 + Lep2
	P2 = Lep1 + Lep3
	P3 = Lep2 + Lep3
	
	# Define 3 groups of possible combinations of muons
	data["p1"] = data['idL1']!=data['idL2']
	data["p2"] = data['idL1']!=data['idL3']
	data["p3"] = data['idL2']!=data['idL3']
	
	# --------- Define Mass1 as (not) the highest pT muon + highest pT anti-muon -------------------------------------
	M0 = (P1).mass*np.logical_not(data["p1"]) + (P2).mass*np.logical_not(data["p2"]) + (P3).mass*np.logical_not(data["p3"])
	M1 = (P3).mass*data["p3"] + (P2).mass*(data["p2"] & np.logical_not(data["p3"]))
	M2 = (P1).mass*data["p1"] + (P2).mass*(data["p2"] & np.logical_not(data["p1"]))
	data["dRM0"] = data['dR12']*np.logical_not(data["p1"]) + data['dR13']*np.logical_not(data["p2"]) + data['dR23']*np.logical_not(data["p3"])
	data["dRM1"] = data['dR12']*data["p1"] + data['dR13']*(data["p2"] & np.logical_not(data["p1"]))
	data["dRM2"] = data['dR23']*data["p3"] + data['dR13']*(data["p2"] & np.logical_not(data["p3"]))
	data["M0"] = M0
	data["M1"] = np.fmax(M1,M2) # pick higher mass possible pair
	data["M2"] = np.fmin(M1,M2) # pick lowest mass possible pair
	# ----------------------------------------------------------------------------------------------------------------

	data["worstIso"] = np.fmax(np.fmax(np.abs(data["IsoL1"]),np.abs(data["IsoL2"])),np.abs(data["IsoL3"]))
	data["worstdxy"] = np.fmax(np.fmax(np.abs(data["dxyL1"]),np.abs(data["dxyL2"])),np.abs(data["dxyL3"]))
	data["worstdz"] = np.fmax(np.fmax(np.abs(data["dzL1"]),np.abs(data["dzL2"])),np.abs(data["dzL3"]))
	data["worstsip3d"] = np.fmax(np.fmax(np.abs(data["sip3dL1"]),np.abs(data["sip3dL2"])),np.abs(data["sip3dL3"]))
	data["worstip3d"] = np.fmax(np.fmax(np.abs(data["ip3dL1"]),np.abs(data["ip3dL2"])),np.abs(data["ip3dL3"]))
	data["worstmedId"] = np.fmin(np.fmin(np.abs(data["medIdL1"]),np.abs(data["medIdL2"])),np.abs(data["medIdL3"]))
	data["worstmvaId"] = np.fmin(np.fmin(np.abs(data["mvaIdL1"]),np.abs(data["mvaIdL2"])),np.abs(data["mvaIdL3"]))

	# --------- Predict discriminator from NN -----------------------
	#clear_session()
	#ZModel = load_model("/orange/avery/nikmenendez/Wto3l/Optimizer/MVA/ZSelector_model_alt.h5")
	#Selector_vars = ["dxyL1", "dzL1", "etaL1", "ip3dL1", "phiL1", "sip3dL1",
    #        		 "dxyL2", "dzL2", "etaL2", "ip3dL2", "phiL2", "sip3dL2",
    #         		 "dxyL3", "dzL3", "etaL3", "ip3dL3", "phiL3", "sip3dL3",
    #         		 "dR12", "dR13", "dR23", "dRM0", "m3l", "mt", "met", "met_phi", "nJets"]
	#df = pd.DataFrame.from_dict(data)
	#data["discriminator"] = (ZModel.predict(df[Selector_vars])).ravel()
	# ---------------------------------------------------------------

	return data
