import re
from pathlib import Path
import fitz
from docx import Document
class DocumentProcessor:
    def process(self, file_path, doc_type=None):
        path = Path(file_path)
        if path.suffix.lower() == ".pdf":
            with fitz.open(path) as doc:
                return [c for page, p in enumerate(doc, 1) for c in self._chunks(p.get_text("text"), path, page, doc_type)]
        if path.suffix.lower() == ".docx":
            doc = Document(path)
            return self._chunks("\n".join(p.text for p in doc.paragraphs), path, 1, doc_type)
        raise ValueError(f"Unsupported file type: {path.suffix}")
    def _chunks(self, text, path, page, doc_type):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip()); groups=[]; current=[]; size=0
        for sentence in sentences:
            length=len(sentence.split())
            if current and size+length>400:
                groups.append(" ".join(current)); current=current[-2:]; size=sum(len(x.split()) for x in current)
            current.append(sentence); size+=length
        if current: groups.append(" ".join(current))
        section=next((x.strip() for x in text.splitlines()[:8] if x.strip() and len(x)<100 and (x.strip().isupper() or re.match(r"^\d+",x))),"General")
        return [{"text":x,"doc_name":path.name,"page":page,"section":section,"doc_type":doc_type or self._type(path.name),"chunk_id":f"{path.stem}_p{page}_c{i}"} for i,x in enumerate(groups) if len(x)>=50]
    def _type(self, name):
        value=name.lower()
        if "oisd" in value or "standard" in value:return "Safety Standard"
        if "work" in value:return "Maintenance Record"
        if "inspection" in value:return "Inspection Report"
        if "procedure" in value:return "Operating Procedure"
        if "incident" in value:return "Incident Report"
        return "General Document"
