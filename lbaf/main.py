import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import math

from . import utils
from .data_handler import DataHandler

import sys, os


class LBAF(object):
    """
    Mostly just a public dummy for setting things up
    """
    def __init__(self, input_folder, output_folder, 
                 file_suffix='.jpg', show=True):

        image_list = sorted([file for file in os.listdir(input_folder) if file.endswith(file_suffix)])

        dh = DataHandler(image_list, input_folder, output_folder)
        self.app = RootPlot(dh)

        if show:
            self.show()

    def show(self):
        # self.app.show()
        plt.show()



class RootPlot(object):
    """
    Main root class handling the interactivity
    """

    def __init__(self, dh):
        self.dh = dh

        image_list = self.dh.image_list # imagelist alias
        self.n_img = len(image_list)

        # set up figure
        self.fig = plt.figure('levee-breach_anglefinder', figsize=(10, 8))
        self.ax = plt.subplot(111)
        plt.subplots_adjust(left=0.085, bottom=0.1, top=0.95, right=0.75)
        self.ax.axis('off')

        # image handling attributes, initialize as blank
        self.img_cnt = 0
        # self.curr_img = self._load_new(os.path.join(folder_root, image_list[self.img_cnt]))
        # self.imgdata = self.ax.imshow(self.curr_img)
        self.curr_img = np.zeros((10,10)) 
        self.imgdata = self.ax.imshow(self.curr_img)

        # connect keys and mouse
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self._on_pick)
        self.kid = self.fig.canvas.mpl_connect('key_press_event', self._key_press)

        # levee pick handling attributes
        self.in_levee_pick = False
        self.levee_pick_cnt = 0
        self.levee_pick_data = np.full((3,2), np.nan)
        
        # plot points as NaNs initially
        self.pt_plt = self.ax.plot(self.levee_pick_data.T, 'or')

        # instructions text
        self.ax.text(1.02, 0.93, 'Instructions:', fontsize=16, 
                     transform=self.ax.transAxes)
        self.instr = self.ax.text(1.04, 0.87, 'Press enter to log a breach.', 
                                  wrap=True, transform=self.ax.transAxes)

        # image ID and angle text
        self.ax.text(1.04, 0.67, 'Image:', transform=self.ax.transAxes)
        self.img_num_txt = self.ax.text(1.05, 0.64, 'Image {0} of {1}'.format(self.img_cnt,self.n_img-1), transform=self.ax.transAxes)
        self.ax.text(1.04, 0.57, 'Image ID:', transform=self.ax.transAxes)
        self.img_text = self.ax.text(1.05, 0.54, image_list[self.img_cnt], transform=self.ax.transAxes)
        self.ax.text(1.04, 0.49, 'Angle:', transform=self.ax.transAxes)
        self.angle_txt = self.ax.text(1.05, 0.43, ' ', transform=self.ax.transAxes)

        # static controls text
        self.ax.text(1.02, 0.33, 'Controls:', fontsize=16, 
                     transform=self.ax.transAxes)
        self.ax.text(1.04, 0.30, 'next img:  `right`\n'
                             'prev img:  `left`\n'
                             'cancel:      `escape`\n',
                     transform=self.ax.transAxes, va='top')

        # already exists text
        self.exists_txt = self.ax.text(1.02, 0.05, '', 
                                       fontsize=10, color='red', 
                                       transform=self.ax.transAxes)

        # lines intialized with nan
        self.firstline, = self.ax.plot(np.array([np.nan, np.nan]), np.array([np.nan, np.nan]), 'r--')
        self.secondline, = self.ax.plot(np.array([np.nan, np.nan]), np.array([np.nan, np.nan]), 'r--')

        # update the image selected
        self._change_image(0)

        # minimanager handles the coordinate tracking of the mouse
        self.mm = utils.MiniManager()
        self.scale = 1 # can be implemented to scale the image (not needed for angles, only distances)

        self.mousemv_cid  = self.fig.canvas.mpl_connect('motion_notify_event', 
                                                    lambda e: e)

    def _load_new(self, path):
        image = Image.open(path)
        return image

    def _change_image(self, interval):
        next_cnt = self.img_cnt + interval
        next_cnt = min(next_cnt, self.n_img-1)
        self.img_cnt = max(next_cnt, 0)
        self.dh.change_data_index(self.img_cnt)
        self.curr_img = self._load_new(os.path.join(self.dh.input_folder, self.dh.image_list[self.img_cnt]))
        self.imgdata.set_data(self.curr_img)
        self.img_num_txt.set_text('Image {0} of {1}'.format(self.img_cnt,self.n_img-1))
        self.img_text.set_text(self.dh.image_list[self.img_cnt])
        if self.dh.data_exists:
            self.exists_txt.set_text('Entry already made for this image.\n'
                                     'Only one entry per image is supported.')
        else:
            self.exists_txt.set_text('')
        self.fig.canvas.draw_idle()

    def _reset_pickers(self, next_image=False):
        """
        Reset everything to the initial values for a new round of picking
        """
        self.instr.set_text('Press enter to log a breach.')
        self.angle_txt.set_text(' ')
        self.in_levee_pick = False
        self.levee_pick_cnt = 0
        self.levee_pick_data = np.zeros((4,2))
        reset_mat = np.full((2,2), np.nan)
        self.firstline.set_data(reset_mat)
        self.secondline.set_data(reset_mat)
        for i in range(3):
            self.pt_plt[i].set_data(self.levee_pick_data[i,:].T)
        if next_image:
            self._change_image(interval=1)
        self.fig.canvas.draw_idle()

    def _key_press(self, event):
        if self.levee_pick_cnt == 0 and not self.in_levee_pick:
            if event.key == ' ':
                self._change_image(interval=1)
            elif event.key == 'left':
                self._change_image(interval=-1)
            elif event.key == 'right':
                self._change_image(interval=1)
            
        if event.key == 'enter':
            self.in_levee_pick = True
            if self.levee_pick_cnt == 0:
                self.instr.set_text('Click the breach apex.')
            elif self.levee_pick_cnt == 3:
                self.dh.add_data_to_df(self.img_cnt, self.levee_pick_data, self.curr_angle)
                self._reset_pickers(next_image=True)
            self.fig.canvas.draw_idle()
        elif event.key == 'escape':
            self.fig.canvas.mpl_disconnect(self.mousemv_cid)
            self._reset_pickers()

    def _mouse_move(self, event, mm, map_ax, scale):
        x, y = event.xdata, event.ydata
        if event.inaxes == map_ax:
            mm._mx, mm._my = x * 1, y * 1
            mm._inax = True
            self.activeline.set_xdata(np.array([self.levee_pick_data[0,0], mm._mx]))
            self.activeline.set_ydata(np.array([self.levee_pick_data[0,1], mm._my]))
            if self.levee_pick_cnt > 1:
                self.curr_angle = self._compute_angle()
                self._update_data_in_table()
            self.fig.canvas.draw_idle()
        else:
            mm._mx, mm._my = x, y
            mm._inax = False

    def _on_pick(self, event=None):
        if event.button == 1: # left click
            x_value = event.xdata
            y_value = event.ydata

            if not self.in_levee_pick:
                return

            if self.levee_pick_cnt == 0:
                # first pick, apex
                self.levee_pick_data[0,:] = np.array([x_value, y_value])
                self.pt_plt[0].set_data(self.levee_pick_data[0,:])
                self.levee_pick_cnt += 1
                self.activeline = self.firstline
                self.mousemv_cid  = self.fig.canvas.mpl_connect('motion_notify_event', 
                                                    lambda e: self._mouse_move(e, self.mm, 
                                                    self.ax, self.scale))
                self.instr.set_text('Click the end of the breach on one side.')
                self.fig.canvas.draw_idle()
            elif self.levee_pick_cnt == 1:
                # second pick, one side
                self.levee_pick_data[1,:] = np.array([x_value, y_value])
                self.p1 = (x_value, y_value)
                self.pt_plt[1].set_data(self.levee_pick_data[1,:])
                self.firstline.set_xdata(np.array([self.levee_pick_data[0,0], self.mm._mx]))
                self.firstline.set_ydata(np.array([self.levee_pick_data[0,1], self.mm._my]))
                self.levee_pick_cnt += 1
                self.activeline = self.secondline
                self.instr.set_text('Click the end of the breach on the other side.')
                self.fig.canvas.draw_idle()
            elif self.levee_pick_cnt == 2:
                # second pick, other side
                self.levee_pick_data[2,:] = np.array([x_value, y_value])
                self.p2 = (x_value, y_value)
                self.pt_plt[2].set_data(self.levee_pick_data[2,:])
                self.fig.canvas.mpl_disconnect(self.mousemv_cid)
                self.secondline.set_xdata(np.array([self.levee_pick_data[0,0], self.mm._mx]))
                self.secondline.set_ydata(np.array([self.levee_pick_data[0,1], self.mm._my]))
                self.levee_pick_cnt += 1
                self.activeline = self.firstline
                self.instr.set_text('Press enter to confirm entry of this data point.')
                self.fig.canvas.draw_idle()
            

    def _update_data_in_table(self):
        """
        Update values on redraw
        """
        self.angle_txt.set_text(np.round(self.curr_angle,1))


    def _compute_angle(self):
        """
        lifted from medium:
        https://medium.com/@manivannan_data/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd
        """
        a = self.levee_pick_data[1,:]
        b = self.levee_pick_data[0,:]
        c = np.array([self.mm._mx,self.mm._my])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)
