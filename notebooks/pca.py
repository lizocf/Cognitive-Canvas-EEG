import sys
import os
import random
import math
import time
import torch; torch.utils.backcompat.broadcast_warning.enabled = True
from torchvision import transforms, datasets
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim
import torch.backends.cudnn as cudnn; cudnn.benchmark = True
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC 
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import GridSearchCV 

torch.manual_seed(64471388412500)

NUM_CLASSES = 5
NUM_CHANNELS = 14
T = 1 # seconds
SR = 128 # hz

feature_df = pd.read_csv(f'../data/lzl_processed/feature_df.csv')
# feature_df = feature_df.drop(columns=['Label'])

labels = feature_df['Label']
training = feature_df.drop(columns=['Label'])


training = training[['hjorth_activity_EEG.F3', 'hjorth_activity_EEG.FC5', 'hjorth_activity_EEG.F4', 'hjorth_activity_EEG.FC6',
              'hjorth_mobility_EEG.F3', 'hjorth_mobility_EEG.FC5', 'hjorth_mobility_EEG.F4', 'hjorth_mobility_EEG.FC6',
              'hjorth_complexity_EEG.F3', 'hjorth_complexity_EEG.FC5', 'hjorth_complexity_EEG.F4', 'hjorth_complexity_EEG.FC6',
              'katz_FD_EEG.F3', 'katz_FD_EEG.FC5', 'katz_FD_EEG.F4', 'katz_FD_EEG.FC6']]


scaler = StandardScaler()
scaled_data = scaler.fit_transform(np.array(training))

pca = PCA(n_components=4)  # Retain 2 principal components
pca.fit(scaled_data)

pca_data = pca.transform(scaled_data)

X_train, X_temp, y_train, y_temp = train_test_split(pca_data, labels, test_size=0.3333, random_state=17)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.666, random_state=17)

# logreg = LogisticRegression(solver='lbfgs', max_iter=9000,random_state=16)

# # fit the model with data
# logreg.fit(X_train, y_train)

# y_pred = logreg.predict(X_val)

# print('Model accuracy score with default hyperparameters: {0:0.4f}'. format(accuracy_score(y_val, y_pred)))

grid={"C":np.logspace(-5,5,20), "penalty":["l2"], "solver":['newton-cg', 'newton-cholesky', 'saga']}

logreg=LogisticRegression(max_iter=3500,random_state=16)
logreg_cv=GridSearchCV(logreg,grid,cv=5)
logreg_cv.fit(X_train,y_train)

print("tuned hpyerparameters :(best parameters) ",logreg_cv.best_params_)
print("accuracy :",logreg_cv.best_score_)