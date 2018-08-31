#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for the I/O relative to fiber bundles and medical images.
"""

import nibabel as nib
import numpy as np

try:
    import vtk
except ImportError:
    pass
from builtins import range
from six import iteritems

try:
    import itertools.izip as zip
except ImportError:
    pass
from vtk.util import numpy_support as ns
from nibabel.streamlines.tck import TckFile as Tck
from nibabel.streamlines.trk import TrkFile as Trk


def load_nii(fname):
    """
    NIfTI images loading
    :param fname: filename
    :return: data array, affine matrix
    """
    img = nib.load(fname)
    return img.get_data(), img.affine


def read_tck(filename):
    """
    MRTrix3 tractogram loading
    :param filename: filename
    :return: tractogram, header
    """
    tck_object = Tck.load(filename)
    streamlines = tck_object.streamlines
    header = tck_object.header

    return streamlines, header


def read_trk(filename):
    """
    TrackVis tractogram loading
    :param filename: filename
    :return: tractogram, header
    """
    trk_object = Trk.load(filename)
    streamlines = trk_object.streamlines
    header = trk_object.header

    return streamlines, header


def read_vtk(filename):
    """
    VTK tractogram loading
    :param filename: filename
    :return: tractogram
    """
    if filename.endswith('xml') or filename.endswith('vtp'):
        polydata_reader = vtk.vtkXMLPolyDataReader()
    else:
        polydata_reader = vtk.vtkPolyDataReader()

    polydata_reader.SetFileName(filename)
    polydata_reader.Update()

    polydata = polydata_reader.GetOutput()

    return vtkpolydata_to_tracts(polydata)


def vtkpolydata_to_tracts(polydata):
    """
    VTK polylines loading
    :param polydata: vtk file polydata
    :return: tractogram, associated data
    """
    result = {'lines': ns.vtk_to_numpy(polydata.GetLines().GetData()),
              'points': ns.vtk_to_numpy(polydata.GetPoints().GetData()), 'numberOfLines': polydata.GetNumberOfLines()}

    data = {}
    if polydata.GetPointData().GetScalars():
        data['ActiveScalars'] = polydata.GetPointData().GetScalars().GetName()
    if polydata.GetPointData().GetVectors():
        data['ActiveVectors'] = polydata.GetPointData().GetVectors().GetName()
    if polydata.GetPointData().GetTensors():
        data['ActiveTensors'] = polydata.GetPointData().GetTensors().GetName()

    for i in range(polydata.GetPointData().GetNumberOfArrays()):
        array = polydata.GetPointData().GetArray(i)
        np_array = ns.vtk_to_numpy(array)
        if np_array.ndim == 1:
            np_array = np_array.reshape(len(np_array), 1)
        data[polydata.GetPointData().GetArrayName(i)] = np_array

    result['pointData'] = data

    tracts, data = vtkpolydata_dictionary_to_tracts_and_data(result)
    return tracts, data


def vtkpolydata_dictionary_to_tracts_and_data(dictionary):
    """
    VTK polydata management
    :param dictionary: polydata dictionary
    :return: tractogram, associated data
    """
    dictionary_keys = {'lines', 'points', 'numberOfLines'}
    if not dictionary_keys.issubset(dictionary):
        raise ValueError("Dictionary must have the keys lines and points" + repr(dictionary))

    tract_data = {}
    tracts = []

    lines = np.asarray(dictionary['lines']).squeeze()
    points = dictionary['points']

    actual_line_index = 0
    number_of_tracts = dictionary['numberOfLines']
    original_lines = []
    for _ in range(number_of_tracts):
        tracts.append(points[lines[actual_line_index + 1:actual_line_index + lines[actual_line_index] + 1]])
        original_lines.append(
            np.array(lines[actual_line_index + 1:actual_line_index + lines[actual_line_index] + 1], copy=True))
        actual_line_index += lines[actual_line_index] + 1

    if 'pointData' in dictionary:
        point_data_keys = [it[0] for it in iteritems(dictionary['pointData']) if isinstance(it[1], np.ndarray)]

        for k in point_data_keys:
            array_data = dictionary['pointData'][k]
            if k not in tract_data:
                tract_data[k] = [array_data[f] for f in original_lines]
            else:
                np.vstack(tract_data[k])
                tract_data[k].extend([array_data[f] for f in original_lines[-number_of_tracts:]])

    return tracts, tract_data
