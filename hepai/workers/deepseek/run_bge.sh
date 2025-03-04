python bge_worker.py \
	--name "hepai/bge-m3:latest" \
    --port 0 \
    --auto_start_port 42650 \
    --permissions "groups: haichat,haiacademic,defualt,payg" \
    --num_workers 1 \
    --engine "bge-m3:latest" \
    --base_url http://10.5.6.130:11434/v1/ \
    $@
