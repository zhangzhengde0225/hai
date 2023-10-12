python run_worker.py \
 --name hepai/demo_worker_in_hai \
 --controller_address http://aiapi.ihep.ac.cn:42901 \
 --limit_model_concurrency 10 \
 --permissions "groups: all"  # 自行修改