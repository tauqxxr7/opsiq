import { FileText } from "lucide-react";
export default function CitationChip({ citation, index, onClick }) {
  return <button onClick={onClick} className="mr-2 mt-2 inline-flex max-w-full items-center gap-2 rounded border border-border bg-surface px-3 py-2 text-left text-xs text-text-secondary hover:border-primary hover:text-primary"><FileText size={13} /><span className="truncate">[{index}] {citation.doc_name} · p.{citation.page}</span></button>;
}