from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QImage, QPixmap
from pyqtgraph import PlotWidget, plot
import sys  # We need sys so that we can pass argv to QApplication
from PyQt6.QtWidgets import QFileDialog
import pyqtgraph as pg
import cv2
import numpy as np
import yaml
import io


class MainWindow(QtWidgets.QMainWindow):
    mean = 16
    #gains = [127,127,127,127,127,127]
    gains = [255,255,255,255,255,255]
    steps = 50
    mapping = [[0,2],[1,2],[0,1]]
    loaded = False
    version = 0.2

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("interface.ui",self)

        self.setWindowTitle(self.windowTitle()+' V'+str(self.version))

        self.redBrowse.clicked.connect(lambda: self.load_image(0))
        self.greenBrowse.clicked.connect(lambda: self.load_image(1))
        self.blueBrowse.clicked.connect(lambda: self.load_image(2))
        self.magentaBrowse.clicked.connect(lambda: self.load_image(3))
        self.cyanBrowse.clicked.connect(lambda: self.load_image(4))
        self.yellowBrowse.clicked.connect(lambda: self.load_image(5))

        self.redCheckbox.stateChanged.connect(self.display_image)
        self.greenCheckbox.stateChanged.connect(self.display_image)
        self.blueCheckbox.stateChanged.connect(self.display_image)
        self.magentaCheckbox.stateChanged.connect(self.display_image)
        self.cyanCheckbox.stateChanged.connect(self.display_image)
        self.yellowCheckbox.stateChanged.connect(self.display_image)

        self.redMaxSpinner.valueChanged.connect(lambda: self.update_hist(0))
        self.greenMaxSpinner.valueChanged.connect(lambda: self.update_hist(1))
        self.blueMaxSpinner.valueChanged.connect(lambda: self.update_hist(2))
        self.magentaMaxSpinner.valueChanged.connect(lambda: self.update_hist(3))
        self.cyanMaxSpinner.valueChanged.connect(lambda: self.update_hist(4))
        self.yellowMaxSpinner.valueChanged.connect(lambda: self.update_hist(5))

        self.redMinSpinner.valueChanged.connect(lambda: self.update_hist(0))
        self.greenMinSpinner.valueChanged.connect(lambda: self.update_hist(1))
        self.blueMinSpinner.valueChanged.connect(lambda: self.update_hist(2))
        self.magentaMinSpinner.valueChanged.connect(lambda: self.update_hist(3))
        self.cyanMinSpinner.valueChanged.connect(lambda: self.update_hist(4))
        self.yellowMinSpinner.valueChanged.connect(lambda: self.update_hist(5))

        self.saveBrowseButton.clicked.connect(self.select_safe_file)
        self.saveButton.clicked.connect(self.save_image)
        self.reloadButton.clicked.connect(self.reload_all)

        self.graphs = [ self.redGraph.getPlotItem(),\
                        self.greenGraph.getPlotItem(),\
                        self.blueGraph.getPlotItem(),\
                        self.magentaGraph.getPlotItem(),\
                        self.cyanGraph.getPlotItem(),\
                        self.yellowGraph.getPlotItem()]

        self.maxSpinners = [self.redMaxSpinner,\
                            self.greenMaxSpinner,\
                            self.blueMaxSpinner,\
                            self.magentaMaxSpinner,\
                            self.cyanMaxSpinner,\
                            self.yellowMaxSpinner]
        
        self.minSpinners = [self.redMinSpinner,\
                            self.greenMinSpinner,\
                            self.blueMinSpinner,\
                            self.magentaMinSpinner,\
                            self.cyanMinSpinner,\
                            self.yellowMinSpinner]
        
        self.files = [self.redFile,\
                        self.greenFile,\
                        self.blueFile,\
                        self.magentaFile,\
                        self.cyanFile,\
                        self.yellowFile]

        self.checkboxes = [self.redCheckbox,\
                           self.greenCheckbox,\
                           self.blueCheckbox,\
                           self.magentaCheckbox,\
                           self.cyanCheckbox,\
                           self.yellowCheckbox]

        self.bw_images = [None]*6
        self.bw_1d = [None]*6

        self.improved = None
        
        self.loaded = True

    def reload_all(self):
        for i1 in range(6):
            self.reload(self.files[i1].text(),i1)

    def display_image(self):
        
        bw_improved = [None]*3

        for i1 in range(6):
            if self.files[i1] != "" and self.checkboxes[i1].isChecked():
                if self.bw_images[i1] is not None:
                    max = self.maxSpinners[i1].value()
                    min = self.minSpinners[i1].value()
                    if i1 < 3:
                        if bw_improved[i1] is None:
                            bw_improved[i1] = (self.bw_images[i1]-min)/(max-min)*self.gains[i1]
                        else:
                            bw_improved[i1] = bw_improved[i1] + (self.bw_images[i1]-min)/(max-min)*self.gains[i1]
                    else:
                        use0 = self.mapping[i1-3][0]
                        if bw_improved[use0] is None:
                            bw_improved[use0] = (self.bw_images[i1]-min)/(max-min)*self.gains[i1]
                        else:
                            bw_improved[use0] = bw_improved[use0] + (self.bw_images[i1]-min)/(max-min)*self.gains[i1]

                        use1 = self.mapping[i1-3][1]
                        if bw_improved[use1] is None:
                            bw_improved[use1] = (self.bw_images[i1]-min)/(max-min)*self.gains[i1]
                        else:
                            bw_improved[use1] = bw_improved[use1] + (self.bw_images[i1]-min)/(max-min)*self.gains[i1]

        #bw_improved_1d = [None]*3
        for i1 in range(3):
            if bw_improved[i1] is not None:
                bw_improved[i1] = np.clip(bw_improved[i1],0,255)
                bw_improved[i1] = bw_improved[i1].astype(np.uint8)
                #bw_improved_1d[i1] = bw_improved[i1].reshape(-1)
        
        if (bw_improved[0] is None) and (bw_improved[1] is None) and (bw_improved[2] is None):
            bw_improved[0] = np.zeros(1,dtype=np.uint8)
            bw_improved[1] = np.zeros(1,dtype=np.uint8)
            bw_improved[2] = np.zeros(1,dtype=np.uint8)
        if (bw_improved[0] is None) and (bw_improved[1] is not None):
            bw_improved[0] = np.zeros(bw_improved[1].shape,dtype=np.uint8)
        if (bw_improved[0] is None) and (bw_improved[2] is not None):
            bw_improved[0] = np.zeros(bw_improved[2].shape,dtype=np.uint8)
        if (bw_improved[1] is None) and (bw_improved[0] is not None):
            bw_improved[1] = np.zeros(bw_improved[0].shape,dtype=np.uint8)
        if (bw_improved[1] is None) and (bw_improved[2] is not None):
            bw_improved[1] = np.zeros(bw_improved[2].shape,dtype=np.uint8)    
        if (bw_improved[2] is None) and (bw_improved[0] is not None):
            bw_improved[2] = np.zeros(bw_improved[0].shape,dtype=np.uint8)
        if (bw_improved[2] is None) and (bw_improved[1] is not None):
            bw_improved[2] = np.zeros(bw_improved[1].shape,dtype=np.uint8)  

        
        self.improved = cv2.merge((bw_improved[0], bw_improved[1], bw_improved[2]))

        height, width, channel = self.improved.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.improved.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)

        label_width = self.imageLabel.width()
        window_height = self.height()
        ratio = height/width

        if ratio*label_width < window_height-100:
            improved_scaled = qImg.scaledToWidth(label_width)
        else:
            improved_scaled = qImg.scaledToHeight(window_height-100)
        

        self.imageLabel.setPixmap(QPixmap.fromImage(improved_scaled))

    def calculate_min_max1(self,img):
        bins = int(2**16/self.mean)
        hist,bin_edges = np.histogram(img,bins=bins,range=(0,2**16))

        hist_max = np.max(hist)
        hist_min = np.min(hist)
        limit = hist_min+(hist_max-hist_min)*self.limitSpinner.value()

        nmax = np.argmax(hist)
        result_min = np.where(hist[0:nmax]<limit)
        result_max = np.where(hist[nmax:]<limit)
        return result_min[0][-1]*self.mean,(nmax+result_max[0][0])*self.mean

    def reload(self,filename,color):
        if filename != "":
            self.bw_images[color] = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            if self.bw_images[color] is None:
                self.statusbar.showMessage("Could not load file: "+filename,3000)
                return False
            self.bw_1d[color] = self.bw_images[color].reshape(-1)
            min,max = self.calculate_min_max1(self.bw_1d[color])
            self.maxSpinners[color].setValue(int(max))
            self.maxSpinners[color].setSingleStep(int(max/self.steps))
            self.minSpinners[color].setValue(int(min))
            self.minSpinners[color].setSingleStep(int(max/self.steps))
            self.update_hist(color)
    
    def update_hist(self,color):
        if self.loaded:
            red_max = self.maxSpinners[color].value()
            red_min = self.minSpinners[color].value()

            if self.graphs[color]:
                self.graphs[color].clear()

            bins = int(2**16/self.mean)
            xaxis = np.arange(0,2**16,self.mean)
            hist,bin_edges = np.histogram(self.bw_1d[color],bins=bins,range=(0,2**16))
            self.red_plot = self.graphs[color].plot(xaxis,hist,pen='k')
            self.graphs[color].setXRange(0, red_max*1.5, padding=0)
            
            max_line = pg.InfiniteLine(pos=red_max,pen='r')
            self.graphs[color].addItem(max_line)

            min_line = pg.InfiniteLine(pos=red_min,pen='g')
            self.graphs[color].addItem(min_line)

            xaxis_slope = np.arange(red_min,red_max)
            nuse = len(xaxis_slope)
            slope = np.linspace(0,max(hist),nuse)

            curve = self.graphs[color].plot(xaxis_slope,slope,pen='b')
            self.graphs[color].addItem(curve)

            self.display_image()

    def load_image(self,color):
        if self.loaded:
            fname = QFileDialog.getOpenFileName(self,'Open file')
            self.files[color].setText(fname[0])
            self.reload(fname[0],color)

    def select_safe_file(self):
        fname = QFileDialog.getSaveFileName(self,'Browse safe file', '', "Image Files (*.png *.jpg)")
        self.saveFile.setText(fname[0])

    def save_image(self):
        fname = self.saveFile.text()
        if fname != '':
            if self.improved is not None:
                cv2.imwrite(fname,cv2.cvtColor(self.improved, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 100])
                self.statusbar.showMessage("Image saved",1000)


                settings = {}
                settings['red_filename'] = self.redFile.text()
                settings['green_filename'] = self.greenFile.text()
                settings['blue_filename'] = self.blueFile.text()
                settings['magenta_filename'] = self.magentaFile.text()
                settings['yellow_filename'] = self.yellowFile.text()
                settings['cyan_filename'] = self.cyanFile.text()
                
                settings['red_max'] = self.redMaxSpinner.value()
                settings['red_min'] = self.redMinSpinner.value()
                settings['green_max'] = self.greenMaxSpinner.value()
                settings['green_min'] = self.greenMinSpinner.value()
                settings['blue_max'] = self.blueMaxSpinner.value()
                settings['blue_min'] = self.blueMinSpinner.value()
                settings['magenta_max'] = self.magentaMaxSpinner.value()
                settings['magenta_min'] = self.magentaMinSpinner.value()
                settings['yellow_max'] = self.yellowMaxSpinner.value()
                settings['yellow_min'] = self.yellowMinSpinner.value()
                settings['cyan_max'] = self.cyanMaxSpinner.value()
                settings['cyan_min'] = self.cyanMinSpinner.value()

                settings['save_file'] = self.saveFile.text()


                settings['limit'] = self.limitSpinner.value()
                settings['mean'] = self.mean
                settings['version'] = self.version

                
                with io.open(fname[:-4]+'_metadata.yaml', 'w', encoding='utf8') as outfile:
                    yaml.dump(settings, outfile, default_flow_style=False, allow_unicode=True)
            else:
                self.statusbar.showMessage("No Image to be saved",1000)
        else:
            self.statusbar.showMessage("Safe filename cannot be empty",1000)

    


def main():
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('useOpenGL',1)

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()