python dpsk_worker.py \
	--name "hepai/bge-reranker-v2-m3" \
	--engine "linux6200/beg-reranker-v2-m3:latest" \
    --port 0 \
    --auto_start_port 42650 \
    --permissions "groups: haichat,haiacademic,defualt,payg" \
    --num_workers 1 \
    --base_url http://10.5.6.130:11434/v1 \
    $@
