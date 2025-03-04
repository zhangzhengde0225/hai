python dpsk_worker.py \
	--name "hepai/deepseek-r1:671b" \
    --port 0 \
    --auto_start_port 42650 \
    --permissions "groups: haichat,haiacademic,defualt,payg" \
    --num_workers 1 \
    --engine "deepseek-r1:671b" \
    --base_url http://aidcu001.ihep.ac.cn:11434/v1 \
    $@
