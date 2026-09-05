import { Activity, Bell, Cpu, LogOut, ShieldCheck, Workflow } from "lucide-react";

const systems = [
  { name: "Production line A", state: "Operational", value: "98.4%", tone: "text-[#77d69b]" },
  { name: "Energy monitoring", state: "Nominal", value: "42.8 MWh", tone: "text-[#77d69b]" },
  { name: "Maintenance queue", state: "3 actions", value: "Priority", tone: "text-[#f4c66d]" },
];

function Desktop() {
  function handleLogout() {
    localStorage.removeItem("karya_access_token");
    localStorage.removeItem("karya_refresh_token");
    window.location.reload();
  }

  return (
    <main className="min-h-screen bg-[#070707] text-white">
      <header className="border-b border-[#202020] bg-[#0A0A0A] px-6 py-5 lg:px-10">
        <div className="mx-auto flex max-w-350 items-center justify-between">
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold tracking-[0.25em]">KARYA</span>
            <span className="hidden border-l border-[#2A2A2A] pl-8 text-[10px] uppercase tracking-[0.2em] text-[#8A8A85] sm:block">Operations desktop</span>
          </div>
          <button onClick={handleLogout} className="flex items-center gap-2 text-xs uppercase tracking-widest text-[#8A8A85] transition hover:text-white">
            <LogOut size={15} />
            Sign out
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-350 px-6 py-10 lg:px-10">
        <div className="flex flex-col justify-between gap-5 border-b border-[#202020] pb-8 sm:flex-row sm:items-end">
          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">System // 001</p>
            <h1 className="mt-4 text-4xl font-semibold tracking-[-0.04em] sm:text-6xl">Good morning.</h1>
            <p className="mt-3 text-sm text-[#8A8A85]">Your autonomous operations layer is active.</p>
          </div>
          <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-[#77d69b]"><span className="h-2 w-2 bg-[#77d69b]" /> All systems nominal</div>
        </div>

        <section className="mt-8 grid gap-px border border-[#202020] bg-[#202020] md:grid-cols-3">
          {systems.map((system) => (
            <article key={system.name} className="bg-[#0A0A0A] p-6">
              <div className="flex items-center justify-between text-[#8A8A85]"><Activity size={18} /><span className="text-[10px] uppercase tracking-widest">Live</span></div>
              <h2 className="mt-10 text-sm text-[#D8D8D8]">{system.name}</h2>
              <p className={`mt-3 text-2xl font-medium ${system.tone}`}>{system.value}</p>
              <p className="mt-2 text-[10px] uppercase tracking-widest text-[#555550]">{system.state}</p>
            </article>
          ))}
        </section>

        <section className="mt-8 grid gap-8 lg:grid-cols-[1.4fr_1fr]">
          <article className="border border-[#202020] bg-[#0A0A0A] p-6 sm:p-8">
            <div className="flex items-center justify-between"><div className="flex items-center gap-3"><Workflow size={18} /><h2 className="text-xs uppercase tracking-widest">Active workflows</h2></div><span className="text-[10px] text-[#8A8A85]">03 running</span></div>
            <div className="mt-8 space-y-5">
              {[["Predictive maintenance", "Analyzing vibration sensors", "74%"], ["Shift coordination", "Preparing handoff report", "52%"], ["Energy optimization", "Balancing load distribution", "91%"]].map(([name, detail, progress]) => (
                <div key={name}>
                  <div className="flex justify-between text-sm"><span>{name}</span><span className="text-[#8A8A85]">{progress}</span></div>
                  <p className="mt-1 text-xs text-[#555550]">{detail}</p>
                  <div className="mt-3 h-1 bg-[#242424]"><div className="h-1 bg-white" style={{ width: progress }} /></div>
                </div>
              ))}
            </div>
          </article>

          <article className="border border-[#202020] bg-[#0A0A0A] p-6 sm:p-8">
            <div className="flex items-center gap-3"><Bell size={18} /><h2 className="text-xs uppercase tracking-widest">Intelligence feed</h2></div>
            <div className="mt-8 space-y-6 text-sm">
              <p><span className="mr-3 text-[#f43131]">09:42</span>Maintenance window recommended for Line A.</p>
              <p><span className="mr-3 text-[#8A8A85]">09:17</span>Shift report generated and filed.</p>
              <p><span className="mr-3 text-[#8A8A85]">08:54</span>Energy variance corrected automatically.</p>
            </div>
          </article>
        </section>

        <footer className="mt-10 flex items-center gap-3 text-[10px] uppercase tracking-[0.2em] text-[#555550]"><ShieldCheck size={15} /> Secure session <Cpu size={15} className="ml-4" /> AI core active</footer>
      </div>
    </main>
  );
}

export default Desktop;
