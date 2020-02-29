import lbaf

import os

input_folder = os.path.join(os.getcwd(), 'example_data')
output_folder = os.path.join('data_output')

gui = lbaf.LBAF(input_folder, output_folder, file_suffix='.jpg')
