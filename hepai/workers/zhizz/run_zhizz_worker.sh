

python zhizz_worker.py \
    --controller_address "https://aiapi.ihep.ac.cn" \
    --no_register False \
    --permissions "groups: payg, haichat, drsai, haioverleaf, haiacademic, hairongzai@ihep.ac.cn, haik8s;owner: zdzhang@ihep.ac.cn" \
    --debug True \
    $@



# python zhizz_worker.py \
#     --controller_address "http://localhost:42601" \
#     --port 0 \
#     --no_register False \
#     --permissions "groups: haichat, payg, drsai" \
#     --debug True \
#     $@
