#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from nibabel.affines import apply_affine


def ras_to_ijk(point, affine):
    inverse = np.linalg.inv(affine)
    return apply_affine(inverse, np.array(point))
