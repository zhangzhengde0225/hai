

python zhizz_worker.py \
    --controller_address "http://localhost:42601" \
    --port 42605 \
    --no_register False \
    --permissions "groups: payg, haichat, drsai, haioverleaf, haiacademic;owner: zdzhang@ihep.ac.cn" \
    --debug False \
    $@
