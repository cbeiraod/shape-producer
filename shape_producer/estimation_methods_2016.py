# -*- coding: utf-8 -*-

import copy
import os

from estimation_methods import EstimationMethod
from estimation_methods import ABCDEstimationMethod
from histogram import *
from cutstring import *
from systematics import *
from systematic_variations import *
from era import log_query

import logging
logger = logging.getLogger(__name__)


class DataEstimation(EstimationMethod):
    def __init__(self, era, directory, channel):
        super(DataEstimation, self).__init__(
            name="data_obs",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign=None)
        self._channel = channel

    def get_files(self):
        return self.artus_file_names(self.era.data_files(self._channel))

    def get_cuts(self):
        return Cuts()


# TODO: Does this work?
class HTTEstimation(EstimationMethod):
    def __init__(self, era, directory, channel):
        super(HTTEstimation, self).__init__(
            name="HTT",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_weights(self):
        return Weights(
            Weight("eventWeight", "eventWeight"), self.era.lumi_weight)

    def get_files(self):
        query = {
            "process": "(^GluGluHToTauTau.*125.*|^VBFHToTauTau.*125.*)",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "powheg\-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class ggHEstimation(HTTEstimation):
    def __init__(self, era, directory, channel):
        super(HTTEstimation, self).__init__(
            name="ggH",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_files(self):
        query = {
            "process": "^GluGluHToTauTau.*125.*",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "powheg\-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class qqHEstimation(HTTEstimation):
    def __init__(self, era, directory, channel):
        super(HTTEstimation, self).__init__(
            name="qqH",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_files(self):
        query = {
            "process": "^VBFHToTauTau.*125.*",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "powheg\-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class VHEstimation(HTTEstimation):
    def __init__(self, era, directory, channel):
        super(HTTEstimation, self).__init__(
            name="VH",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_files(self):
        query = {
            "process": "(^W(minus|plus)HToTauTau.*125.*|^ZHToTauTau.*125.*)",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "powheg\-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class ZTTEstimation(EstimationMethod):
    def __init__(self, era, directory, channel):
        super(ZTTEstimation, self).__init__(
            name="ZTT",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_weights(self):
        return Weights(
            Weight("eventWeight", "eventWeight"),
            Weight("zPtReweightWeight", "zPtReweightWeight"),
            Weight("((gen_match_2 == 5)*0.95 + (gen_match_2 != 5))",
                   "hadronic_tau_sf"),
            Weight(
                "((((genbosonmass >= 150.0 && (npartons == 0 || npartons >= 5))*3.95423374e-5) + ((genbosonmass >= 150.0 && npartons == 1)*1.27486147e-5) + ((genbosonmass >= 150.0 && npartons == 2)*1.3012785e-5) + ((genbosonmass >= 150.0 && npartons == 3)*1.33802133e-5) + ((genbosonmass >= 150.0 && npartons == 4)*1.09698723e-5)+((genbosonmass >= 50.0 && genbosonmass < 150.0 && (npartons == 0 || npartons >= 5))*3.95423374e-5) + ((genbosonmass >= 50.0 && genbosonmass < 150.0 && npartons == 1)*1.27486147e-5) + ((genbosonmass >= 50.0 && genbosonmass < 150.0 && npartons == 2)*1.3012785e-5) + ((genbosonmass >= 50.0 && genbosonmass < 150.0 && npartons == 3)*1.33802133e-5) + ((genbosonmass >= 50.0 && genbosonmass < 150.0 && npartons == 4)*1.09698723e-5)+((genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight))/(numberGeneratedEventsWeight*crossSectionPerEventWeight*sampleStitchingWeight))",
                "z_stitching_weight"), self.era.lumi_weight)

    def get_cuts(self):
        return Cuts(Cut("gen_match_2==5",
                        "ztt_genmatch_mt"))  # FIXME: Doubles with weights?

    def get_files(self):
        query = {
            "process":
            "(DYJetsToLL_M10to50|DYJetsToLL_M50|DY1JetsToLL_M50|DY2JetsToLL_M50|DY3JetsToLL_M50|DY4JetsToLL_M50)",
            "data":
            False,
            "campaign":
            self._mc_campaign,
            "generator":
            "madgraph\-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class ZLLEstimation(ZTTEstimation):
    def __init__(self, era, directory, channel):
        super(ZTTEstimation, self).__init__(
            name="ZLL",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_cuts(self):
        return Cuts(Cut("(gen_match_2<5||gen_match_2==6)", "zll_genmatch_mt"))

    def get_weights(self):
        ztt_weights = super(ZLLEstimation, self).get_weights()
        return ztt_weights + Weights(
            Weight(
                "(((decayMode_2 == 0)*1.0) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"))


class ZLEstimationMT(ZTTEstimation):
    def __init__(self, era, directory, channel):
        super(ZTTEstimation, self).__init__(
            name="ZL",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_cuts(self):
        return Cuts(Cut("gen_match_2<5", "zl_genmatch_mt"))


class ZJEstimationMT(ZTTEstimation):
    def __init__(self, era, directory, channel):
        super(ZTTEstimation, self).__init__(
            name="ZJ",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_cuts(self):
        return Cuts(Cut("gen_match_2==6", "zj_genmatch_mt"))


# et is equivalent to mt
class ZJEstimationET(ZJEstimationMT):
    pass


class ZLEstimationET(ZLEstimationMT):
    pass


class WEstimation(EstimationMethod):
    def __init__(self, era, directory, channel):
        super(WEstimation, self).__init__(
            name="W",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_weights(self):
        return Weights(
            Weight(
                "(((npartons == 0 || npartons >= 5)*7.09390278348407e-4) + ((npartons == 1)*1.90063898596475e-4) + ((npartons == 2)*5.8529964471165e-5) + ((npartons == 3)*1.9206444928444e-5) + ((npartons == 4)*1.923548021385e-5))/(numberGeneratedEventsWeight*crossSectionPerEventWeight*sampleStitchingWeight)",
                "wj_stitching_weight"),
            Weight("((gen_match_2 == 5)*0.95 + (gen_match_2 != 5))",
                   "hadronic_tau_sf"),
            Weight("eventWeight", "eventWeight"), self.era.lumi_weight)

    def get_files(self):
        query = {
            "process": "W.*JetsToLNu",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "madgraph-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class TTEstimation(EstimationMethod):
    def __init__(self, era, directory, channel):
        super(TTEstimation, self).__init__(
            name="TT",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_weights(self):
        return Weights(
            Weight("topPtReweightWeight", "topPtReweightWeight"),
            Weight("eventWeight", "eventWeight"),
            Weight("((gen_match_2 == 5)*0.95 + (gen_match_2 != 5))",
                   "hadronic_tau_sf"), self.era.lumi_weight)

    def get_files(self):
        query = {
            "process": "^TT$",
            "data": False,
            "campaign": self._mc_campaign
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)
        log_query(self.name, query, files)
        return self.artus_file_names(files)


class TTTEstimationMT(TTEstimation):
    def get_cuts(self):
        return Cuts(Cut("gen_match_2==5", "ttt_genmatch_mt"))


class TTJEstimationMT(TTEstimation):
    def get_cuts(self):
        return Cuts(Cut("gen_match_2!=5", "ttj_genmatch_mt"))


class TTTEstimationET(TTTEstimationMT):
    pass


class TTJEstimationET(TTJEstimationMT):
    pass


class VVEstimation(EstimationMethod):
    def __init__(self, era, directory, channel):
        super(VVEstimation, self).__init__(
            name="VV",
            folder="nominal",
            era=era,
            directory=directory,
            channel=channel,
            mc_campaign="RunIISummer16MiniAODv2")

    def get_weights(self):
        return Weights(
            Weight("((gen_match_2 == 5)*0.95 + (gen_match_2 != 5))",
                   "hadronic_tau_sf"), Weight("eventWeight", "eventWeight"))

    def get_files(self):
        query = {
            "process":
            "(WWTo1L1Nu2Q|" + "WZTo1L1Nu2Q|" + "WZTo1L3Nu|" + "WZTo2L2Q|" +
            "ZZTo2L2Q" + ")",
            "data":
            False,
            "campaign":
            self._mc_campaign,
            "generator":
            "amcatnlo-pythia8"
        }
        files = self.era.datasets_helper.get_nicks_with_query(query)

        query = {
            "process": "ZZTo4L",
            "extension": "ext1",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "amcatnlo-pythia8"
        }
        files += self.era.datasets_helper.get_nicks_with_query(query)

        query = {
            "process": "WZJToLLLNu",
            "data": False,
            "campaign": self._mc_campaign,
            "generator": "pythia8"
        }
        files += self.era.datasets_helper.get_nicks_with_query(query)

        query = {
            "process":
            "(STt-channelantitop4finclusiveDecays|STt-channeltop4finclusiveDecays|STtWantitop5finclusiveDecays|STtWtop5finclusiveDecays)",
            "data":
            False,
            "campaign":
            self._mc_campaign
        }
        files += self.era.datasets_helper.get_nicks_with_query(query)

        log_query(self.name, "<optimzed out>", files)
        return self.artus_file_names(files)


class QCDEstimation(ABCDEstimationMethod):
    def __init__(self, name, folder, era, directory, channel, bg_processes,
                 data_process):
        super(QCDEstimation, self).__init__(
            name=name,
            folder=folder,
            era=era,
            directory=directory,
            channel=channel,
            bg_processes=bg_processes,
            data_process=data_process,
            AC_cut_names=[ # cuts to be removed to include region for shape derivation
                "tau_2_iso"
            ],
            BD_cuts=[      # cuts to be applied to restrict to region for shape derivation
                Cut("byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5",
                    "tau_2_iso_loose")
            ],
            AB_cut_names=[ # cuts to be removed to include region for the determination of the extrapolation derivation
                "os"
            ],
            CD_cuts=[      # cuts to be applied to restrict to region for the determination of the extrapolation derivation
                Cut("q_1*q_2>0", "ss")
            ]
        )
