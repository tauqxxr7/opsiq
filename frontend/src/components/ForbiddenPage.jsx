import { ArrowLeft, ShieldX } from "lucide-react";
import { Link } from "react-router-dom";

export default function ForbiddenPage({ role }) {
  return <main className="grid min-h-[calc(100vh-4rem)] place-items-center p-6"><section className="w-full max-w-lg rounded-2xl border border-critical/30 bg-surface p-8 text-center shadow-panel"><span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl border border-critical/30 bg-critical/10 text-critical"><ShieldX size={26} /></span><p className="section-label mt-5">HTTP 403</p><h1 className="mt-2 text-2xl font-semibold">Access restricted</h1><p className="mt-3 text-sm leading-6 text-text-secondary">Your {role} role is authenticated but is not authorized to open this workspace. Contact an OPSIQ administrator if your operational responsibilities require access.</p><Link to="/dashboard" className="secondary-button mt-6 inline-flex"><ArrowLeft size={16} />Return to overview</Link></section></main>;
}