"""
Title: mlp.py
Reference: https://github.com/lukasruff/Deep-SAD-PyTorch/tree/master/src/networks
"""

from .base_net import BaseNet
from helper import utils
import torch
import torch.nn as nn
import torch.nn.functional as F


class MLP(BaseNet):

    def __init__(self, x_dim, h_dims='32-16', rep_dim=8, bias=False):
        super().__init__()

        self.rep_dim = rep_dim
        self.h_dims = utils.str_to_list(h_dims)

        neurons = [x_dim, *self.h_dims]
        layers = [Linear_BN_leakyReLU(neurons[i - 1], neurons[i], bias=bias) for i in range(1, len(neurons))]
        self.hidden = nn.ModuleList(layers)
        self.code = nn.Linear(self.h_dims[-1], rep_dim, bias=bias)

    def forward(self, x):
        x = x.view(int(x.size(0)), -1)
        for layer in self.hidden:
            x = layer(x)
        return self.code(x)


class MLP_Decoder(BaseNet):

    def __init__(self, x_dim, h_dims='32-16', rep_dim=8, bias=False):
        super().__init__()

        self.rep_dim = rep_dim
        self.h_dims = utils.str_to_list(h_dims)

        neurons = [rep_dim, *self.h_dims]
        layers = [Linear_BN_leakyReLU(neurons[i - 1], neurons[i], bias=bias) for i in range(1, len(neurons))]

        self.hidden = nn.ModuleList(layers)
        self.reconstruction = nn.Linear(self.h_dims[-1], x_dim, bias=bias)
        self.output_activation = nn.Sigmoid()

    def forward(self, x):
        x = x.view(int(x.size(0)), -1)
        for layer in self.hidden:
            x = layer(x)
        x = self.reconstruction(x)
        return self.output_activation(x)


class MLP_Autoencoder(BaseNet):

    def __init__(self, x_dim, h_dims='32-16', rep_dim=8, bias=False):
        super().__init__()

        self.rep_dim = rep_dim
        self.h_dims = h_dims
        self.reverse_h_dims = list(reversed(utils.str_to_list(h_dims)))
        self.reverse_h_dims = '-'.join(str(i) for i in self.reverse_h_dims)

        self.encoder = MLP(x_dim, self.h_dims, rep_dim, bias)
        self.decoder = MLP_Decoder(x_dim, self.reverse_h_dims, rep_dim, bias)

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


class Linear_BN_leakyReLU(nn.Module):
    """
    A nn.Module that consists of a Linear layer followed by BatchNorm1d and a leaky ReLu activation
    """

    def __init__(self, in_features, out_features, bias=False, eps=1e-04):
        super(Linear_BN_leakyReLU, self).__init__()

        self.linear = nn.Linear(in_features, out_features, bias=bias)
        self.bn = nn.BatchNorm1d(out_features, eps=eps, affine=bias)

    def forward(self, x):
        return F.leaky_relu(self.bn(self.linear(x)))
