#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for the I/O relative to fiber bundles and medical images.
"""

import nibabel as nib
import numpy as np
import os.path

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
from nibabel.streamlines.trk import TrkFile as Trk


def load_nii(fname):
    """
    NIfTI images loading
    :param fname: filename
    :return: data array, affine matrix
    """
    img = nib.load(fname)
    return img.get_fdata(), img.affine


def read_tck(filename):
    """
    MRTrix3 tractogram loading
    :param filename: filename
    :return: tractogram, header
    """

    header = read_mrtrix_header(filename)

    vertices, line_starts, line_ends = read_mrtrix_streamlines(filename, header)
    streamlines = []
    for s, e in zip(line_starts, line_ends):
        streamlines.append(vertices[s:e, :])

    return streamlines, header


def read_mrtrix_header(in_file):
    fileobj = open(in_file, "rb")
    header = {}
    #iflogger.info("Reading header data...")
    for line in fileobj:
        line = line.decode()
        if line == "END\n":
            #iflogger.info("Reached the end of the header!")
            break
        elif ": " in line:
            line = line.replace("\n", "")
            line = line.replace("'", "")
            key = line.split(": ")[0]
            value = line.split(": ")[1]
            header[key] = value
            #iflogger.info('...adding "%s" to header for key "%s"', value, key)
    fileobj.close()
    header["count"] = int(header["count"].replace("\n", ""))
    header["offset"] = int(header["file"].replace(".", ""))
    return header


def read_mrtrix_streamlines(in_file, header):
    byte_offset = header["offset"]
    stream_count = header["count"]
    datatype = header["datatype"]
    dt = 4
    if datatype.startswith( 'Float64' ):
        dt = 8
    elif not datatype.startswith( 'Float32' ):
        print('Unsupported datatype: ' + datatype)
        return
    #tck format stores three floats (x/y/z) for each vertex
    num_triplets = (os.path.getsize(in_file) - byte_offset) // (dt * 3)
    dt = 'f' + str(dt)
    if datatype.endswith( 'LE' ):
        dt = '<'+dt
    if datatype.endswith( 'BE' ):
        dt = '>'+dt
    vtx = np.fromfile(in_file, dtype=dt, count=(num_triplets*3), offset=byte_offset)
    vtx = np.reshape(vtx, (-1,3))
    #make sure last streamline delimited...
    if not np.isnan(vtx[-2,1]):
        vtx[-1,:] = np.nan
    line_ends, = np.where(np.all(np.isnan(vtx), axis=1))
    if stream_count != line_ends.size:
        print('expected {} streamlines, found {}'.format(stream_count, line_ends.size))
    line_starts = line_ends + 0
    line_starts[1:line_ends.size] = line_ends[0:line_ends.size-1]
    #the first line starts with the first vertex (index 0), so preceding NaN at -1
    line_starts[0] = -1
    #first vertex of line is the one after a NaN
    line_starts = line_starts + 1
    #last vertex of line is the one before NaN
    line_ends = line_ends - 1

    return vtx, line_starts, line_ends


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
