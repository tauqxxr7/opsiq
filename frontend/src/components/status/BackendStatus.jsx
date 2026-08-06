import { useEffect, useState } from "react";
import { Wifi, WifiOff } from "lucide-react";
import { health } from "../../services/api";
const labels = { checking: "Checking", connected: "Connected", degraded: "Degraded", offline: "Offline" };
export default function BackendStatus() {
  const [status, setStatus] = useState("checking");
  useEffect(() => { let active = true; const check = () => health().then((data) => active && setStatus(data.status === "operational" ? "connected" : "degraded")).catch(() => active && setStatus("offline")); check(); const timer = setInterval(check, 30000); return () => { active = false; clearInterval(timer); }; }, []);
  return <span className={`status-pill ${status}`} role="status" aria-live="polite">{status === "connected" ? <Wifi size={13} /> : <WifiOff size={13} />}<span>{labels[status]}</span></span>;
}
