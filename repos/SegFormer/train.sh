#!/usr/bin/env bash

# 官方训练实例
# Single-gpu training
python tools/train.py \
    local_configs/segformer/B1/segformer.b1.512x512.ade.160k.py

# Multi-gpu training
# ./tools/dist_train.sh \
#     local_configs/segformer/B1/segformer.b1.512x512.ade.160k.py <GPU_NUM>