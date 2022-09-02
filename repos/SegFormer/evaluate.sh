#!/usr/bin/env bash

# 官方性能评估命令https://github.com/NVlabs/SegFormer

# Single-gpu testing
python tools/test.py \
  local_configs/segformer/B1/segformer.b1.1024x1024.city.160k.py \
  /home/zzd/weights/segformer/segformer.b1.1024x1024.city.160k.pth

# Multi-gpu testing
#./tools/dist_test.sh \
#  local_configs/segformer/B1/segformer.b1.512x512.ade.160k.py \
#  /path/to/checkpoint_file <GPU_NUM>

# Multi-gpu, multi-scale testing
#tools/dist_test.sh \
#  local_configs/segformer/B1/segformer.b1.512x512.ade.160k.py \
#  /path/to/checkpoint_file <GPU_NUM> --aug-test
