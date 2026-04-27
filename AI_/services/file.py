import os
from pathlib import Path


def read_uploaded_file(uploaded_file):
    """
    读取上传的文件内容，返回文本字符串。
    支持格式: .txt, .md, .pdf, .csv, .docx
    """
    if uploaded_file is None:
        return None

    filename = uploaded_file.name
    ext = Path(filename).suffix.lower()

    try:
        if ext in ('.txt', '.md', '.py', '.json', '.yaml', '.yml', '.xml', '.html', '.css', '.js'):
            return uploaded_file.read().decode('utf-8')

        elif ext == '.csv':
            content = uploaded_file.read().decode('utf-8')
            return content

        elif ext == '.pdf':
            return _read_pdf(uploaded_file)

        elif ext == '.docx':
            return _read_docx(uploaded_file)

        else:
            return f"【不支持的文件格式：{ext}，目前支持 txt/md/pdf/csv/docx】"
    except Exception as e:
        return f"【读取文件失败：{str(e)}】"


def _read_pdf(uploaded_file):
    # pdfplumber — 中文支持较好，优先使用
    try:
        import pdfplumber
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        os.unlink(tmp_path)
        if text.strip():
            return text.strip()
    except ImportError:
        pass

    # pypdf — 后备方案
    try:
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        if text.strip():
            return text.strip()
    except ImportError:
        pass

    # PyPDF2 — 最后尝试
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        if text.strip():
            return text.strip()
    except ImportError:
        pass

    return "【读取PDF需要安装 pdfplumber 库：pip install pdfplumber】"


def _read_docx(uploaded_file):
    try:
        from docx import Document
        doc = Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return text.strip() or "【Word文件无可用文本内容】"
    except ImportError:
        return "【读取Word文件需要安装 python-docx 库：pip install python-docx】"
