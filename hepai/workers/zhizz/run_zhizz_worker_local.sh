

python zhizz_worker.py \
    --controller_address "http://localhost:42601" \
    --port 0 \
    --no_register False \
    --permissions "groups: haichat, payg, drsai" \
    --debug True \
    $@
