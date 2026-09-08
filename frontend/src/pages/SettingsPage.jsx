import { Check, LockKeyhole, UserRound } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import { useAuth } from "../context/AuthContext";
import { useOperations } from "../context/OperationsContext";

export default function SettingsPage() {
  const { user } = useAuth();
  const { systemStatus } = useOperations();
  const [notifications, setNotifications] = useState(true);
  const [saved, setSaved] = useState(false);

  function savePreferences(event) {
    event.preventDefault();
    localStorage.setItem("karya_preferences", JSON.stringify({ notifications }));
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  }

  return <div><PageHeader eyebrow="Control" title="Settings" description="Manage the local workspace experience while account and security changes remain governed by the existing API." />
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <form onSubmit={savePreferences} className="border border-[#202020] bg-[#0A0A0A] p-6 sm:p-8"><div className="flex items-center gap-3"><UserRound size={18} /><h2 className="text-xs uppercase tracking-[0.18em]">Profile and preferences</h2></div><div className="mt-8 grid gap-5 sm:grid-cols-2"><label className="block text-xs uppercase tracking-[0.16em] text-[#777772]">Email<input readOnly value={user?.email || "Authenticated session"} className="mt-3 w-full border border-[#2A2A2A] bg-[#111111] px-4 py-3 text-sm text-[#C8C8C3]" /></label><label className="block text-xs uppercase tracking-[0.16em] text-[#777772]">Role<input readOnly value={user?.role || "Workspace operator"} className="mt-3 w-full border border-[#2A2A2A] bg-[#111111] px-4 py-3 text-sm text-[#C8C8C3]" /></label></div><label className="mt-8 flex cursor-pointer items-center justify-between border-t border-[#202020] pt-5 text-sm text-[#D8D8D8]"><span><span className="block">System notifications</span><span className="mt-1 block text-xs text-[#777772]">Show task, workflow, integration, and approval events.</span></span><input type="checkbox" checked={notifications} onChange={(event) => setNotifications(event.target.checked)} className="h-4 w-4 accent-white" /></label><button className="mt-8 inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.16em] text-black">{saved ? <Check size={14} /> : null}{saved ? "Saved" : "Save preferences"}</button></form>
      <section className="border border-[#202020] bg-[#0A0A0A] p-6 sm:p-8"><div className="flex items-center gap-3"><LockKeyhole size={18} /><h2 className="text-xs uppercase tracking-[0.18em]">Session and security</h2></div><div className="mt-8 space-y-5 border-y border-[#202020] py-5 text-sm"><div className="flex justify-between gap-4"><span className="text-[#777772]">Session</span><span className="text-[#C8C8C3]">{systemStatus.secureSession ? "SECURE" : "ATTENTION"}</span></div><div className="flex justify-between gap-4"><span className="text-[#777772]">AI runtime</span><span className="text-[#C8C8C3]">{systemStatus.aiCore}</span></div></div><p className="mt-6 text-sm leading-6 text-[#777772]">Password, MFA, token rotation, and session revocation use the backend authentication contract.</p><Link to="/login" className="mt-6 inline-flex border border-[#2A2A2A] px-4 py-3 text-xs uppercase tracking-[0.16em] text-[#D8D8D8] hover:border-white">Review authentication</Link></section>
    </div>
  </div>;
}
