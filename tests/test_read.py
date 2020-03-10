import numpy as np
import pytest
from seismic_zfp.read import *
from seismic_zfp.utils import get_correlated_diagonal_length, get_anticorrelated_diagonal_length

SZ_FILE_025 = 'test_data/small_025bit.sz'
SZ_FILE_05 = 'test_data/small_05bit.sz'
SZ_FILE_1 = 'test_data/small_1bit.sz'
SZ_FILE_2 = 'test_data/small_2bit.sz'
SZ_FILE_4 = 'test_data/small_4bit.sz'
SZ_FILE_8 = 'test_data/small_8bit.sz'
SEGY_FILE = 'test_data/small.sgy'


def compare_inline(sz_filename, tolerance):
    for preload in [True, False]:
        reader = SzReader(sz_filename, preload=preload)
        for line_number in range(5):
            slice_sz = reader.read_inline(line_number)
            with segyio.open(SEGY_FILE) as segyfile:
                slice_segy = segyfile.iline[segyfile.ilines[line_number]]
            assert np.allclose(slice_sz, slice_segy, rtol=tolerance)


def test_read_inline():
    compare_inline(SZ_FILE_025, tolerance=1e+1)
    compare_inline(SZ_FILE_05, tolerance=1e-1)
    compare_inline(SZ_FILE_1, tolerance=1e-2)
    compare_inline(SZ_FILE_2, tolerance=1e-4)
    compare_inline(SZ_FILE_4, tolerance=1e-6)
    compare_inline(SZ_FILE_8, tolerance=1e-10)


def compare_crossline(sz_filename, tolerance):
    for preload in [True, False]:
        reader = SzReader(sz_filename, preload=preload)
        for line_number in range(5):
            slice_sz = reader.read_crossline(line_number)
            with segyio.open(SEGY_FILE) as segyfile:
                slice_segy = segyfile.xline[segyfile.xlines[line_number]]
            assert np.allclose(slice_sz, slice_segy, rtol=tolerance)


def test_read_crossline():
    compare_crossline(SZ_FILE_025, tolerance=1e+1)
    compare_crossline(SZ_FILE_05, tolerance=1e-1)
    compare_crossline(SZ_FILE_1, tolerance=1e-2)
    compare_crossline(SZ_FILE_2, tolerance=1e-4)
    compare_crossline(SZ_FILE_4, tolerance=1e-6)
    compare_crossline(SZ_FILE_8, tolerance=1e-10)


def compare_zslice(sz_filename, tolerance):
    for preload in [True, False]:
        reader = SzReader(sz_filename, preload=preload)
        for line_number in range(50):
            slice_sz = reader.read_zslice(line_number)
            with segyio.open(SEGY_FILE) as segyfile:
                slice_segy = segyfile.depth_slice[line_number]
            assert np.allclose(slice_sz, slice_segy, rtol=tolerance)


def test_read_zslice():
    compare_zslice(SZ_FILE_025, tolerance=1e+1)
    compare_zslice(SZ_FILE_05, tolerance=1e-1)
    compare_zslice(SZ_FILE_1, tolerance=1e-2)
    compare_zslice(SZ_FILE_2, tolerance=1e-4)
    compare_zslice(SZ_FILE_4, tolerance=1e-6)
    compare_zslice(SZ_FILE_8, tolerance=1e-10)


def compare_correlated_diagonal(sz_filename, tolerance):
    for preload in [True, False]:
        reader = SzReader(sz_filename, preload=preload)
        for line_number in range(-4, 4):
            slice_sz = reader.read_correlated_diagonal(line_number)
            with segyio.open(SEGY_FILE) as segyfile:
                diagonal_length = get_correlated_diagonal_length(line_number, len(segyfile.ilines), len(segyfile.xlines))
                slice_segy = np.zeros((diagonal_length, len(segyfile.samples)))
                if line_number >= 0:
                    for d in range(diagonal_length):
                        slice_segy[d, :] = segyfile.trace[(d+line_number)*len(segyfile.xlines) + d]
                else:
                    for d in range(diagonal_length):
                        slice_segy[d, :] = segyfile.trace[d*len(segyfile.xlines) + d - line_number]
            assert np.allclose(slice_sz, slice_segy, rtol=tolerance)


def test_read_correlated_diagonal():
    compare_correlated_diagonal(SZ_FILE_025, tolerance=1e+1)
    compare_correlated_diagonal(SZ_FILE_05, tolerance=1e-1)
    compare_correlated_diagonal(SZ_FILE_1, tolerance=1e-2)
    compare_correlated_diagonal(SZ_FILE_2, tolerance=1e-4)
    compare_correlated_diagonal(SZ_FILE_4, tolerance=1e-6)
    compare_correlated_diagonal(SZ_FILE_8, tolerance=1e-10)


def compare_anticorrelated_diagonal(sz_filename, tolerance):
    for preload in [True, False]:
        reader = SzReader(sz_filename, preload=preload)
        for line_number in range(6):
            print("\n\n\n\n", line_number)
            slice_sz = reader.read_anticorrelated_diagonal(line_number)
            with segyio.open(SEGY_FILE) as segyfile:
                diagonal_length = get_anticorrelated_diagonal_length(line_number, len(segyfile.ilines), len(segyfile.xlines))
                slice_segy = np.zeros((diagonal_length, len(segyfile.samples)))
                if line_number < len(segyfile.xlines):
                    for d in range(diagonal_length):
                        slice_segy[d, :] = segyfile.trace[line_number + d * (len(segyfile.xlines) - 1)]
                else:
                    for d in range(diagonal_length):
                        slice_segy[d, :] = segyfile.trace[(line_number - len(segyfile.xlines) + 1 + d) * len(segyfile.xlines)
                                                          + (len(segyfile.xlines) - d - 1)]
            assert np.allclose(slice_sz, slice_segy, rtol=tolerance)


def test_read_anticorrelated_diagonal():
    compare_anticorrelated_diagonal(SZ_FILE_025, tolerance=1e+1)
    compare_anticorrelated_diagonal(SZ_FILE_05, tolerance=1e-1)
    compare_anticorrelated_diagonal(SZ_FILE_1, tolerance=1e-2)
    compare_anticorrelated_diagonal(SZ_FILE_2, tolerance=1e-4)
    compare_anticorrelated_diagonal(SZ_FILE_4, tolerance=1e-6)
    compare_anticorrelated_diagonal(SZ_FILE_8, tolerance=1e-10)


def compare_subvolume(sz_filename, tolerance):
    for preload in [True, False]:
        min_il, max_il = 2,  3
        min_xl, max_xl = 1,  2
        min_z,  max_z = 10, 20
        vol_sz = SzReader(sz_filename, preload=preload).read_subvolume(min_il=min_il, max_il=max_il,
                                                      min_xl=min_xl, max_xl=max_xl,
                                                      min_z=min_z, max_z=max_z)
        vol_segy = segyio.tools.cube(SEGY_FILE)[min_il:max_il, min_xl:max_xl, min_z:max_z]
        assert np.allclose(vol_sz, vol_segy, rtol=tolerance)


def test_read_subvolume():
    compare_subvolume(SZ_FILE_025, tolerance=1e+1)
    compare_subvolume(SZ_FILE_05, tolerance=1e-1)
    compare_subvolume(SZ_FILE_1, tolerance=1e-2)
    compare_subvolume(SZ_FILE_2, tolerance=1e-4)
    compare_subvolume(SZ_FILE_4, tolerance=1e-6)
    compare_subvolume(SZ_FILE_8, tolerance=1e-10)


def test_index_errors():
    reader = SzReader(SZ_FILE_4)

    with pytest.raises(IndexError):
        reader.read_inline(-1)

    with pytest.raises(IndexError):
        reader.read_inline(5)

    with pytest.raises(IndexError):
        reader.read_crossline(-1)

    with pytest.raises(IndexError):
        reader.read_crossline(5)

    with pytest.raises(IndexError):
        reader.read_zslice(-1)

    with pytest.raises(IndexError):
        reader.read_zslice(50)

    with pytest.raises(IndexError):
        reader.read_correlated_diagonal(-5)

    with pytest.raises(IndexError):
        reader.read_correlated_diagonal(5)

    with pytest.raises(IndexError):
        reader.read_anticorrelated_diagonal(-1)

    with pytest.raises(IndexError):
        reader.read_anticorrelated_diagonal(9)
