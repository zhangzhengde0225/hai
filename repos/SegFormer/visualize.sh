#!/usr/bin/env bash

#python demo/image_demo.py \
#  ${IMAGE_FILE} ${CONFIG_FILE} ${CHECKPOINT_FILE} \
#  [--device ${DEVICE_NAME}] [--palette-thr ${PALETTE}]

python demo/image_demo.py \
  demo/demo.png \
  local_configs/segformer/B1/segformer.b1.1024x1024.city.160k.py \
  /home/zzd/weights/segformer/segformer.b1.1024x1024.city.160k.pth \
  --device cuda:0 \
  --palette cityscapes
