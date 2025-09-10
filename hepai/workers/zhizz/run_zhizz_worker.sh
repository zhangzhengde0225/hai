

python zhizz_worker.py \
    --controller_address "https://aiapi.ihep.ac.cn/apiv2" \
    --no_register False \
    --permissions "groups: haichat, payg, drsai" \
    --debug True \
    $@



# python zhizz_worker.py \
#     --controller_address "http://localhost:42601/apiv2" \
#     --no_register False \
#     --permissions "groups: haichat, payg, drsai" \
#     --debug True \
#     $@
