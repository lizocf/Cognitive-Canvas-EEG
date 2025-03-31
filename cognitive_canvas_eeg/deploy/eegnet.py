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

class EEGNet(nn.Module):
    def __init__(self, num_channels=14, num_classes=5, verbose=False):
        super(EEGNet, self).__init__()
        self.num_channels = num_channels
        self.num_classes = num_classes
        self.verbose = verbose

        # Layer 1: Temporal Convolution
        self.conv1 = nn.Conv2d(1, 16, (1, num_channels), padding=0)  # (Batch, 1, EEG_Channels, Timepoints)
        self.batchnorm1 = nn.BatchNorm2d(16, False)

        # Layer 2: Depthwise Convolution + Pooling
        self.padding1 = nn.ZeroPad2d((16, 17, 0, 1))
        self.conv2 = nn.Conv2d(16, 4, (2, 32))  # Ensure 16 input channels match output of conv1
        self.batchnorm2 = nn.BatchNorm2d(4, False)
        self.pooling2 = nn.MaxPool2d((1, 4))  

        # Layer 3: Further Convolution + Pooling
        self.padding2 = nn.ZeroPad2d((2, 1, 4, 3))
        self.conv3 = nn.Conv2d(4, 4, (8, 4))
        self.batchnorm3 = nn.BatchNorm2d(4, False)
        self.pooling3 = nn.MaxPool2d((1, 4))  

        # Fully Connected Layer (Compute dynamically)
        fc_input_dim = self._compute_fc_input_dim()
        self.fc1 = nn.Linear(fc_input_dim, num_classes)

    def _compute_fc_input_dim(self):
        # Run a forward pass with dummy data to compute the correct size
        # dummy_input = torch.randn(1, 1, self.num_channels, 1281)  # (batch, 1, 14, 1281)
        dummy_input = torch.randn(1, 1, self.num_channels, 256)  # (batch, 1, 14, 1281)
        dummy_output = self._forward_features(dummy_input)
        return dummy_output.view(1, -1).shape[1]

    def _forward_features(self, x):
        """Forward pass through feature extraction layers only (used for FC size computation)"""
        x = F.elu(self.conv1(x))
        x = self.batchnorm1(x)
        x = F.dropout(x, 0.25)

        x = self.padding1(x)
        x = F.elu(self.conv2(x))
        x = self.batchnorm2(x)
        x = F.dropout(x, 0.25)
        x = self.pooling2(x)

        x = self.padding2(x)
        x = F.elu(self.conv3(x))
        x = self.batchnorm3(x)
        x = F.dropout(x, 0.25)
        x = self.pooling3(x)
        return x

    def forward(self, x):
        if self.verbose:
            print(f"[INPUT] {x.shape}")

        x = x.unsqueeze(1)  # Add channel dimension -> (batch, 1, 14, 1281)
        
        # Layer 1
        x = F.elu(self.conv1(x))
        x = self.batchnorm1(x)
        x = F.dropout(x, 0.25)
        if self.verbose:
            print(f"[CONV1] {x.shape}")

        # Layer 2
        x = self.padding1(x)
        x = F.elu(self.conv2(x))
        x = self.batchnorm2(x)
        x = F.dropout(x, 0.25)
        x = self.pooling2(x)
        if self.verbose:
            print(f"[CONV2] {x.shape}")

        # Layer 3
        x = self.padding2(x)
        x = F.elu(self.conv3(x))
        x = self.batchnorm3(x)
        x = F.dropout(x, 0.25)
        x = self.pooling3(x)
        if self.verbose:
            print(f"[CONV3] {x.shape}")

        # Flatten & Fully Connected Layer
        x = x.view(x.shape[0], -1)  
        if self.verbose:
            print(f"[FLATTEN] {x.shape}")

        x = self.fc1(x)
        if self.verbose:
            print(f"[FC1] {x.shape}")

        return x

