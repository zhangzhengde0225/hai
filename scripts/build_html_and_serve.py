import os, sys
from pathlib import Path
here = Path(__file__).parent


def run():
    api_doc_dir = f'{here.parent}/docs/api_doc'
    cdir = os.getcwd()
    os.chdir(api_doc_dir)
    os.system('make html')
    os.chdir(cdir)

    start_server()

def start_server():
    os.system(f'python -m http.server -d {here.parent}/docs/api_doc/_build/html 8001')

if __name__ == '__main__':
    run()

