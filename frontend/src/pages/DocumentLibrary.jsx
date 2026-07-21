import { useEffect, useState } from "react";
import LoadingState from "../components/ui/LoadingState";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import { EmptyState, ErrorState } from "../components/ui/StatePanel";
import UploadZone from "../components/ui/UploadZone";
import { documents, getApiErrorMessage, upload } from "../services/api";

export default function DocumentLibrary() {
  const [busy, setBusy] = useState(false); const [progress, setProgress] = useState(0); const [result, setResult] = useState(null); const [inventory, setInventory] = useState([]); const [inventoryError, setInventoryError] = useState(""); const [reload, setReload] = useState(0);
  const refresh = () => documents().then((data) => { setInventory(data.documents); setInventoryError(""); }).catch((error) => setInventoryError(getApiErrorMessage(error)));
  useEffect(() => { let active = true; documents().then((data) => { if (active) setInventory(data.documents); }).catch((error) => { if (active) setInventoryError(getApiErrorMessage(error)); }); return () => { active = false; }; }, [reload]);
  const handleFiles = async (files) => { if (!files?.[0]) return; setBusy(true); setProgress(0); setResult(null); try { const response = await upload(files[0], (event) => { if (event.total) setProgress(Math.round((event.loaded / event.total) * 100)); }); setResult(response); await refresh(); } catch (error) { setResult({ error: getApiErrorMessage(error) }); } finally { setBusy(false); } };
  return <div className="space-y-6">
    <PageHeader eyebrow="Knowledge ingestion" title="Document library" description="Add PDF or DOCX evidence to the retrieval corpus. Backend size limits apply and identical content is rejected by SHA-256." />
    <div className="grid gap-6 xl:grid-cols-[minmax(320px,.75fr)_minmax(0,1.25fr)]">
      <div className="space-y-6"><UploadZone onFiles={handleFiles} busy={busy} />{busy && <div className="mt-3"><div className="flex justify-between text-xs text-text-secondary"><span>Uploading and processing</span><span>{progress}%</span></div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-border"><div className="h-full bg-primary" style={{ width: `${progress}%` }} /></div></div>}
        {(busy || result) && <Panel title="Processing result">{busy ? <LoadingState message="Extracting and indexing document chunks..." /> : result?.error ? <ErrorState message={result.error} /> : <div className="text-sm text-secondary"><p className="font-medium">{result.document}: {result.chunks_indexed} chunks across {result.pages} page(s).</p><p className="mt-2 break-all font-mono text-xs text-muted">SHA-256 {result.content_hash}</p></div>}</Panel>}
      </div>
      <Panel title="Indexed corpus" description="Persistent ingestion manifest returned by the backend." flush>
        {inventoryError ? <div className="p-5"><ErrorState message={inventoryError} onRetry={() => setReload((value) => value + 1)} /></div> : inventory.length === 0 ? <EmptyState title="No uploaded documents" description="Upload a PDF or DOCX file to create the first indexed corpus entry." /> : <div className="overflow-x-auto"><table className="data-table w-full min-w-[700px]"><thead className="bg-card"><tr><th>Document</th><th>Type</th><th>Pages / chunks</th><th>Indexed</th><th>Hash</th></tr></thead><tbody>{inventory.map((item) => <tr key={item.content_hash}><td className="font-medium">{item.filename}</td><td className="uppercase text-text-secondary">{item.doc_type}</td><td>{item.pages} / {item.chunks}</td><td className="whitespace-nowrap text-text-secondary">{new Date(item.indexed_at).toLocaleString()}</td><td className="font-mono text-xs text-muted">{item.content_hash.slice(0, 12)}...</td></tr>)}</tbody></table></div>}
      </Panel>
    </div>
  </div>;
}