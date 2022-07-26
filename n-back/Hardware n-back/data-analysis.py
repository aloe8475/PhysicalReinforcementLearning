







import sys
import os
from datetime import datetime
import time as Tiempo
import numpy as np
import csv
import pandas 
import re
from numpy.random import default_rng

from scipy import signal as sg
from scipy import stats
"""
GUI/ VISUAL
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import LinearLocator

plt.style.use('ggplot')
mpl.rcParams['figure.facecolor'] = '#ededed'
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QComboBox, QTextEdit, QFileDialog, QLabel, QLineEdit, QFrame, QCheckBox, QListWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import QTimer, QTime, QObject, pyqtSignal

from matplotlib.backends.qt_compat import QtCore, QtWidgets

if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

global downsample_rate
downsample_rate=10





default_dir_files='C:/Users/Adrian/Desktop/python_nidaq_may_current/'
default_save_dir='C:/Users/Adrian/Desktop/NBACK/saves_py/'
default_save_name='figure_plot'

"""
Style Sheets for changing the appearance of some application buttons
"""
StyleButCoral = """QPushButton{background-color:LightCoral;
                                            border-style:outset;
                                            border-width: 1px;
                                            border-color:#FDF5E6;
                                            padding:3px;
                                            transition:background-color 1s}
                                QPushButton:hover{background-color:azure;
                                                  border:0.5px solid LightCoral}
                                QPushButton:pressed{background-color:DarkGray;
                                            border-style: inset;
                                            border-width: 1px;
                                            border-color:Crimson;}"""
StyleButDarkGreen = """QPushButton{background-color:DarkGreen;
                                            border-style:outset;
                                            border-width: 1px;
                                            border-color:#FDF5E6;
                                            padding:3px;
                                            transition:background-color 1s}
                                QPushButton:hover{background-color:azure;
                                                  border:0.5px solid LightCoral}
                                QPushButton:pressed{background-color:DarkGray;
                                            border-style: inset;
                                            border-width: 1px;
                                            border-color:Crimson;}"""

exp_list = ['none', 'oscillo', 'lockin', 
            'control_four', 'iv_curve', 'delay', 
            'oscillo-keith', 'dig_switch', 'iv-keith',
            'multiple-probe','staircase','n_back']

class ApplicationWindow(QWidget):

    def __init__(self):
        """
        
        """

        super().__init__()
        # self._main = QtWidgets.QWidget()
        # self.setCentralWidget(self._main)

        layout = QGridLayout()
        self.setLayout(layout)

 
        # pixels
        inix =200
        iniy = 130
        main_width = 1600
        main_height = 700
        self.setGeometry(inix, iniy, main_width, main_height)

        


        
       

        """
        Add BUTTONS/EDITS
        """
        ButtonLayout = QVBoxLayout()
        self.buttonLoadData = QPushButton('Load')
        self.buttonLoadData.clicked.connect(self.load_from_file)
        ButtonLayout.addWidget(self.buttonLoadData,1)
        self.buttonSendChans = QPushButton('Send')
        self.buttonSendChans.clicked.connect(self.SendChannels)
        ButtonLayout.addWidget(self.buttonSendChans)
        self.ButtonSpecOps=QPushButton('DeleteAll')
        self.ButtonSpecOps.clicked.connect(self.DeleteAll)
        ButtonLayout.addWidget(self.ButtonSpecOps)
        self.ButtonProcess=QPushButton('SaveFigPng')
        self.ButtonProcess.minimumHeight()
        self.ButtonProcess.clicked.connect(self.SaveFig)
        ButtonLayout.addWidget(self.ButtonProcess)
        self.QDir=QTextEdit(default_save_dir)
        self.QDir.setFixedHeight(30)
        
        self.QName=QTextEdit(default_save_name)
        self.QName.setFixedHeight(30)
        self.MetaText = QTextEdit('Metahere')
        
        verlay=QHBoxLayout()
        #self.QList1.itemSelectionChanged.connect(self.DoThis) 
        self.QListPat= QListWidget()
        self.QListPat.setSelectionMode(QAbstractItemView.ExtendedSelection)

        verlay.addWidget(self.QListPat)
        #special kind of lists
        self.QListTest=QListWidget()
        self.QListTest.setSelectionMode(QAbstractItemView.ExtendedSelection)
       
        verlay.addWidget(self.QListTest)
        
        ButtonLayout.addWidget(self.QDir)
        ButtonLayout.addWidget(self.QName)
        ButtonLayout.addWidget(self.MetaText)
        ButtonLayout.addLayout(verlay)
        
        self.buttonSelect=QPushButton('Select Pattern')
        self.buttonSelect.clicked.connect(self.SelFromButton)
        ButtonLayout.addWidget(self.buttonSelect)
        
        
        
        
        
        """
        DATA LISTS
        """
        VerLay=QVBoxLayout()
        HorLay = QHBoxLayout()
        

        self.QList1 = QListWidget()
        self.QList1.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.QList1.itemSelectionChanged.connect(self.SelFromList1)
        
        self.QListChans=QListWidget()
        self.QListChans.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.QListChans.itemSelectionChanged.connect(self.SelFromList2)
    
        HorLay.addWidget(self.QList1)
        HorLay.addWidget(self.QListChans)
        
        GridButtons=QGridLayout()
        self.PlotSpecial=QPushButton('PlotSpecial')
        self.PlotSpecial.clicked.connect(self.PlotSpecialButton)
        self.CheckAccuracy=QCheckBox('ShowAccuracy')
        self.CheckCompress=QCheckBox('CompressTime')
        self.CheckThresChange=QCheckBox('ThreshChange')
       
        GridButtons.addWidget(self.PlotSpecial,0,0,3,1)
        GridButtons.addWidget(self.CheckAccuracy,0,1,1,1)
        GridButtons.addWidget(self.CheckCompress,1,1,1,1)
        GridButtons.addWidget(self.CheckThresChange,2,1,1,1)
        
        VerLay.addLayout(HorLay)
        VerLay.addLayout(GridButtons)
        Listlayout = QVBoxLayout()
        Listlayout.addLayout(VerLay,5)
 
        

        """
       .FIGURE
        """
        plt.ioff()
        
        self.fig, self.axes = plt.subplots(tight_layout=True)
        self.axes2=self.axes.twinx() #auxiliary ax
        self.axes2.set_axis_off()
        self.canvas = FigureCanvas(self.fig)

        # self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                NavigationToolbar(dynamic_canvas, self))
        self.ToolBar = NavigationToolbar(self.canvas, self)
        self.FigLayout = QVBoxLayout()
        self.FigLayout.addWidget(self.canvas)
        self.FigLayout.addWidget(self.ToolBar)
      
        
        self.fig2,self.axes3=plt.subplots(tight_layout=True)
        self.CanvasAux=FigureCanvas(self.fig2)
        self.ToolBarAux=NavigationToolbar(self.CanvasAux,self)
        
        self.FigAuxLayout=QVBoxLayout()
        self.FigAuxLayout.addWidget(self.CanvasAux)
        self.FigAuxLayout.addWidget(self.ToolBarAux)
        
        layout.addLayout(ButtonLayout,0,0,2,1)
        layout.setColumnStretch(0,1)
        layout.addLayout(Listlayout, 0, 1,2,1)
        layout.setColumnStretch(1,1)
        layout.addLayout(self.FigLayout, 0, 2,2,1)
        layout.setColumnStretch(2,3)
        layout.addLayout(self.FigAuxLayout,0,3,1,1)
        layout.setColumnStretch(3,1)
        
        
       # ButtonLayout.insertSpacing(-1, int(0.2 * main_height))
        
       

        



        """
        """
    


            
        #holder of pandas
        self.DataList = []
        self.MetaList=[]
        self.setWindowTitle('Analysis')
    
    def load_from_file(self):
        filedialog = QFileDialog.getOpenFileNames(self,'open file',directory=default_dir_files)
        filelist=filedialog[0]
        fnames=list()
        for file in filelist:
            fnames.append(file.split('/')[-1][:-4])
         
            
       
        datafiles,metafiles=self.open_and_transform(filelist)
        
        self.MetaList.extend(metafiles)
        self.DataList.extend(datafiles)
        
        self.QList1.addItems(fnames)
        self.convert_meta_to_txt_list(self.MetaList[0])

        return
    

    
    def open_and_transform(self,infiles):
        #file dialog for chosing files and transform data to pandas
        datafiles=list()
        metafiles=list()


        for fpath in infiles:
    
            with open(fpath) as csvDataFile:
                csvReader=csv.reader(csvDataFile)
                header=self.HeaderReader(csvReader)
    
            #chan_names=ChannelReader(header)
            name=fpath.split('/')[-1][:-4]
            expname=[fn for fn in exp_list if name.find(fn)>=0][0]
           
            if expname=='n_back':
                chan_names=['out1','out2']
            df=pandas.read_csv(fpath,delimiter=';',header=None,skiprows=4,names=chan_names,quoting=3)
            #df=pandas.read_csv(fpath,delimiter=';',engine='python',
            #                   skiprows=4,names=chan_names,
            #                   error_bad_lines=False)
            chanref=chan_names[1]
            index0=df[chanref][df[chanref]==999].index[0:]
            last=index0[-1]
            
            df=df[0:last+3].copy()
            
            ndf=self.process_file(df,header,chanref)
           
            datafiles.append(ndf)
            metafiles.append(header)
            
                    
                      

        return datafiles,metafiles

    

    def SaveFig(self):
        base_dir=self.QDir.toPlainText()
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        
        
        
        filename=self.QName.toPlainText()
        t=datetime.now().strftime("_%H_%M_%S")
        aux='_aux_'
        
        fpath=base_dir+filename+t  
        fpath_aux=base_dir+filename+aux+t
        self.fig.savefig(fpath)
        self.fig2.savefig(fpath_aux)
    
        return

        
    def HeaderReader(self,csVReader):
        #read csv file header
        headlen=4
        lin=[]
        for i in range(headlen-1):
            line=next(csVReader)
            lin.append(line)
        ls2=[]
        for val in lin[2]:
            try:
                ls2.append(float(val))
            except:
                ls2.append(val)
                
        return dict(zip(lin[0],ls2))
    
    def process_file(self,pandata,header,chanref):
        """
        processing files of n_back according to current file formatting
        There is a marker between intervals (number 999). The next two rows of data
        contain information about which pattern was in input(4 electrode)/output(2 electrode) 
        and whether it was train or test interval.
        Example: 
            out1 out2
        idx
       100     999  999  -> 999 is marker of previous interval end
       101     5    0    -> 5 is input pattern (0101 in binary, ie. two electrodes opened). 0 is train interval (1 would be test)
       102     1    -1   -> 1 is output pattern (01 in binary, ie. one output electrode being trained). -1 does not have meaning.
        """
        sel=list(pandata[chanref][pandata[chanref]==999].index)
        sel2=sel.copy()
        sel.insert(0,-3)
        sel.pop(-1)
        
        index_start=list()
        index_end=list()
        interval=list()
        pat=list()
        outpat=list()
        descript=list()
        Vout1=list()
        Vout2=list()
        Time=list()
        thresh1=list()
        thresh2=list()
        TrainOrTest=lambda a:'Train' if a==0 else 'Test'
        bin_str= lambda a: bin(int(a))[2:] if bin(int(a))[2:][-1]=='0' else '0'+bin(int(a))[2:]
        time_off=0
        for i1,i2 in zip(sel,sel2):
            index_start.append(i1+3)
            index_end.append(i2)
            interval.append(TrainOrTest(pandata.iloc[i2+1,1]))
            pat.append(pandata.iloc[i2+1,0])
            outpat.append(pandata.iloc[i2+2,0])
            thresh1.append(pandata.iloc[i2+2,1])
            thresh2.append(pandata.iloc[i2,0])
            descript.append(TrainOrTest(pandata.iloc[i2+1,1])+'_IN:'+bin_str(pat[-1])+'__OUT:'+bin_str(outpat[-1]))
            
            
            
            
            vo1=np.array(pandata['out1'][i1+3:i2])
            extra_v1=np.random.choice(vo1[-10:],3) #this is just for index matching w. time. does not impact results.
            vo2=np.array(pandata['out2'][i1+3:i2])
            extra_v2=np.random.choice(vo2[-10:],3)
            Vout1.extend(list(np.concatenate((vo1,extra_v1))))
            Vout2.extend(list(np.concatenate((vo2,extra_v2))))
            par_t=self.CreateTimeArray(pandata['out1'][i1+3:i2],header,downsample=downsample_rate)+time_off
            time_off=max(par_t)
            Time.extend(list(par_t))
            Time.extend([999,999,999])
        
        
        index_start=pandas.DataFrame(index_start)
        index_end=pandas.DataFrame(index_end)
        interval=pandas.DataFrame(interval)
        pat=pandas.DataFrame(pat)
        outpat=pandas.DataFrame(outpat)
        thresh1=pandas.DataFrame(thresh1)
        thresh2=pandas.DataFrame(thresh2)
        
        descript=pandas.DataFrame(descript)
        Vout1=pandas.DataFrame(Vout1)
        Vout2=pandas.DataFrame(Vout2)
        Time=pandas.DataFrame(self.CreateTimeArray(pandata[chanref],header,downsample=downsample_rate))
       
        pdout=pandas.concat([pandata,Time,Vout1,Vout2,index_start,index_end,interval,thresh1,thresh2,pat,outpat,descript]
                         ,axis=1,ignore_index=True)
        
        pdout.columns=['out1','out2','Time','Vout1','Vout2','index_start','index_end','interval','thresh1','thresh2','pat',
                      'outpat','descript']
        return pdout
    
    def CreateTimeArray(self,pandata,header=[],downsample=1,rate=1):
        #create time array from sampled acquisition
        tlen=pandata.shape[0]
        if header:
           
            rate=np.divide(1,int(header['Rate'])/downsample)
                
        else:
            rate=np.divide(1,int(rate)/downsample)
        
        return np.linspace(0,rate*tlen,tlen) 


  
        
    def convert_meta_to_txt_list(self,meta):
        text=''
        self.MetaText.setPlainText(text)
        nl='\n'
        for key,value in meta.items():
            text=text+str(key)+' : '+str(value)+nl
        
        self.MetaText.setPlainText(text)
        
    def DeleteAll(self):
        self.MetaList=[]
        self.DataList=[]
        self.QList1.itemSelectionChanged.disconnect()
        self.QList1.clear()
        self.QList1.itemSelectionChanged.connect(self.SelFromList1)
        
        self.QListChans.itemSelectionChanged.disconnect()
        self.QListChans.clear()
        self.QListChans.itemSelectionChanged.connect(self.SelFromList2)
        
        self.QListPat.clear()
        self.QListTest.clear()
        return




    def SendChannels(self):
        selIndex=self.QList1.selectedIndexes() #list of selected items, the item position is accesed when selIndex[idx].row() is called
        pos_index=[ind.row() for ind in selIndex]
        exp_name='multiple_probe'
        for ind in pos_index:
            pd=self.DataList[ind]
            if exp_name=='multiple_probe':
                self.mp_patlist,self.mp_patind=self.pat_list_ind(pd)
                strpat=list()
                for pat in self.mp_patlist:
                    strpat.append(str(pat))
                self.QList2.addItems(strpat)
            
        
        return


    def SelFromList1(self):
        selIndex=self.QList1.selectedIndexes()
        pos_index=selIndex[0].row()
        #print(pos_index)
        
        
        
        selData=self.DataList[pos_index]
        selMeta=self.MetaList[pos_index]
        columns=list(selData['descript'].dropna())
      
        self.convert_meta_to_txt_list(selMeta)
        
        
        
        
        self.QListPat.clear()
        self.QListPat.addItems(list(selData.pat.dropna().unique().astype('str')))
        
        self.QListTest.clear()
        self.QListTest.addItems(list(selData.interval.dropna().unique()))
        
        self.QListChans.clear()
        self.QListChans.addItems(columns)

        return
     
    def SelFromButton(self):
        if self.QListPat.count()==0:
            return
        if not self.QListPat.selectedIndexes():
            self.QListPat.selectAll()
        if not self.QListTest.selectedIndexes():
            self.QListTest.selectAll()
            
            
            
        cPat=[float(pat.data()) for pat in self.QListPat.selectedIndexes()]
        cInt=[int.data() for int in self.QListTest.selectedIndexes()]

        pandata=self.DataList[self.QList1.selectedIndexes()[0].row()]
        slice_ind=pandata.loc[:,['index_start']][(pandata['pat'].isin(cPat)) & (pandata['interval'].isin(cInt))]
        listpos=list(slice_ind.index)
        pos=-1
        
        self.QListChans.itemSelectionChanged.disconnect()
        self.QListChans.clearSelection()
        for idx in listpos:
            pos+=1
            if pos==len(listpos)-1:
                self.QListChans.itemSelectionChanged.connect(self.SelFromList2)
                
            self.QListChans.item(idx).setSelected(True)
        
        
        return

        
        
    def PlotSpecialButton(self):
        seldataset=self.QList1.selectedIndexes()
        selIndex=self.QListChans.selectedIndexes()
        pos_data=seldataset[0].row()
        pos_index=[Index.row() for Index in selIndex]
        pos_index.sort()

        
        pandata=self.DataList[pos_data]
        header=self.MetaList[pos_data]
        
        self.clear_axes()
        
        self.plot_special(pandata,header,pos_index)
        
        return
    
    def SelFromList2(self):
     
        seldataset=self.QList1.selectedIndexes()
        selIndex=self.QListChans.selectedIndexes()
        pos_data=seldataset[0].row()
        pos_index=[Index.row() for Index in selIndex]
        
        
        pos_index.sort()
        

        
        pandata=self.DataList[pos_data]
        header=self.MetaList[pos_data]
        
        self.clear_axes()
        self.plot_multiple(pandata,header,indexes=pos_index)

        return
    def clear_axes(self):
        
        self.axes2.clear()      
        self.axes.clear()
       
        self.axes2.set_axis_off()
        
        
        return
    def plot_multiple(self,pandata,header,indexes=[]):
        if not indexes:
            return
        
        pandataS=pandata.loc[indexes]
        slice_ind=pandataS.loc[:,['index_start','index_end']]
       
    
        
                        
        col_space=np.linspace(0,0.5,slice_ind.shape[0])
        
        for row,fr in zip(slice_ind.iterrows(),col_space):
                i1=row[1]['index_start']
                i2=row[1]['index_end']
                y1=pandata.loc[i1:i2-1,'out1']
                y2=pandata.loc[i1:i2-1,'out2']
                x=self.CreateTimeArray(y1,header,downsample_rate)
                b=(fr,fr,1)
                r=(1,fr,fr)
                self.axes.plot(x,y1,color=b)
                self.axes.plot(x,y2,color=r)
                
                #there are some problems w. twinaxis, quick fix.
                xmin=min(x)-0.05*(max(x)-min(x))
                xmax=max(x)+0.05*(max(x)-min(x))
                self.axes.set_xlim(xmin,xmax)
                
                self.axes.set_xlabel('Time(s)')
                self.axes.set_ylabel('Current(V)')
                self.axes.set_title('Current vs. Time ')
                
        self.canvas.draw()
        return 
    
    def plot_special(self,pandata,header,indexes=[]):
        if not indexes:
            return
        
        
        pandataS=pandata.loc[indexes]
        
        sliceT=pandataS.loc[:,['index_start','index_end']]
        target=pandataS.loc[:,['outpat']]
        
        checkAcc=lambda result,target: 1 if result==target else 0
        
        compress=self.CheckCompress.isChecked()
        accuracy=self.CheckAccuracy.isChecked()
        thresh=self.CheckThresChange.isChecked()
       
        targets_in=[int(pat) for pat in header['PatList'].split(',')]
        target_out=[int(pat) for pat in header['OutPat'].split(',')]

        #t=CreateTimeArray(y1,header,downsample_rate)
        #['Time']
        
        
        #plot scatter dots accuracy
        x_ac1=list()
        y_ac1=list()
        
        x_ac2=list()
        y_ac2=list()
       
        time_off=0
        init=pandata.loc[pandataS.loc[sliceT.index[0],'index_start'],'Time']
        
 
        tlims=[init,init]
        
        
        midlist=list()
        threshlist1=list()
        threshlist2=list()
        fulltime=list()
        
        for idx,row in sliceT.iterrows():
            testing_pat=pandata.loc[idx,'pat']
            out_pat=pandata.loc[idx,'outpat']
           
            
            i1=row['index_start']
            i2=row['index_end']
            y1=pandata.loc[i1:i2-1,'out1']
            y2=pandata.loc[i1:i2-1,'out2']
            if compress:
                t=self.CreateTimeArray(y1,header,downsample_rate)
                t=t+time_off
                time_off=max(t)
                tlims=[0,time_off]
                
            else:
                t=pandata.loc[i1:i2-1,'Time']
                tlims=self.checktimeLimits(t,tlims)
                
            
            
            
            self.axes.plot(t,y1,color='b')
            self.axes.plot(t,y2,color='r')
            
            self.axes.set_xlabel('Time(s)')
            self.axes.set_ylabel('Current(V)')
            self.axes.set_title('Current vs. Time ')
            
            midtime=t.mean()
            thresh_pat1=pandata.loc[idx,'thresh1']
            thresh_pat2=pandata.loc[idx,'thresh2']
            
            midlist.append(midtime)
            threshlist1.append(thresh_pat1)
            threshlist2.append(thresh_pat2)

                
                
                
            if (out_pat==-1):
                
                endtime=max(t)
                fulltime.append(endtime)
                
               
                av=[y1.mean(),y2.mean()]
                booled=[int(el/max(av)) for el in av]
                
                winner=self.bool_to_int(booled)
                
                target_idx=targets_in.index(testing_pat)
                target=target_out[target_idx]
                
                if target==1:
                    x_ac1.append(midtime)
                    y_ac1.append(checkAcc(winner,target))
                if target==2:
                    x_ac2.append(midtime)
                    y_ac2.append(checkAcc(winner,target))
                
               
                
       
              
        if ((x_ac1) or (x_ac2)) and (accuracy):
            self.axes2.set_axis_on()
            
            #self.axes2.scatter(x_ac1,y_ac1,color='blue')
            #self.axes2.scatter(x_ac2,y_ac2,color='red')
            if x_ac1:    
                self.axes2.stem(x_ac1,y_ac1,linefmt='b--',markerfmt='bo')
            if x_ac2:
                self.axes2.stem(x_ac2,y_ac2,linefmt='r--',markerfmt='ro')
            
            self.axes2.set_ylabel('accuracy')
            self.axes2.grid(False)
            comb=y_ac1+y_ac2
            perc=sum(comb)/len(comb)
            print('Percentage of correct :')
            print('-----------------------')
            print(perc)
            print('.......................')
            n_div=5
            min_y=-0.05 #extra room for better visualization
            max_y=(1-0.25*min_y)/0.75
            #just a trick to match 1 of accuracy with a tick and preserve matching grid
            
            self.axes2.set_ylim(min_y,max_y)
            #matching the grid lines
            self.axes.yaxis.set_major_locator(LinearLocator(n_div))
            self.axes2.yaxis.set_major_locator(LinearLocator(n_div))
        if ((x_ac1) or (x_ac2)) and (thresh):
            
                if threshlist2[0]==999:   
                #old version of data format, simulating change in threshold
                    c1,c2,tp=self.thresh_simulation(x_ac1,x_ac2,y_ac1,y_ac2,header)
                else:
                    c1=threshlist1
                    c2=threshlist2
                    tp=midlist
                
                
                
                
                
                
                #if midlist:
                #    for dat in midlist:
                #        self.axes.axvline(dat,color='green')
                
                self.axes3.clear()
                
                self.axes3.plot(tp,c1,'b')
                self.axes3.plot(tp,c2,'r')
                #self.axes3.scatter(tp,c1,s=70,c='k',marker='+')
                #self.axes3.scatter(tp,c2,s=70,c='k',marker='+')
                self.CanvasAux.draw()
        
        
        tmin=min(tlims)-0.05*(max(tlims)-min(tlims))
        tmax=max(tlims)+0.05*(max(tlims)-min(tlims))
        self.axes.set_xlim(tmin,tmax)
        self.canvas.draw()  

        return 
    
    def thresh_simulation(self,x_ac1,x_ac2,y_ac1,y_ac2,header):
        
        inithresh=header['PatThresh']
        VoltPenalty=header['VoltPenalty']
        min_pen=header['MinPenalty']
        max_pen=header['MaxPenalty']
        
        x_ar=np.array(x_ac1+x_ac2)
        y_ar=np.array(y_ac1+y_ac2)
        idx=np.argsort(x_ar)
        
        c1=np.ones(len(x_ac1))
        c2=2*np.ones(len(x_ac2))
        chan=np.concatenate((c1,c2))
        
        xchan=chan[idx]
        x_ar=x_ar[idx]
        y_ar=y_ar[idx]
        
        
        chan1_thresh=[inithresh]
        chan2_thresh=[inithresh]
        change_t=[x_ar[0]]
        
        
        #first element is alrady in place
        x_ar=x_ar[1:]
        y_ar=y_ar[1:]
        xchan=xchan[1:]
        
        t_count1=inithresh
        t_count2=inithresh
        for y,x,ch in zip(y_ar,x_ar,xchan):
            if (y==0) and (ch==1):
                t_count1=t_count1+VoltPenalty
                t_count2=t_count2-VoltPenalty
                
                t_count1=float(np.clip(t_count1,min_pen,max_pen))
                t_count2=float(np.clip(t_count2,min_pen,max_pen))
            if (y==0) and (ch==2):
                t_count1=t_count1-VoltPenalty
                t_count2=t_count2+VoltPenalty
                
                t_count1=float(np.clip(t_count1,min_pen,max_pen))
                t_count2=float(np.clip(t_count2,min_pen,max_pen))
            
            chan1_thresh.append(t_count1)
            chan2_thresh.append(t_count2)
            change_t.append(x)
            
        return chan1_thresh,chan2_thresh,change_t
    
    def checktimeLimits(self,t_arr,tlim=[0,0]):
        tmin=min(t_arr)
        tmax=max(t_arr)
        
        return [min(tmin,tlim[0]),max(tmax,tlim[1])]
    def str_to_bool_array(self,int_pat):
        pat=[int(d) for d in str(bin(int(int_pat)))[2:]]
        #print(pat)
        return pat
    

    def bool_to_int(self,bool_arr):
        numb=0

        for idx,el in enumerate(bool_arr):
            numb=2**(idx)*el+numb
        return numb
    
    
    def wfm_gen(self,set_ini,Freq=None,phase=None, sig=None, amp=None,ov_sig='sin',phas=0,points=0,keith='off'):
        """
        Waveform generations. For synchronized IV's, waveform has same number of smaples and rate
        as the data acquisition. Although this does not need to be like this, but then you would need to 
        recalculate different n_samples and time to match the acquisiton and generation rates.
        """
        if Freq is None:
            Freq=set_ini['Freq']
        if phase is None:
             Phase=set_ini['PhaseDec']*np.pi/180
        else: 
            Phase=phase*np.pi/180
        if sig is None:
            Signal=set_ini['Signal']
        else:
            Signal=sig
        if amp is None:
            Amp=set_ini['Amp']
        else:
            Amp=amp
            
    
        Off=set_ini['Offset']
        Rate=set_ini['Rate']
        Ncycles=set_ini['NCycles']
        if points==0:
            samps=Rate*Ncycles/Freq
            
        else:
            samps=points
            #Rate=Freq*points/Ncycles
            Ncycles=Freq*points/Rate
            Freq=Ncycles
            print(Freq)
        if keith=='on':
            Ncycles = set_ini['NCycles']
            samps=points
    
            Rate=points*Freq/Ncycles
        final_t=np.divide(samps,Rate)
        t=np.linspace(0,final_t,int(samps),endpoint=False)
    
         
        if Signal=='square':
            return t,(Amp)*sg.square(2*np.pi*Freq*t+Phase,set_ini['Duty'])+Off
        elif Signal=='triangle':
            return t,(Amp)*sg.sawtooth(2*np.pi*Freq*t+Phase,0.5)+Off
        elif Signal=='sawtooth':
            return t,(Amp)*sg.sawtooth(2*np.pi*Freq*t+Phase,1)+Off
        elif Signal=='sin':
            return t,(Amp)*np.sin(2*np.pi*Freq*t+Phase)+Off
        elif Signal=='cos':
            return t,(Amp)*np.cos(2*np.pi*Freq*t+Phase)+Off
        elif Signal=='const':
            return t,(Amp)*np.ones(len(t))
        else:
            print('no valid name')
            return 0



"""
****************************************************************************
\\\\\\\\\\\\\\\\\\\\\\\\\\\M  A   I   N ////////////////////////////////
****************************************************************************
"""



def __main__():
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)

    app=0 
    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
    del app

    #sys.exit(qapp.exec_())



# main
if __name__ == '__main__':
    __main__()