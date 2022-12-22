
try:
    import hai
except Exception as e:
    import os, sys
    from pathlib import Path
    workdir = os.getcwd()
    hai_dir = f'{Path(workdir).parent}/hai'
    if hai_dir not in sys.path:
        sys.path.append(hai_dir)
    import hai
    