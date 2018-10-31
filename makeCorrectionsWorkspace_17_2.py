#!/usr/bin/env python
import ROOT
import imp
import json
from array import array
import numpy as np

wsptools = imp.load_source('wsptools', 'workspaceTools.py')

def GetFromTFile(str):
    f = ROOT.TFile(str.split(':')[0])
    obj = f.Get(str.split(':')[1]).Clone()
    f.Close()
    return obj

# Boilerplate
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.RooWorkspace.imp = getattr(ROOT.RooWorkspace, 'import')
ROOT.TH1.AddDirectory(0)
ROOT.gROOT.LoadMacro("CrystalBallEfficiency.cxx+")

w = ROOT.RooWorkspace('w')

### Muon tracking efficiency scale factor from the Tracking POG
loc = 'inputs/TrackingPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/fits_muon_trk_2017.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron reconstruction efficiency scale factor from the egamma POG
loc = 'inputs/EGammaPOG'

electron_reco_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_run2017BCDEF_passingRECO.root:EGamma_SF2D')
electron_reco_eff_hist_lowEt = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_run2017BCDEF_passingRECO_lowEt.root:EGamma_SF2D')

eta_bins = set()
pt_bins = set()

for i in range(electron_reco_eff_hist.GetXaxis().GetNbins()):
    lowbin = electron_reco_eff_hist.GetXaxis().GetBinLowEdge(i+1)
    upbin = lowbin + electron_reco_eff_hist.GetXaxis().GetBinWidth(i+1)
    eta_bins.add(lowbin)
    eta_bins.add(upbin)

for i in range(electron_reco_eff_hist_lowEt.GetYaxis().GetNbins()):
    lowbin = electron_reco_eff_hist_lowEt.GetYaxis().GetBinLowEdge(i+1)
    upbin = lowbin + electron_reco_eff_hist_lowEt.GetYaxis().GetBinWidth(i+1)
    pt_bins.add(lowbin)
    pt_bins.add(upbin)

for i in range(electron_reco_eff_hist.GetYaxis().GetNbins()):
    lowbin = electron_reco_eff_hist.GetYaxis().GetBinLowEdge(i+1)
    upbin = lowbin + electron_reco_eff_hist.GetYaxis().GetBinWidth(i+1)
    pt_bins.add(lowbin)
    pt_bins.add(upbin)

eta_bins = np.array(sorted(eta_bins))
pt_bins = np.array(sorted(pt_bins))

electron_reco_eff_hist_full = ROOT.TH2F("eGammaSFs","eGammaSFs",len(eta_bins)-1,eta_bins,len(pt_bins)-1,pt_bins)

for i in range(len(eta_bins)-1):
    for j in range(len(pt_bins)-1):
        value = 0.0
        if j == 0:
            searched_bin = electron_reco_eff_hist_lowEt.FindBin(eta_bins[i],pt_bins[j])
            value = electron_reco_eff_hist_lowEt.GetBinContent(searched_bin)
        else:
            value = electron_reco_eff_hist.GetBinContent(i+1,j)
        electron_reco_eff_hist_full.SetBinContent(i+1,j+1,value)

wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_reco_eff_hist_full, name='e_reco_ratio')


### DESY electron & muon tag and probe results
#loc = 'inputs/LeptonEfficiencies'
#
## electron triggers
#desyHistsToWrap = [
#    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'MC', 'e_trg_EleTau_Ele24Leg_desy_mc'),
#    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'Data', 'e_trg_EleTau_Ele24Leg_desy_data'),
#    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'MC', 'e_trg_SingleEle_Ele32OREle35_desy_mc'),
#    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'Data', 'e_trg_SingleEle_Ele32OREle35_desy_data')
#]
#
#for task in desyHistsToWrap:
#    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
#                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])
#
#for t in ['trg_EleTau_Ele24Leg_desy','trg_SingleEle_Ele32OREle35_desy']:
#    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))
#
## muon triggers
#desyHistsToWrap = [
#    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'MC', 'm_trg_MuTau_Mu20Leg_desy_mc'),
#    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'Data', 'm_trg_MuTau_Mu20Leg_desy_data'),
#    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'MC', 'm_trg_SingleMu_Mu24ORMu27_desy_mc'),
#    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'Data', 'm_trg_SingleMu_Mu24ORMu27_desy_data')
#]
#
#for task in desyHistsToWrap:
#    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
#                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])
#
#for t in ['trg_MuTau_Mu20Leg_desy','trg_SingleMu_Mu24ORMu27_desy']:
#    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
#
### KIT electron/muon tag and probe results

# triggr SFs Muons from KIT
loc = 'inputs/KIT/v17_2/'


histsToWrap = [
    (loc+'ZmmTP_Data_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                'm_id_kit_data'),
    (loc+'ZmmTP_DY_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                  'm_id_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',           'm_id_kit_embed'),

    (loc+'ZmmTP_Data_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'm_iso_kit_data'),
    (loc+'ZmmTP_DY_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'm_iso_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'm_iso_kit_embed'),

    (loc+'ZmmTP_Data_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'm_aiso1_kit_data'),
    (loc+'ZmmTP_DY_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                'm_aiso1_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',         'm_aiso1_kit_embed'),

    (loc+'ZmmTP_Data_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'm_aiso2_kit_data'),
    (loc+'ZmmTP_DY_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'm_aiso2_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'm_aiso2_kit_embed'),

    (loc+'ZmmTP_Data_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',      'm_trg_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',        'm_trg_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins', 'm_trg_kit_embed'),

    (loc+'ZmmTP_Data_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',      'm_trg_aiso1_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',        'm_trg_aiso1_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta', 'm_trg_aiso1_kit_embed'),

    (loc+'ZmmTP_Data_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',      'm_trg_aiso2_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',        'm_trg_aiso2_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta', 'm_trg_aiso2_kit_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_kit_data', ['m_trg_kit_data', 'm_trg_aiso1_kit_data', 'm_trg_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_kit_mc', ['m_trg_kit_mc', 'm_trg_aiso1_kit_mc', 'm_trg_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_kit_embed', ['m_trg_kit_embed', 'm_trg_aiso1_kit_embed', 'm_trg_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_data', ['m_iso_kit_data', 'm_aiso1_kit_data', 'm_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_mc', ['m_iso_kit_mc', 'm_aiso1_kit_mc', 'm_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_embed', ['m_iso_kit_embed', 'm_aiso1_kit_embed', 'm_aiso2_kit_embed'])

for t in ['data', 'mc', 'embed']:
    w.factory('expr::m_idiso_kit_%s("@0*@1", m_id_kit_%s, m_iso_kit_%s)' % (t, t, t))
    w.factory('expr::m_idiso_binned_kit_%s("@0*@1", m_id_kit_%s, m_iso_binned_kit_%s)' % (t, t, t))

for t in ['trg', 'trg_binned', 'id', 'iso', 'iso_binned', 'idiso_binned' ]:
    w.factory('expr::m_%s_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_mc)' % (t, t, t))
    w.factory('expr::m_%s_embed_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_embed)' % (t, t, t))

# trigger SFs Electrons from KIT

histsToWrap = [
    (loc+'ZeeTP_Data_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                'e_id90_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                  'e_id90_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',           'e_id90_kit_embed'),
    (loc+'ZeeTP_Data_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                'e_id80_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                  'e_id80_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',           'e_id80_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'e_iso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'e_iso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'e_iso_kit_embed'),
    (loc+'ZeeTP_Data_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'e_aiso1_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                'e_aiso1_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',         'e_aiso1_kit_embed'),
    (loc+'ZeeTP_Data_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'e_aiso2_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'e_aiso2_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'e_aiso2_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',      'e_trg_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',        'e_trg_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins', 'e_trg_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',      'e_trg_aiso1_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',        'e_trg_aiso1_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta', 'e_trg_aiso1_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',      'e_trg_aiso2_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',        'e_trg_aiso2_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta', 'e_trg_aiso2_kit_embed'),
]
for task in histsToWrap:
    print task
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20,  0.50],
                                   'e_trg_binned_kit_data', ['e_trg_kit_data', 'e_trg_aiso1_kit_data',  'e_trg_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20,  0.50],
                                   'e_trg_binned_kit_mc', ['e_trg_kit_mc', 'e_trg_aiso1_kit_mc',  'e_trg_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20,  0.50],
                                   'e_trg_binned_kit_embed', ['e_trg_kit_embed', 'e_trg_aiso1_kit_embed', 'e_trg_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20,  0.50],
                                   'e_iso_binned_kit_data', ['e_iso_kit_data', 'e_aiso1_kit_data', 'e_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20,  0.50],
                                   'e_iso_binned_kit_mc', ['e_iso_kit_mc', 'e_aiso1_kit_mc', 'e_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20,  0.50],
                                   'e_iso_binned_kit_embed', ['e_iso_kit_embed', 'e_aiso1_kit_embed', 'e_aiso2_kit_embed'])


w.factory('expr::e_idiso_kit_embed("@0*@1", e_id90_kit_embed, e_iso_kit_embed)')
w.factory('expr::e_idiso_binned_kit_embed("@0*@1", e_id_kit_embed, e_iso_binned_kit_embed)')
w.factory('expr::e_idiso_kit_embed("@0*@1", e_id80_kit_embed, e_iso_kit_embed)')
w.factory('expr::e_idiso_binned_kit_embed("@0*@1", e_id80_kit_embed, e_iso_binned_kit_embed)')

for t in ['trg', 'trg_binned', 'id90', 'id80', 'iso', 'iso_binned', 'idiso_binned']:
    w.factory('expr::e_%s_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_mc)' % (t, t, t))
for t in ['trg', 'trg_binned', 'id90', 'id80', 'iso_binned', 'idiso_binned']:
    w.factory('expr::e_%s_embed_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_embed)' % (t, t, t))


w.importClassCode('CrystalBallEfficiency')

w.Print()
w.writeToFile('htt_scalefactors_v17_2.root')
w.Delete()
