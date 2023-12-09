import base64
from pathlib import Path

def pdf_process(data):
    pdf_path = Path(data.pop('pdf_path', None))
    pdf_path = pdf_path.resolve()
    if not pdf_path.exists():
        raise ValueError("PDF路径为空.请使用pdf_path参数来提供有效的PDF路径。")
    else:
        with open(pdf_path, 'rb') as pdf_file:
            pdfbin = pdf_file.read()          
        pdfbin= base64.b64encode(pdfbin).decode()
    data['pdfbin'] = pdfbin
    return data