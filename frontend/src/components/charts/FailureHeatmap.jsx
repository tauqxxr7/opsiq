
export default function FailureHeatmap(){return <div className="grid grid-cols-8 gap-2">{Array.from({length:32},(_,i)=><span key={i} className="aspect-square rounded" style={{background:"rgba(239,68,68,"+(.12+(i%5)*.15)+")"}}/>)}</div>}
