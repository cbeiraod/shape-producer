# -*- coding: utf-8 -*-

import ROOT
from histogram import *
import copy

import logging
logger = logging.getLogger(__name__)
"""
"""


class Systematic(object):
    def __init__(self, category, process, analysis, era, variation, mass):
        self._category = category
        self._process = process
        self._analysis = analysis
        self._era = era
        self._mass = mass
        self._variation = variation
        self._shape = None
        self._root_objects = None

    # TODO: What does this magic?
    def __deepcopy__(self, memo):
        # some kind of workaround: the deepcopy method is overwritten, but anyway the one from the base class should be called
        deepcopy_method = self.__deepcopy__
        self.__deepcopy__ = None
        cp = copy.deepcopy(self, memo)
        self.__deepcopy__ = deepcopy_method

        # manually copy also the associated process
        cp.process = copy.deepcopy(self.process)

        return cp

    @property
    def channel(self):
        return self._category.channel

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, process):
        self._process = process

    @property
    def era(self):
        return self._era

    @property
    def analysis(self):
        return self._analysis

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = category

    @property
    def mass(self):
        return self._mass

    @property
    def variation(self):
        return self._variation

    @variation.setter
    def variation(self, variation):
        self._variation = variation

    @property
    def root_objects(self):
        if self._root_objects == None:
            logger.fatal("ROOT objects of systematic %s are not created.",
                         self.name)
            raise Exception
        return self._root_objects

    def create_root_objects(self):
        self._root_objects = self._process.estimation_method.create_root_objects(
            self)

    def do_estimation(self):
        self._shape = self._process.estimation_method.do_estimation(self)

    @property
    def shape(self):
        if self._shape == None:
            logger.fatal("Shape of systematic %s has not been produced.",
                         self.name)
            raise Exception
        return self._shape

    @property
    def name(self):
        return "#{CHANNEL}#{CATEGORY}#{PROCESS}#{ANALYSIS}#{ERA}#{VARIABLE}#{MASS}#{VARIATION}".format(
            CHANNEL=self._category._channel.name,
            CATEGORY=self._category.name,
            PROCESS=self._process.name,
            ANALYSIS=self._analysis,
            ERA=self._era.name,
            VARIABLE='COUNT' if self._category.variable == None else
            self._category.variable.name,
            MASS=self._mass,
            VARIATION=""
            if self._variation.name == "Nominal" else self._variation.name)

    def summary(self):
        return [
            self.name, self._category.name, self._process.name, self._analysis,
            self._era.name, self._category.channel.name,
            str(self.mass), self.variation.name,
            str(self._process.estimation_method),
            str(self._shape)
        ]


# holder class for systematics
class Systematics(object):
    def __init__(self, output_file, num_threads=1, backend="classic"):
        # member holding the systematics
        self._systematics = []
        self._backend = backend
        self._output_file = output_file
        self._num_threads = num_threads

    def add(self, systematic):
        self._systematics.append(systematic)

    # do the estimations
    def produce(self):
        # create the input histograms, all at once to make optimal use of TDFs
        self.create_histograms()

        # sort the estimation modules. TODO to be implemented, if estimation modules are dependent on each other
        # self.sort_estimations()

        # do the background estimations
        self.do_estimations()
        logger.debug("Successfully finished systematics production.")

    # read root histograms from the inputfiles and write them to the outputfile
    def create_histograms(self):
        # collect ROOT objects
        self._root_objects_holder = RootObjects(self._output_file)
        for systematic in self._systematics:
            logger.debug("Create ROOT objects for systematic %s.",
                         systematic.name)
            systematic.create_root_objects()
            self._root_objects_holder.add(systematic.root_objects)
            self._root_objects_holder.add_unique(systematic.root_objects)
        #self._root_objects_holder.check_duplicates() # TODO: Implement this if needed

        # produce unique ROOT objects (in parallel)
        logger.debug("Produce ROOT objects using the %s backend.",
                     self._backend)
        if self._backend == "classic":
            self._root_objects_holder.produce_classic(self._num_threads)
        elif self._backend == "tdf":
            self._root_objects_holder.produce_tdf(self._num_threads)
        else:
            logger.fatal("Backend %s is not implemented.", self._backend)
            raise Exception

        # set duplicates to the produced ROOT objects
        self._root_objects_holder.set_duplicates()

    # to the actual estimations. Currently do not run in parallel due to expected very low runtime, can in principle be parallelized
    def do_estimations(self):
        for systematic in self._systematics:
            logger.debug("Do estimation for systematic %s.", systematic.name)
            systematic.do_estimation()
            systematic.shape.save(self._root_objects_holder)

    def summary(self):
        table = [[
            "name", "category", "process", "analysis", "era", "channel",
            "mass", "systematic", "estimation method", "results"
        ]]
        for systematic in self._systematics:
            table.append(systematic.summary())
        for line in table:
            logger.info("|".join([a.ljust(20)[0:20] for a in line]))

    # function to add systematic variations
    # TODO: Make this nicer, too hacky
    # Enable application of multiple variations at once
    def add_systematic_variation(self, variation, **properties):
        new_systematics = []
        for systematic in self._systematics:
            # consider only Nominal values for shifts
            if systematic.variation.is_nominal():
                found = 0
                for key, value in properties.iteritems():
                    if hasattr(systematic, key):
                        property_ = getattr(systematic, key)
                        if hasattr(property_, "name") and hasattr(
                                value, "name"):
                            if property_.name == value.name: found += 1
                        else:
                            logger.fatal(
                                "Method %s.name does not exist. Comparison is not possible.",
                                key)
                            raise Exception

                if found == len(properties):
                    new_systematic = copy.deepcopy(systematic)
                    new_systematic.variation = variation
                    new_systematics.append(new_systematic)
        self._systematics += new_systematics

    def add_extra_category(self, new_category, category_to_modify):
        new_systematics = []
        for systematic in self._systematics:
            # consider only Nominal values for shifts
            if systematic.category == category_to_modify:
                new_systematic = copy.deepcopy(systematic)
                new_systematic.category = new_category
                new_systematics.append(new_systematic)
        self._systematics += new_systematics
