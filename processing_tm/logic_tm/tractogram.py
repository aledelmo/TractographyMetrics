#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tractogram specific operation and data encapsulation.
"""

from __future__ import division

import sys

import numpy as np
from builtins import int
from dipy.tracking.benchmarks.bench_streamline import compress_streamlines
from dipy.tracking.streamline import set_number_of_points, values_from_volume
from dipy.tracking.metrics import midpoint, winding
from nibabel.affines import apply_affine


def get_centroid(tract, affine):
    tract = [set_number_of_points(s, len(tract[0])) for s in tract]
    central_line = []
    for i in range(len(tract[0])):
        x, y, z = (0.0, 0.0, 0.0)
        for s in tract:
            x, y, z = (n + s[i][j] for j, n in enumerate((x, y, z)))
        x, y, z = (n / len(tract) for n in (x, y, z))
        central_line.append([x, y, z])
    central_line = np.array(central_line)
    inverse = np.linalg.inv(affine)
    central_line_vox = [apply_affine(inverse, np.array(s)) for s in central_line]
    if central_line_vox[0][2] < central_line_vox[-1][2]:
        return central_line[::-1]

    return central_line


def get_shortest(tract):
    return ((((tract[0] - tract[-1]) ** 2).sum()) ** .5).sum()


def get_length(tract):
    """
    Compute streamline length
    :param tract: streamline
    :return: length
    """
    return ((((tract[1:] - tract[:-1]) ** 2).sum(1)) ** .5).sum()


def streamlines_mapvolume(streamlines, volume, affine):
    """
    Map tractograms on volumetric image
    :param streamlines: tractogram
    :param volume: image
    :param affine: affine matrix
    :return: tractogram with mapping
    """
    inverse = np.linalg.inv(affine)
    streamlines = [apply_affine(inverse, np.array(s)) for s in streamlines]
    mapping = values_from_volume(volume, streamlines)

    return mapping


class Tracts:
    """
    Tractogram encapsulation
    """

    def __init__(self, tractogram, header=None):
        """
        Object creation operations
        :param tractogram: streamlines
        :param header: header (if input not in vtk)
        """
        self.tractogram = tractogram
        self.header = header

    @property
    def tractogram(self):
        return self._tractogram

    @tractogram.setter
    def tractogram(self, value):
        if len(value) == 0:
            sys.exit(1)

        self._tractogram = value

    def __repr__(self):
        return "{}({},{})".format(self.__class__.__name__, self.tractogram, self.header)

    def __str__(self):
        return "{}({},{})".format(self.__class__.__name__, 'Tractogram', 'Header')

    def resample(self, perc):
        """
        Reduction of streamlines number of points
        :param perc: resampling percentage
        """
        self.tractogram = [set_number_of_points(s, max(int(len(s) * perc / 100.), 2)) for s in self.tractogram]

    def compress(self):
        self.tractogram = compress_streamlines(self.tractogram)

    def sort(self, affine):
        """
        Reorient fiber in the same direction
        """

        template = self.tractogram[0]
        initial_flip = []
        for i, s in enumerate(self.tractogram):
            dist_norm = np.linalg.norm(s[0] - template[0]) + np.linalg.norm(s[-1] - template[-1])
            dist_flipped = np.linalg.norm(s[-1] - template[0]) + np.linalg.norm(s[0] - template[-1])
            if dist_flipped < dist_norm:
                initial_flip.append(s[::-1])
            else:
                initial_flip.append(s)
        template = get_centroid(initial_flip, affine)
        for i, s in enumerate(self.tractogram):
            dist_norm = np.linalg.norm(s[0] - template[0]) + np.linalg.norm(s[-1] - template[-1])
            dist_flipped = np.linalg.norm(s[-1] - template[0]) + np.linalg.norm(s[0] - template[-1])
            if dist_flipped < dist_norm:
                self.tractogram[i] = s[::-1]

    def n_lines(self):
        """
        Get number of lines composing the tractogram
        :return: number of fibers
        """
        return len(self.tractogram)

    def n_points(self):
        points = [len(s) for s in self.tractogram]
        return points

    def extremities(self):
        """
        Get streamline endpoints
        :return: tractogram composed only by the extremities
        """
        extremities = [np.array([s[0], s[-1]], s[0].dtype) for s in self.tractogram]
        return extremities

    def lengths(self):
        """
        Get tractogram streamline lengths
        :return: tractogram composed by lengths
        """
        tracts_lengths = [get_length(s) for s in self.tractogram]
        return tracts_lengths

    def shortest(self):
        tracts_shortest = [get_shortest(s) for s in self.tractogram]
        return tracts_shortest

    def mapping(self, volume, affine):
        """
        Get tractogram mapping
        :param volume: volume to be mapped on
        :param affine: affine matrix
        :return: mapped tractogram
        """
        mapped = streamlines_mapvolume(self.tractogram, volume, affine)
        return mapped

    def get_midpoints(self):
        midpoints = [midpoint(s) for s in self.tractogram]
        return midpoints

    def get_winding(self):
        windings = [winding(s) for s in self.tractogram]
        return windings
