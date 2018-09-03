#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from builtins import int
from .utils import ras_to_ijk
from .tractogram import streamlines_mapvolume
from itertools import islice


def get_length(tract):
    """
    Compute streamline length
    :param tract: streamline
    :return: length
    """
    return ((((tract[1:] - tract[:-1]) ** 2).sum(1)) ** .5).sum()


def batch_iterable(iterable, size):
    iterable = iter(iterable)
    batch = list(islice(iterable, size))
    while batch:
        yield batch
        batch = list(islice(iterable, size))


class Metrics:
    def __init__(self, tractogram):
        self.measures = dict()
        self.tractogram = tractogram
        self.affine = None
        self.txt_str = ''
        self.txt_dict = dict()

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def set_affine(self, affine):
        self.affine = affine

    def geometric(self):
        n_lines = self.tractogram.n_lines()

        self.txt_str += '\n\n'
        self.txt_str += '{}: {}'.format('Number of fibers', n_lines)
        self.txt_dict['Number of fibers'] = n_lines

        n_points = np.asarray(self.tractogram.n_points(), dtype=np.int64)

        mean_n_points = n_points.mean()
        std_n_points = n_points.std()
        median_n_points = np.median(n_points)
        max_n_points = np.amax(n_points)
        min_n_points = np.amin(n_points)

        self.txt_str += '\n\n'
        self.txt_str += '{}: {}'.format('Mean number of points per fiber', mean_n_points)
        self.txt_dict['Mean number of points per fiber'] = mean_n_points
        self.txt_str += '\n'
        self.txt_str += '{}: {}'.format('Std number of points per fiber', std_n_points)
        self.txt_dict['Std number of points per fiber'] = std_n_points
        self.txt_str += '\n'
        self.txt_str += '{}: {}'.format('Median number of points per fiber', int(median_n_points))
        self.txt_dict['Median number of points per fiber'] = int(median_n_points)
        self.txt_str += '\n'
        self.txt_str += '{}: {}, {}: {}'.format('Max number of points per fiber', max_n_points,
                                                'Min number of points per fiber', min_n_points)
        self.txt_dict['Max number of points per fiber'] = max_n_points
        self.txt_dict['Min number of points per fiber'] = min_n_points

        lengths = np.asarray(self.tractogram.lengths(), dtype=np.float64)

        mean_length = lengths.mean()
        std_length = lengths.std()
        median_length = np.median(lengths)
        max_length = np.amax(lengths)
        min_length = np.amin(lengths)

        self.txt_str += '\n\n'
        self.txt_str += '{}: {} mm'.format('Mean Length', mean_length)
        self.txt_dict['Mean Length'] = mean_length
        self.txt_str += '\n'
        self.txt_str += '{}: {} mm'.format('Std Length', std_length)
        self.txt_dict['Std Length'] = std_length
        self.txt_str += '\n'
        self.txt_str += '{}: {} mm'.format('Median Length', median_length)
        self.txt_dict['Median Length'] = median_length
        self.txt_str += '\n'
        self.txt_str += '{}: {} mm, {}: {} mm'.format('Max Length', max_length, 'Min Length', min_length)
        self.txt_dict['Max Length'] = max_length
        self.txt_dict['Min Length'] = min_length

        shortest = np.asarray(self.tractogram.shortest(), dtype=np.float64)

        mean_shortest = shortest.mean()
        std_shortest = shortest.std()
        median_shortest = np.median(shortest)
        max_shortest = np.amax(shortest)
        min_shortest = np.amin(shortest)

        self.txt_str += '\n\n'
        self.txt_str += '{}: {} mm'.format('Mean Shortest Length', mean_shortest)
        self.txt_dict['Mean Shortest Length'] = mean_shortest
        self.txt_str += '\n'
        self.txt_str += '{}: {} mm'.format('Std Shortest Length', std_shortest)
        self.txt_dict['Std Shortest Length'] = std_shortest
        self.txt_str += '\n'
        self.txt_str += '{}: {} mm'.format('Median Shortest Length', median_shortest)
        self.txt_dict['Median Shortest Length'] = median_shortest
        self.txt_str += '\n'
        self.txt_str += '{}: {} mm, {}: {} mm'.format('Max Shortest Length', max_shortest,
                                                      'Min Shortest Length', min_shortest)
        self.txt_dict['Max Shortest Length'] = max_shortest
        self.txt_dict['Min Shortest Length'] = min_shortest

        midpoints = np.asarray(self.tractogram.get_midpoints())

        mean_midpoints = midpoints.mean(axis=0)

        if type(self.affine) is np.ndarray:
            mean_midpoints_ijk = ras_to_ijk(mean_midpoints, self.affine)

            self.txt_str += '\n\n'
            self.txt_str += '{}: {} mm / {} vox'.format('Mean Midpoint Position', mean_midpoints, mean_midpoints_ijk)
            self.txt_dict['Mean Midpoint Position (mm)'] = mean_midpoints
            self.txt_dict['Mean Midpoint Position (vox)'] = mean_midpoints_ijk
        else:
            self.txt_str += '\n\n'
            self.txt_str += '{}: {} mm'.format('Mean Midpoint Position', mean_midpoints)
            self.txt_dict['Mean Midpoint Position (mm)'] = mean_midpoints

        turning_angles = np.asarray(self.tractogram.get_winding())

        mean_turning_angles = turning_angles.mean()
        std_turning_angles = turning_angles.std()
        median_turning_angles = np.median(turning_angles)
        max_turning_angles = np.amax(turning_angles)
        min_turning_angles = np.amin(turning_angles)

        self.txt_str += '\n\n'
        self.txt_str += '{}: {} °'.format('Mean Turning Angle', mean_turning_angles)
        self.txt_dict['Mean Turning Angle'] = mean_turning_angles
        self.txt_str += '\n'
        self.txt_str += '{}: {} °'.format('Std Turning Angle', std_turning_angles)
        self.txt_dict['Std Turning Angle'] = std_turning_angles
        self.txt_str += '\n'
        self.txt_str += '{}: {} °'.format('Median Turning Angle', median_turning_angles)
        self.txt_dict['Median Turning Angle'] = median_turning_angles
        self.txt_str += '\n'
        self.txt_str += '{}: {} °, {}: {} °'.format('Max Turning Angle', max_turning_angles,
                                                    'Min Turning Angle', min_turning_angles)
        self.txt_dict['Max Turning Angle'] = max_turning_angles
        self.txt_dict['Min Turning Angle'] = min_turning_angles

        self.tractogram.sort()

        extremities = np.asarray(self.tractogram.extremities())

        seed_points = extremities[:, 0, :]

        termination_points = extremities[:, -1, :]

        seed_points_mean_pos = seed_points.mean(axis=0)
        termination_points_mean_pos = termination_points.mean(axis=0)

        if type(self.affine) is np.ndarray:
            seed_points_mean_pos_ijk = ras_to_ijk(seed_points_mean_pos, self.affine)
            termination_points_mean_pos_ijk = ras_to_ijk(termination_points_mean_pos, self.affine)

            self.txt_str += '\n\n'
            self.txt_str += '{}: {} mm / {} vox'.format('Seed Points Mean Position', seed_points_mean_pos,
                                                        seed_points_mean_pos_ijk)
            self.txt_dict['Seed Points Mean Position (mm)'] = seed_points_mean_pos
            self.txt_dict['Seed Points Mean Position (vox)'] = seed_points_mean_pos_ijk

            self.txt_str += '\n\n'
            self.txt_str += '{}: {} mm / {} vox'.format('Termination  Points Mean Position',
                                                        termination_points_mean_pos,
                                                        termination_points_mean_pos_ijk)
            self.txt_dict['Termination Points Mean Position (mm)'] = seed_points_mean_pos
            self.txt_dict['Termination Points Mean Position (vox)'] = termination_points_mean_pos_ijk
        else:
            self.txt_str += '\n\n'
            self.txt_str += '{}: {} mm'.format('Seed Points Mean Position', seed_points_mean_pos)
            self.txt_dict['Seed Points Mean Position (mm)'] = seed_points_mean_pos

            self.txt_str += '\n\n'
            self.txt_str += '{}: {} mm'.format('Termination  Points Mean Position', termination_points_mean_pos)
            self.txt_dict['Termination Points Mean Position (mm)'] = seed_points_mean_pos

    def diffusion(self, scalar_map, scalar_name):
        if scalar_name != 'FA':
            scalar_map = (scalar_map - np.amin(scalar_map)) / (np.amax(scalar_map) - np.amin(scalar_map))
        scalar_measurement = self.tractogram.mapping(scalar_map, self.affine)
        scalar_measurement_mean = np.asarray([np.asarray(m).mean() for m in scalar_measurement])

        mean_shortest = scalar_measurement_mean.mean()
        std_shortest = scalar_measurement_mean.std()
        median_shortest = np.median(scalar_measurement_mean)
        max_shortest = np.amax(np.concatenate(scalar_measurement).ravel())
        min_shortest = np.amin(np.concatenate(scalar_measurement).ravel())

        self.txt_str += '\n\n'
        self.txt_str += '{}: {}'.format('Mean ' + scalar_name + ' Value', mean_shortest)
        self.txt_dict['Mean ' + scalar_name + ' Value'] = mean_shortest
        self.txt_str += '\n'
        self.txt_str += '{}: {}'.format('Std ' + scalar_name + ' Value', std_shortest)
        self.txt_dict['Std ' + scalar_name + ' Value'] = std_shortest
        self.txt_str += '\n'
        self.txt_str += '{}: {}'.format('Median ' + scalar_name + ' Value', median_shortest)
        self.txt_dict['Median ' + scalar_name + ' Value'] = median_shortest
        self.txt_str += '\n'
        self.txt_str += '{}: {}, {}: {}'.format('Max ' + scalar_name + ' Value', max_shortest,
                                                'Min ' + scalar_name + ' Value', min_shortest)
        self.txt_dict['Max ' + scalar_name + ' Value'] = max_shortest
        self.txt_dict['Min ' + scalar_name + ' Value'] = min_shortest

        behavior = np.zeros((len(self.tractogram.tractogram), 10))
        for i, tract in enumerate(self.tractogram.tractogram):
            cum_len = [get_length(tract[:n]) for n in range(1, len(tract) + 1)]
            ten_perc = get_length(tract) / 10.
            for j in range(1, 11):
                current = tract[(ten_perc * (j - 1) < cum_len) & (cum_len < ten_perc * j)]
                behavior[i, j - 1] = np.asarray(streamlines_mapvolume([current], scalar_map, self.affine)).mean()
        return np.mean(behavior, axis=0)

    def get_str(self):
        return self.txt_str

    def get_dict(self):
        return self.txt_dict
