import numpy as np
import pandas as pd
import os
import csv

class DataHandler(object):
    def __init__(self, image_list, input_folder, output_folder):

        self.image_list = image_list
        self.input_folder = input_folder
        folder_root = os.path.basename(os.path.normpath(input_folder))
        self.data_path = os.path.join(output_folder, folder_root+'.csv')

        if os.path.isfile(self.data_path):
            print('Data file found.')
            self.db = pd.read_csv(self.data_path)
        else:
            self.db = pd.DataFrame(data=np.full((len(self.image_list),8), np.nan), 
                              columns=['img_id', 'apex_x', 'apex_y', 'pt1_x', 'pt1_y', 'pt2_x', 'pt2_y', 'angle'])
            self.db['img_id'] = self.image_list
            self._write_db()

        self.data_idx = 0
        self.data_exists = self._check_data_exists()


    def _write_db(self):
        self.db.to_csv(self.data_path, index_label=False)


    def change_data_index(self, img_cnt):
        self.data_idx = img_cnt
        self.data_exists = self._check_data_exists()
        return self.data_idx


    def _check_data_exists(self):
        row = self.db.iloc[self.data_idx]
        rowna = row.isna()
        data_exists = not rowna[1] # just check the first entry for simplicity
        return data_exists


    def add_data_to_df(self, img_idx, dataArray, angle):
        self.db.ix[self.data_idx, 1:-1] = dataArray.flatten()
        self.db.ix[self.data_idx, -1] = angle
        self._write_db()
