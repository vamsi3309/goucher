"""
this pre processor selects one every "skip_count" images in the sample 
for example if the sample has 100 images, out put will have 20 for skip_count =5 

test samples will have only one image chosen at random 
"""
from src.preprocessing.preprocessor import preprocessor
import numpy as np
import cv2
from numpy import array, zeros
import os
from glob import  glob
import cv2
import json


class BasicVariance ( preprocessor ):

    def __init__(self, exportPath, trainingPath , testPath , images_size=[640,640], importPath = None , skip_count =5):
        self.exportPath = exportPath
        self.trainingPath = trainingPath
        self.testPath = testPath
        self.image_size = images_size
        self.importPath = importPath
        self.skip_count = skip_count
        self.name = "BasicVariance_" + str(skip_count)
        self.x_test = None
        self.y_train = None
        self.x_train = None



    def preprocess(self):
        """
        this funciton preopricess the imagaes into three arays, test_x tarin_x , train_y
        :return:
        """
        train_x = [] # None #np.array([])
        train_y = []  # None # np.array([])
        train_vars = []
        # create the trainig set
        if( not  self.trainingPath is None):
            for sample in sorted(os.listdir(self.trainingPath)) :

                mask_path = os.path.join( self.trainingPath, sample + '/mask.png')

                # make varinaces
                if os.path.exists(os.path.join( self.trainingPath, sample + '/basicVariance.png')  ):
                    the_var = cv2.imread( os.path.join( self.trainingPath, sample + '/basicVariance.png') ,0 )
                else:
                    files = sorted( glob( os.path.join(self.trainingPath, "%s/frame*.png" % sample) ) )
                    files = np.array([self.change_size(cv2.imread(x, 0)) for x in files])
                    variances = np.var(files, axis=0)
                    variances = (variances / np.max(variances)) * 255

                    del (files )

                    cv2.imwrite( os.path.join( self.trainingPath, sample + '/basicVariance.png'), variances )

                    the_var = variances

                the_var = np.expand_dims(the_var.reshape(the_var.shape + (1,)), axis=0)
                # load train_y
                y = self.change_size(cv2.imread( mask_path, 0))
                y= np.expand_dims( y, axis=0 )
                y=( y==2 ).astype(int)

                # take under account the skip count and lod the images
                t = [  self.change_size(cv2.imread(os.path.join(self.trainingPath, "%s/frame%04d.png" % (sample, i)),0))  for i in range(0, 99, self.skip_count) ]
                t = [ np.expand_dims(x, axis=0)  for x in t ]
                train_x.extend(t)
                for i in range( len(t)):
                    train_y.append(y)
                    train_vars.append(the_var)

        # create the test set
        # test_x = []
        test_dic = {}
        test_size_ref = {}
        test_vars = {}
        if not self.testPath is None:
            for sample in sorted(os.listdir(self.testPath)):
                # image = cv2.imread(os.path.join(self.testPath, "%s/frame0050.png" % sample),0) #/ 255
                # test_size_ref[sample]= image.shape
                # image = self.change_size(image)
                # image = image.reshape(image.shape + (1,))
                # test_dic[sample] = np.expand_dims(image, axis=0)
                print (os.path.join(self.testPath, "%s/frame%04d.png" % (sample, i)))
                if  '.DS_Store' in sample : continue
                the_var= None
                # make varinaces
                if  os.path.exists(os.path.join(self.testPath, sample + '/basicVariance.png')):
                    the_var = cv2.imread(os.path.join(self.testPath, sample + '/basicVariance.png'), 0)
                else:
                    files = sorted(glob(os.path.join(self.testPath, "%s/frame*.png" % sample)))
                    files = np.array([self.change_size(cv2.imread(x, 0)) for x in files])
                    variances = np.var(files, axis=0)
                    variances = (variances / np.max(variances)) * 255
                    del (files )
                    cv2.imwrite(os.path.join(self.testPath, sample + '/basicVariance.png'), variances)

                    the_var = variances

                the_var = np.expand_dims(the_var.reshape(the_var.shape + (1,)), axis=0)
                test_vars[sample] = the_var

                t = [cv2.imread(os.path.join(self.testPath, "%s/frame%04d.png" % (sample, i)), 0)
                     for i in range(0, 99, 8)]

                test_size_ref[sample] = t[0].shape

                t = [ self.change_size(x) for x in  t ]

                t = [np.expand_dims(x.reshape(x.shape + (1,)), axis=0)  for x in t]

                temp_vars  = []
                for i in range ( len(t) ):
                    temp_vars.append(the_var)

                test_vars[sample] = np.vstack(temp_vars)


                test_dic[sample] = np.vstack(t)



                # test_x.append(np.expand_dims(image, axis=0))

        train_x = np.vstack(train_x)
        train_y = np.vstack(train_y)
        train_vars = np.vstack(train_vars)
        # test_x = np.vstack(test_x)

        train_x = train_x.reshape(train_x.shape + (1,))
        train_y = train_y.reshape(train_y.shape + (1,))
        #test_x = test_x.reshape(test_x.shape + (1,))

        print(train_x.shape)
        print(train_y.shape)
        # print(test_x.shape)

        self.x_train = train_x
        # self.x_test = test_x
        self.y_train = train_y

        # if( not self.exportPath is None):
        #     self.save_to_file()

        return train_x , train_y , test_dic, test_size_ref, train_vars, test_vars