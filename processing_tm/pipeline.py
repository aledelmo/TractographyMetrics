#!/usr/bin/env python
# -*- coding: utf-8 -*-

import processing_tm.logic_tm as lg
import numpy as np
import csv
import xlsxwriter
from six import iteritems


def proc(tractogram_filepath, txt_filepath, fa_filepath, bzero_filepath, md_filepath, header, to_csv, to_xlsx,
         perc_resampling, from_plugin=False):
    tractogram = load_tracts(tractogram_filepath)

    if from_plugin:
        txt_filepath = txt_filepath.decode()

    if perc_resampling:
        tractogram.resample(perc_resampling)

    metrics = lg.Metrics(tractogram)
    behaviors = dict()
    if fa_filepath:
        fa, affine = lg.load_nii(fa_filepath)
        metrics.set_affine(affine)
        tractogram.sort(affine)
        behaviors['FA'] = metrics.diffusion(fa, 'FA')
    if bzero_filepath:
        bzero, affine = lg.load_nii(bzero_filepath)
        metrics.set_affine(affine)
        if not fa_filepath:
            tractogram.sort(affine)
        behaviors['b-zero'] = metrics.diffusion(bzero, 'b-zero')
    if md_filepath:
        md, affine = lg.load_nii(md_filepath)
        metrics.set_affine(affine)
        if not fa_filepath or bzero_filepath:
            tractogram.sort(affine)
        behaviors['MD'] = metrics.diffusion(md, 'MD')

    metrics.geometric()

    body = metrics.get_str()
    body_dict = metrics.get_dict()

    if not header:
        header = txt_filepath

    save_txt(txt_filepath, body, header)

    if to_xlsx:
        xlsx_filepath = txt_filepath.split('.')[0] + '.xlsx'
        save_xlsx(xlsx_filepath, body_dict, header)

    if to_csv:
        csv_filepath = txt_filepath.split('.')[0] + '.csv'
        save_csv(csv_filepath, body_dict)
    else:
        if from_plugin:
            csv_filepath = from_plugin['csv_fname']
            save_csv(csv_filepath, body_dict)

    if from_plugin:
        return csv_filepath, behaviors


def load_tracts(fname):
    """
    Tractogram loading manager
    :param fname: tractogram filename
    :return: tractogram class object
    """
    if fname.endswith('.tck'):
        tractogram, header = lg.read_tck(fname)
        obj = lg.Tracts(tractogram, header=header)
    elif fname.endswith('.trk'):
        tractogram, header = lg.read_trk(fname)
        obj = lg.Tracts(tractogram, header=header)
    else:
        tractogram = lg.read_vtk(fname)[0]
        obj = lg.Tracts(tractogram)
    return obj


def save_txt(txt_filepath, body, header):
    with open(txt_filepath, "w") as handler:
        handler.write(header + '\n' + body)


def save_csv(csv_filepath, body):
    with open(csv_filepath, 'w') as handle:
        w = csv.DictWriter(handle, body.keys(), delimiter=';')
        w.writeheader()
        w.writerow(body)


def save_xlsx(xlsx_filepath, body, header):
    with xlsxwriter.Workbook(xlsx_filepath) as handle:
        worksheet = handle.add_worksheet()
        worksheet.write(0, 0, header)
        row = 2
        for (key, value) in iteritems(body):
            col = 1
            worksheet.write(row, 0, key)
            if type(value) is np.ndarray:
                for v in value:
                    worksheet.write(row, col, v)
                    col += 1
            else:
                worksheet.write(row, 1, value)
            row += 1
