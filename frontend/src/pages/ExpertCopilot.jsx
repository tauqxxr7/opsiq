import { FileText, Send } from "lucide-react";
import { useEffect, useState } from "react";
import CitationChip from "../components/ui/CitationChip";
import ConfidenceBar from "../components/ui/ConfidenceBar";
import PageHeader from "../components/ui/PageHeader";
import { ask, documentStats, getApiErrorMessage } from "../services/api";

const suggestions = ["What recurring failures affect P-201?", "What evidence gaps exist for OISD-118?", "Which assets have the highest recurrence risk?", "Summarize the strongest cross-source failure pattern."];
const initialMessage = { role: "assistant", content: "Ask about an indexed procedure, safety standard, equipment history, or work order. Responses are generated only when supporting evidence is retrieved.", citations: [], confidence: null };

export default function ExpertCopilot() {
  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState(null);
  const [collectionSize, setCollectionSize] = useState(null);
  const noDocuments = collectionSize === 0;

  useEffect(() => {
    let ignore = false;
    documentStats().then((data) => { if (!ignore) setCollectionSize(data.chunks); }).catch(() => {});
    return () => { ignore = true; };
  }, []);

  const send = async () => {
    if (!input.trim() || loading) return;
    const query = input.trim();
    setInput("");
    setLoading(true);
    setMessages((current) => [...current, { role: "user", content: query }]);
    try {
      const data = await ask({ query });
      setMessages((current) => [...current, { role: "assistant", content: data.answer, citations: data.citations || [], confidence: data.confidence }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", content: getApiErrorMessage(error), citations: [], confidence: 0 }]);
    } finally {
      setLoading(false);
    }
  };

  return <div className="page-enter page-enter-active space-y-6">
    <PageHeader eyebrow="Evidence-grounded assistance" title="Expert knowledge copilot" description="Natural-language retrieval over indexed documents, with source passages and confidence attached to each supported answer." />
    <div className="grid min-h-[650px] gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
      <section className="card-hover flex min-h-[650px] flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-panel">
        <div className="border-b border-border/70 px-5 py-3"><p className="text-xs leading-relaxed text-text-secondary">No retrieved evidence means no generated answer.</p></div>
        <div className="scrollbar-thin flex-1 space-y-6 overflow-y-auto p-5 sm:p-6">
          {noDocuments && <div className="rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm leading-relaxed text-text-secondary">No documents are indexed. Add evidence in the Document Library before asking corpus-specific questions.</div>}
          {messages.length === 1 && <div><p className="text-xs font-medium uppercase tracking-widest text-muted">Supported starting points</p><div className="mt-3 flex flex-wrap gap-2">{suggestions.map((question) => <button key={question} onClick={() => setInput(question)} className="rounded-lg border border-border bg-card px-3 py-2 text-left text-xs text-text-secondary transition-all hover:border-primary/40 hover:text-text-primary">{question}</button>)}</div></div>}
          {messages.map((message, index) => {
            const isUser = message.role === "user";
            return <article key={`${message.role}-${index}`} className={`flex items-start gap-3 ${isUser ? "ml-auto max-w-[80%] flex-row-reverse" : "max-w-[90%]"}`}>
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border font-mono text-[10px] font-bold ${isUser ? "border-primary/30 bg-primary text-white" : "border-secondary/30 bg-secondary/15 text-secondary"}`}>{isUser ? "YOU" : "OQ"}</div>
              <div className="min-w-0 flex-1">
                <p className={`mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted ${isUser ? "text-right" : ""}`}>{isUser ? "Operator question" : "OPSIQ evidence response"}</p>
                <div className={`px-4 py-3 text-sm leading-relaxed text-text-primary ${isUser ? "rounded-xl rounded-tr-sm border border-primary/25 bg-primary/15" : "rounded-xl rounded-tl-sm border border-border bg-card"}`}>{message.content}</div>
                {message.confidence != null && <div className="mt-3 max-w-md"><ConfidenceBar score={message.confidence} /></div>}
                {message.citations?.map((citation, citationIndex) => <CitationChip key={`${citation.doc_name}-${citation.page}-${citationIndex}`} citation={citation} index={citationIndex + 1} onClick={() => setActive(citation)} />)}
              </div>
            </article>;
          })}
          {loading && <div className="flex max-w-[90%] items-start gap-3" role="status" aria-live="polite"><span className="sr-only">Retrieving from the knowledge base...</span><div className="skeleton h-8 w-8 shrink-0 rounded-full" /><div className="flex-1 space-y-2"><div className="skeleton h-3 w-32" /><div className="skeleton h-20 w-full rounded-xl" /></div></div>}
        </div>
        <div className="border-t border-border/70 bg-card/50 p-4">
          <div className="flex gap-2">
            <label className="sr-only" htmlFor="copilot-input">Ask an operational question</label>
            <input id="copilot-input" className="min-w-0 flex-1 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-text-primary outline-none transition-colors placeholder:text-muted focus:border-primary focus:ring-1 focus:ring-primary" value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === "Enter" && send()} placeholder="Ask an evidence-grounded operational question..." />
            <button onClick={send} disabled={loading || !input.trim()} className="flex min-w-12 items-center justify-center rounded-lg bg-primary px-4 text-white transition-colors hover:bg-primary/90 disabled:opacity-40" aria-label="Send question">{loading ? <span className="skeleton h-4 w-4 rounded-full" /> : <Send size={18} />}</button>
          </div>
          <p className="mt-2 font-mono text-xs text-muted">Retrieves from indexed documents only. All answers include source citations.{noDocuments && <span className="ml-2 text-warning">No documents indexed — upload files in Document Library</span>}</p>
        </div>
      </section>
      <aside className="card-hover rounded-xl border border-border bg-surface p-5 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted">Source inspector</p>
        {active ? <div className="mt-6 space-y-4"><div className="flex h-10 w-10 items-center justify-center rounded-xl border border-primary/20 bg-primary/10"><FileText className="text-primary" size={19} /></div><div><p className="text-sm font-semibold">{active.doc_name}</p><p className="mt-1 font-mono text-xs text-text-secondary">Page {active.page} / {active.section}</p></div><blockquote className="rounded-r-lg border-l-2 border-primary bg-card p-3 text-xs leading-relaxed text-text-secondary">{active.excerpt}</blockquote><ConfidenceBar score={active.relevance_score} /></div> : <p className="mt-5 text-sm leading-relaxed text-text-secondary">Select a citation beneath a response to inspect the retrieved source passage and relevance score.</p>}
      </aside>
    </div>
  </div>;
}