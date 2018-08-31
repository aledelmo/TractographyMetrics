#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import os.path
from time import time
import processing_tm as tm

__author__ = 'Alessandro Delmonte'
__email__ = 'delmonte.ale92@gmail.com'


def main():
    tractogram, txt_filepath, fa_filepath, bzero_filepath, md_filepath, header, to_csv, to_xlsx, perc_resampling = setup()
    tm.proc(tractogram, txt_filepath, fa_filepath, bzero_filepath, md_filepath, header, to_csv, to_xlsx,
            perc_resampling)


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('Input_Tractogram', help='Name of the input tractography file', type=check_tracto)
    parser.add_argument('Output_Stats', help='Name of the output statistic file', type=check_txt)
    parser.add_argument('-fa', '--Fractional_Anisotropy', help='Name of the input fractional anisotropy image file',
                        type=check_nii)
    parser.add_argument('-bzero', '--b_zero', help='Name of the input b zero image file', type=check_nii)
    parser.add_argument('-md', '--Mean_Diffusivity', help='Name of the input mean diffusivity image file',
                        type=check_nii)
    parser.add_argument('-hd', '--header', help='Add header information to the text file.', type=check_str)
    parser.add_argument('-csv', '--save_csv', help='Save additional file in CSV format.', action='store_true')
    parser.add_argument('-xlsx', '--save_xlsx', help='Save additional file in Excel format.', action='store_true')
    parser.add_argument('-r', '--resample', help='Downsampling streamlines (might improve computational time)',
                        type=check_threshold)

    args = parser.parse_args()

    return (args.Input_Tractogram, args.Output_Stats, args.Fractional_Anisotropy, args.b_zero, args.Mean_Diffusivity,
            args.header, args.save_csv, args.save_xlsx, args.resample)


def check_tracto(value):
    if (value.endswith('.vtk') or value.endswith('.xml') or value.endswith('.vtp') or value.endswith(
            '.tck') or value.endswith('.trk')) and os.path.isfile(os.path.abspath(value)):
        return value
    else:
        raise argparse.ArgumentTypeError(
            "Invalid input file extension (file format supported: tck, trk, vtk): %s" % value)


def check_txt(value):
    if value.endswith('.txt'):
        return value
    else:
        raise argparse.ArgumentTypeError("Invalid output extension (file format supported: txt): %s" % value)


def check_nii(value):
    if value.endswith('.nii') or value.endswith('.nii.gz') and os.path.isfile(os.path.abspath(value)):
        return os.path.abspath(value)
    else:
        raise argparse.ArgumentTypeError("Invalid output extension (file format supported: nii, nii.gz): %s" % value)


def check_str(value):
    try:
        return str(value)
    except:
        raise argparse.ArgumentTypeError("Invalid header information (must be a string): %s" % value)


def check_threshold(value):
    try:
        t = float(value)
        if 0 < t <= 100:
            return t
        else:
            print('Suggestion: The resampling factor represent a percentage and must be between 0 and 100')
            sys.exit(1)
    except ValueError:
        print('Suggestion: The resampling factor represent a percentage and must be between 0 and 100')
        sys.exit(1)


if __name__ == '__main__':
    t0 = time()
    main()
    print('Execution time: {} s'.format(round((time() - t0), 2)))

    sys.exit(0)
