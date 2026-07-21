import { useEffect, useState } from "react";

import LoadingState from "../components/ui/LoadingState";
import UploadZone from "../components/ui/UploadZone";
import { documents, getApiErrorMessage, upload } from "../services/api";

export default function DocumentLibrary() {
  const [busy,setBusy]=useState(false); const [result,setResult]=useState(null); const [inventory,setInventory]=useState([]); const [inventoryError,setInventoryError]=useState("");
  const refresh=()=>documents().then((data)=>{setInventory(data.documents);setInventoryError("")}).catch((error)=>setInventoryError(getApiErrorMessage(error)));
  useEffect(()=>{let active=true;documents().then((data)=>{if(active)setInventory(data.documents)}).catch((error)=>{if(active)setInventoryError(getApiErrorMessage(error))});return()=>{active=false}},[]);
  const handleFiles=async(files)=>{if(!files?.[0])return;setBusy(true);setResult(null);try{const response=await upload(files[0]);setResult(response);await refresh()}catch(error){setResult({error:getApiErrorMessage(error)})}finally{setBusy(false)}};
  return <div className="space-y-6"><div><h1 className="text-2xl font-semibold">Document Library</h1><p className="text-sm text-text-secondary">Upload PDF or DOCX evidence. The upload size limit is configured by the backend; identical content is rejected using SHA-256.</p></div><UploadZone onFiles={handleFiles} busy={busy}/>
    {(busy||result)&&<section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Processing result</h2>{busy?<LoadingState message="Extracting and indexing document chunks..."/>:<>{result?.error?<p className="mt-4 text-sm text-critical">{result.error}</p>:<div className="mt-4 text-sm text-secondary"><p>{result.document}: {result.chunks_indexed} chunks across {result.pages} page(s).</p><p className="mt-2 font-mono text-xs text-muted">SHA-256 {result.content_hash}</p></div>}</>}</section>}
    <section className="overflow-hidden rounded-xl border border-border bg-surface"><div className="border-b border-border p-5"><h2 className="font-semibold">Indexed corpus</h2><p className="text-xs text-text-secondary">Persistent ingestion manifest returned by the backend.</p></div>{inventoryError?<p className="p-5 text-sm text-critical">{inventoryError}</p>:inventory.length===0?<p className="p-5 text-sm text-text-secondary">No uploaded documents are currently registered.</p>:<div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm"><thead className="bg-card text-xs uppercase text-muted"><tr><th className="p-4">Document</th><th>Type</th><th>Pages / chunks</th><th>Indexed</th><th>Hash</th></tr></thead><tbody>{inventory.map((item)=><tr className="border-t border-border" key={item.content_hash}><td className="p-4">{item.filename}</td><td>{item.doc_type}</td><td>{item.pages} / {item.chunks}</td><td className="text-text-secondary">{new Date(item.indexed_at).toLocaleString()}</td><td className="font-mono text-xs text-muted">{item.content_hash.slice(0,12)}…</td></tr>)}</tbody></table></div>}</section>
  </div>;
}
