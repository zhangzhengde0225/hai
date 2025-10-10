


python drsai_as_llm_worker.py \
    --port 0 \
    --controller_address https://aiapi.ihep.ac.cn \
    --no_register False \
    --permissions "groups: payg, drsai;owner: zdzhang@ihep.ac.cn" \
    --debug True \
    $@

