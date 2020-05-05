import torch
import torch.nn as nn
import numpy as np
import math
import point_cloud_utils as pcu
from torch_geometric.data import Batch

from relative_layer.neighborhood_encoder import NeighborhoodEncoder
from relative_layer.grid_deform_decoder import GridDeformationDecoder
from full_network.point_cloud_ae import PointCloudAE
from full_network.middlelayer_encoder import MiddleLayerEncoder
from full_network.middlelayer_decoder import MiddleLayerDecoder

RESULT_PATH = "D:/Documenten/Results/"


def get_neighborhood_encoder(latent_size, mean):
    return NeighborhoodEncoder(
        nbs_features=[32, 64, 64],
        nbs_features_global=[64, 32, latent_size],
        mean=mean
    )


def get_neighborhood_decoder(latent_size, nb_neighbors):
    return GridDeformationDecoder(
        input_size=latent_size,
        nbs_features_global=[32, 64, 64],
        nbs_features=[64, 32, 3],
        nb_neighbors=nb_neighbors
    )


NB_LAYERS = 3
NBS_NEIGHS = [25, 16, 9]
RADII = [0.23, 1.3, 2.0]

LAT1 = 8
LAT2 = 64
LAT3 = 128
MEAN = False

neigh_enc1 = get_neighborhood_encoder(LAT1, MEAN)
encoder1 = neigh_enc1
neigh_enc2 = get_neighborhood_encoder(LAT1, MEAN)
encoder2 = MiddleLayerEncoder(
    neighborhood_enc=neigh_enc2,
    input_size=LAT1,
    nbs_features=[64, 128, 128],
    nbs_features_global=[128, 64, LAT2],
    mean=MEAN
)
neigh_enc3 = get_neighborhood_encoder(LAT1, MEAN)
encoder3 = MiddleLayerEncoder(
    neighborhood_enc=neigh_enc3,
    input_size=LAT2,
    nbs_features=[128, 256, 256],
    nbs_features_global=[256, 128, LAT3],
    mean=MEAN
)

neigh_dec1 = get_neighborhood_decoder(LAT1, NBS_NEIGHS[-1])
decoder1 = MiddleLayerDecoder(
    neighborhood_dec=neigh_dec1,
    input_size=LAT3,
    nbs_features_global=[128, 256, LAT1],
    nbs_features=[128, 256, LAT2]
)
neigh_dec2 = get_neighborhood_decoder(LAT1, NBS_NEIGHS[-2])
decoder2 = MiddleLayerDecoder(
    neighborhood_dec=neigh_dec2,
    input_size=LAT2,
    nbs_features_global=[64, 128, LAT1],
    nbs_features=[64, 128, LAT1]
)
neigh_dec3 = get_neighborhood_decoder(LAT1, NBS_NEIGHS[-3])
decoder3 = neigh_dec3

ENCODERS = [encoder1, encoder2, encoder3]
DECODERS = [decoder1, decoder2, decoder3]


ae = PointCloudAE(
    NB_LAYERS,
    NBS_NEIGHS,
    RADII,
    ENCODERS,
    DECODERS
)

input_tens = torch.rand((7200, 3))
input_batch = torch.arange(2).repeat_interleave(3600)
batch_obj = Batch(pos=input_tens, batch=input_batch)

print(batch_obj)

points_list, batch_list, points_list_out, batch_list_out = ae(batch_obj)

length = len(points_list)
assert(length == len(batch_list))
assert(length == len(points_list_out))
assert(length == len(batch_list_out))

for i in range(length):
    print()
    print(points_list[i].size())
    print(batch_list[i].size())

for i in range(length):
    print()
    print(points_list_out[i].size())
    print(batch_list_out[i].size())












