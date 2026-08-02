import { useEffect, useRef, useState } from "react";
export function AnimatedNumber({ value, suffix = "" }) {
  const numeric = Number(value), previous = useRef(numeric), [shown, setShown] = useState(numeric);
  useEffect(() => { if (!Number.isFinite(numeric) || matchMedia("(prefers-reduced-motion: reduce)").matches) { setShown(numeric); return; } const start = previous.current, began = performance.now(); let frame; const tick = (now) => { const progress = Math.min((now - began) / 320, 1); setShown(start + (numeric - start) * (1 - (1 - progress) ** 3)); if (progress < 1) frame = requestAnimationFrame(tick); else previous.current = numeric; }; frame = requestAnimationFrame(tick); return () => cancelAnimationFrame(frame); }, [numeric]);
  return <span>{Number.isFinite(shown) ? (Number.isInteger(numeric) ? Math.round(shown) : shown.toFixed(1)) : value}{suffix}</span>;
}
export function DisclosurePanel({ title, children, defaultOpen = false }) { const [open, setOpen] = useState(defaultOpen); return <section className="rounded-xl border border-border/70 bg-card/35"><button type="button" className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium" aria-expanded={open} onClick={() => setOpen((value) => !value)}><span>{title}</span><span aria-hidden="true" className={`transition-transform ${open ? "rotate-45" : ""}`}>+</span></button>{open ? <div className="motion-reveal border-t border-border/60 p-4">{children}</div> : null}</section>; }
export function PageTransition({ children }) { return <div className="page-transition">{children}</div>; }
