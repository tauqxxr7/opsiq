import { useState } from "react";

import LoadingState from "../components/ui/LoadingState";
import UploadZone from "../components/ui/UploadZone";
import { getApiErrorMessage, upload } from "../services/api";

const corpus = [
  ["OISD-118-Process-Design.pdf", "Safety Standard", "187 pages"],
  ["Maintenance_Work_Orders_2024.json", "Maintenance Record", "50 records"],
  ["Tank_Farm_Inspection_Jan_2026.pdf", "Inspection Report", "24 pages"],
];

export default function DocumentLibrary() {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  const handleFiles = async (files) => {
    if (!files?.[0]) return;
    setBusy(true);
    setResult(null);
    try {
      setResult(await upload(files[0]));
    } catch (error) {
      setResult({ error: getApiErrorMessage(error) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold">Document Library</h1><p className="text-sm text-text-secondary">Upload PDFs, Word documents, or JSON records. Chunks are semantically indexed and immediately queryable.</p></div>
      <UploadZone onFiles={handleFiles} busy={busy} />
      {(busy || result) && <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Processing pipeline</h2>{busy ? <LoadingState message="Indexing document chunks..." /> : <><div className="mt-5 grid gap-3 sm:grid-cols-5">{["Uploading", "Extracting", "Chunking", "Embedding", "Indexed"].map((step) => <div className={`rounded-lg border p-3 text-center text-xs ${result && !result.error ? "border-secondary/30 bg-secondary/5 text-secondary" : "border-border text-muted"}`} key={step}>{step}</div>)}</div>{result?.error ? <p className="mt-4 text-sm text-critical">{result.error}</p> : <p className="mt-4 text-sm text-secondary">{result.document}: {result.chunks_indexed} grounded chunks indexed successfully.</p>}</>}</section>}
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Indexed corpus</h2><div className="mt-4 divide-y divide-border">{corpus.map(([name, type, size]) => <div className="grid gap-2 py-4 text-sm sm:grid-cols-3" key={name}><span>{name}</span><span className="text-text-secondary">{type}</span><span className="text-text-secondary sm:text-right">{size}</span></div>)}</div></section>
    </div>
  );
}
