


python aliyun_worker.py \
    --port 0 \
    --controller_address https://aiapi.ihep.ac.cn \
    --no_register False \
    --permissions "groups: payg, haichat, drsai, haioverleaf" \
    --debug True \
    $@

