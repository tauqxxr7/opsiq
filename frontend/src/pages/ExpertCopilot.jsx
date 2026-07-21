import { FileText, Send } from "lucide-react";
import { useEffect, useState } from "react";
import CitationChip from "../components/ui/CitationChip";
import ConfidenceBar from "../components/ui/ConfidenceBar";
import LoadingState from "../components/ui/LoadingState";
import PageHeader from "../components/ui/PageHeader";
import { ask, documentStats, getApiErrorMessage } from "../services/api";

const suggestions = ["What recurring failures affect P-201?", "What evidence gaps exist for OISD-118?", "Which assets have the highest recurrence risk?", "Summarize the strongest cross-source failure pattern."];

const initialMessage = { role: "assistant", content: "Ask about an indexed procedure, safety standard, equipment history, or work order. Responses are generated only when supporting evidence is retrieved.", citations: [], confidence: null };

export default function ExpertCopilot() {
  const [messages, setMessages] = useState([initialMessage]); const [input, setInput] = useState(""); const [loading, setLoading] = useState(false); const [active, setActive] = useState(null); const [noDocuments, setNoDocuments] = useState(false);
  useEffect(() => { let ignore = false; documentStats().then((data) => { if (!ignore) setNoDocuments(data.chunks === 0); }).catch(() => {}); return () => { ignore = true; }; }, []);
  const send = async () => {
    if (!input.trim() || loading) return;
    const query = input.trim(); setInput(""); setMessages((current) => [...current, { role: "user", content: query }]); setLoading(true);
    try { const data = await ask({ query }); setMessages((current) => [...current, { role: "assistant", content: data.answer, citations: data.citations || [], confidence: data.confidence }]); }
    catch (error) { setMessages((current) => [...current, { role: "assistant", content: getApiErrorMessage(error), citations: [], confidence: 0 }]); }
    finally { setLoading(false); }
  };
  return <div className="space-y-6">
    <PageHeader eyebrow="Evidence-grounded assistance" title="Expert knowledge copilot" description="Natural-language retrieval over indexed documents, with source passages and confidence attached to each supported answer." />
    <div className="grid min-h-[650px] gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
      <section className="flex min-h-[650px] flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-panel">
        <div className="border-b border-border px-5 py-3"><p className="text-xs text-text-secondary">No retrieved evidence means no generated answer.</p></div>
        <div className="scrollbar-thin flex-1 space-y-6 overflow-y-auto p-5 sm:p-6">
          {noDocuments && <div className="border-l-2 border-warning bg-warning/5 px-4 py-3 text-sm text-text-secondary">No documents are indexed. Add evidence in the Document Library before asking corpus-specific questions.</div>}
          {messages.length === 1 && <div><p className="text-xs font-medium text-text-secondary">Supported starting points</p><div className="mt-2 flex flex-wrap gap-2">{suggestions.map((question) => <button key={question} onClick={() => setInput(question)} className="rounded-md border border-border bg-surface px-3 py-2 text-left text-xs text-text-secondary hover:border-primary hover:text-primary">{question}</button>)}</div></div>}
          {messages.map((message, index) => <article key={`${message.role}-${index}`} className={message.role === "user" ? "ml-auto max-w-2xl" : "max-w-3xl"}>
            <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">{message.role === "user" ? "Operator question" : "OPSIQ evidence response"}</p>
            <div className={`rounded-lg px-4 py-3 text-sm leading-6 ${message.role === "user" ? "bg-sidebar text-white" : "border border-border bg-card text-text-primary"}`}>{message.content}</div>
            {message.confidence != null && <div className="mt-3 max-w-md"><ConfidenceBar score={message.confidence} /></div>}
            {message.citations?.map((citation, citationIndex) => <CitationChip key={`${citation.doc_name}-${citation.page}-${citationIndex}`} citation={citation} index={citationIndex + 1} onClick={() => setActive(citation)} />)}
          </article>)}
          {loading && <LoadingState message="Retrieving from the knowledge base..." />}
        </div>
        <div className="border-t border-border bg-card p-4"><div className="flex gap-2"><label className="sr-only" htmlFor="copilot-input">Ask an operational question</label><input id="copilot-input" className="min-w-0 flex-1 rounded-md border border-border bg-surface px-4 py-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === "Enter" && send()} placeholder="Ask an evidence-grounded operational question..." /><button onClick={send} disabled={loading || !input.trim()} className="rounded-md bg-primary px-4 text-white hover:bg-primary/90 disabled:opacity-40" aria-label="Send question"><Send size={18} /></button></div></div>
      </section>
      <aside className="rounded-lg border border-border bg-surface p-5 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted">Source inspector</p>
        {active ? <div className="mt-6 space-y-4"><FileText className="text-primary" size={22} /><div><p className="text-sm font-semibold">{active.doc_name}</p><p className="mt-1 font-mono text-xs text-text-secondary">Page {active.page}  /  {active.section}</p></div><blockquote className="border-l-2 border-primary bg-card p-3 text-xs leading-5 text-text-secondary">{active.excerpt}</blockquote><ConfidenceBar score={active.relevance_score} /></div> : <p className="mt-5 text-sm leading-6 text-text-secondary">Select a citation beneath a response to inspect the retrieved source passage and relevance score.</p>}
      </aside>
    </div>
  </div>;
}