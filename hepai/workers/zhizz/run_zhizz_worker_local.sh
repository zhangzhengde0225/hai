

python zhizz_worker.py \
    --controller_address "http://localhost:42601" \
    --port 0 \
    --no_register False \
    --permissions "groups: payg, haichat, drsai, haioverleaf, haiacademic;owner: zdzhang" \
    --debug True \
    $@
