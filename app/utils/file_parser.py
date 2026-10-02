from pathlib import Path

ALLOWED={".txt",".md",".docx"}
def parse_script(filename:str,data:bytes)->str:
 ext=Path(filename).suffix.lower()
 if ext not in ALLOWED: raise ValueError("Unsupported script extension")
 if len(data)>10*1024*1024: raise ValueError("Script exceeds 10 MB")
 if ext==".docx":
  import io
  try:
   from docx import Document
  except ImportError: raise ValueError("python-docx is required for .docx uploads")
  return "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
 return data.decode("utf-8-sig")
