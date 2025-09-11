


python ark_worker.py \
    --port 0 \
    --controller_address http://localhost:42601 \
    --no_register False \
    --permissions "groups: payg, haichat, drsai, haioverleaf" \
    --debug True \
    $@

