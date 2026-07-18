
export default function HealthTimeline(){return <div className="flex h-40 items-end gap-2">{[82,78,73,66,59,51,42,31].map((v,i)=><span key={i} className="flex-1 bg-primary" style={{height:v+"%"}}/>)}</div>}
