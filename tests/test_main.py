import pytest

import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import numpy as np

# set up needed directories for tests
input_folder = os.path.join(os.getcwd(), 'example_data')
output_folder = os.path.join('data_output')


def test_intialize():

    from lbaf import LBAF

    gui = LBAF(input_folder, output_folder, 
               file_suffix='.jpg', show=False)

    assert gui.app.img_cnt == 0


def test_next_image():

    from lbaf import LBAF

    gui = LBAF(input_folder, output_folder, 
               file_suffix='.jpg', show=False)
    gui.app._change_image(1)

    assert gui.app.img_cnt == 1
