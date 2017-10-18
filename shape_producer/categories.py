# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
"""
"""


# Category object, holding all relevant information defining this category
# TODO: helper functions to compare the overlap of two categories
class Category(object):
    def __init__(self, name, channel, cuts, variable):
        self._channel = channel
        self._cuts = cuts + channel.cuts
        self._name = name
        self._variable = variable

    @property
    def cuts(self):
        return self._cuts

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def variable(self):
        return self._variable

    @property
    def channel(self):
        return self._channel
