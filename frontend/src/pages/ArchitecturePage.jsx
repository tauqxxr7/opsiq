import { useState } from "react";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";

const nodes = [
  ["user", "Operator", 35, 35, "#08708f", "Operational users access the seven-page React interface on desktop or mobile."],
  ["react", "React frontend", 220, 35, "#147a5b", "React 18, Vite, Tailwind CSS, bounded API requests, and explicit no-data states."],
  ["api", "FastAPI", 415, 35, "#a96300", "REST routes expose health, document, maintenance, compliance, pattern, and query capabilities."],
  ["graph", "LangGraph router", 415, 145, "#6750a4", "A StateGraph classifies supported queries and routes them to the relevant specialist workflow."],
  ["copilot", "Expert copilot", 90, 275, "#08708f", "Hybrid retrieval and reranking precede Gemini synthesis. Generation occurs only when evidence is available."],
  ["maint", "Maintenance", 285, 275, "#147a5b", "Deterministic historical recurrence-risk analysis from synthetic work-order evidence; not failure prediction."],
  ["compliance", "Compliance", 480, 275, "#a96300", "Deterministic OISD-118 prototype evidence-gap assessment from synthetic inspection records."],
  ["pattern", "Pattern engine", 675, 275, "#bd3038", "NetworkX correlations across work orders and recovered incident records; associations are not causal proof."],
  ["index", "ChromaDB + BM25", 185, 405, "#526176", "Dense and sparse retrieval indexes support evidence discovery and citation packaging."],
  ["gemini", "Gemini synthesis", 575, 405, "#526176", "Optional context-only answer synthesis for the expert copilot when credentials and evidence are present."],
];
const edges = [["user", "react"], ["react", "api"], ["api", "graph"], ["graph", "copilot"], ["graph", "maint"], ["graph", "compliance"], ["graph", "pattern"], ["copilot", "index"], ["maint", "index"], ["copilot", "gemini"]];

export default function ArchitecturePage() {
  const [selected, setSelected] = useState("graph"); const current = nodes.find((node) => node[0] === selected);
  return <div className="space-y-6">
    <PageHeader eyebrow="Technical reference" title="System architecture" description="Traceable specialist workflows combining deterministic industrial analytics with evidence-grounded retrieval." />
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
      <Panel title="Request and evidence flow" description="Select a component to inspect its implemented responsibility.">
        <div className="overflow-x-auto"><svg viewBox="0 0 850 470" className="min-w-[760px]" role="img" aria-label="OPSIQ request and evidence architecture">{edges.map(([fromId, toId]) => { const from = nodes.find((node) => node[0] === fromId); const to = nodes.find((node) => node[0] === toId); return <line key={fromId + toId} x1={from[2] + 65} y1={from[3] + 18} x2={to[2] + 65} y2={to[3] + 18} stroke="#aab4c0" strokeWidth="1.5" />; })}{nodes.map((node) => <g key={node[0]} role="button" tabIndex="0" aria-label={`Inspect ${node[1]}`} className="cursor-pointer outline-none" onClick={() => setSelected(node[0])} onKeyDown={(event) => (event.key === "Enter" || event.key === " ") && setSelected(node[0])}><rect x={node[2]} y={node[3]} width="130" height="38" rx="5" fill={selected === node[0] ? node[4] : "#ffffff"} stroke={node[4]} strokeWidth={selected === node[0] ? "2" : "1.2"} /><text x={node[2] + 65} y={node[3] + 23} textAnchor="middle" fill={selected === node[0] ? "#ffffff" : "#172033"} fontSize="10" fontWeight="600">{node[1]}</text></g>)}</svg></div>
      </Panel>
      <Panel title={current[1]} description="Implemented responsibility"><span className="block h-1 w-12 rounded" style={{ background: current[4] }} /><p className="mt-5 text-sm leading-6 text-text-secondary">{current[5]}</p></Panel>
    </div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{[["Frontend", "React 18 · Vite · Tailwind"], ["Backend", "FastAPI · Python 3.11"], ["Orchestration", "LangGraph · specialist workflows"], ["Evidence", "ChromaDB · BM25 · NetworkX"]].map(([label, value]) => <div className="border-t-2 border-primary bg-surface p-4 shadow-panel" key={label}><p className="text-xs font-semibold uppercase tracking-wider text-muted">{label}</p><p className="mt-2 font-mono text-xs text-text-primary">{value}</p></div>)}</div>
  </div>;
}