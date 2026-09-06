import { Bell, LogOut, Menu, Search, UserRound } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import Sidebar from "./Sidebar";

export default function AppShell() {
  const { user, signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F5F5]">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className={mobileOpen ? "fixed inset-0 z-40 bg-[#050505]/70 lg:hidden" : "hidden"} onClick={() => setMobileOpen(false)} />

        <aside className={mobileOpen ? "fixed inset-y-0 left-0 z-50 w-72 border-r border-[#202020] bg-[#0A0A0A] p-3 lg:hidden" : "hidden"}>
          <div className="space-y-1 pt-4">
            {[
              ["/app", "Overview"],
              ["/app/agents", "AI Employees"],
              ["/app/workflows", "Workflows"],
              ["/app/tasks", "Tasks"],
              ["/app/knowledge", "Knowledge"],
              ["/app/integrations", "Integrations"],
              ["/app/activity", "Activity"],
              ["/app/approvals", "Approvals"],
              ["/app/analytics", "Analytics"],
              ["/app/settings", "Settings"],
            ].map(([to, label]) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `block rounded-xl px-3 py-3 text-sm ${
                    isActive ? "bg-white text-black" : "text-[#D8D8D8] hover:bg-[#111111]"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </div>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-[#202020] bg-[#050505]/90 backdrop-blur-sm">
            <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className="inline-flex rounded-xl border border-[#2A2A2A] p-2 text-[#D8D8D8] lg:hidden"
                  onClick={() => setMobileOpen(true)}
                  aria-label="Open navigation menu"
                >
                  <Menu size={18} />
                </button>

                <div className="hidden items-center gap-3 rounded-xl border border-[#2A2A2A] bg-[#0A0A0A] px-3 py-2 text-[#8A8A85] sm:flex">
                  <Search size={15} />
                  <span className="text-xs uppercase tracking-[0.2em]">Search KARYA</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button type="button" className="rounded-xl border border-[#2A2A2A] p-2 text-[#D8D8D8]" aria-label="Notifications">
                  <Bell size={16} />
                </button>
                <div className="flex items-center gap-3 rounded-xl border border-[#2A2A2A] bg-[#0A0A0A] px-3 py-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black">
                    <UserRound size={15} />
                  </div>
                  <div className="hidden text-left sm:block">
                    <div className="text-xs uppercase tracking-[0.2em] text-[#8A8A85]">User</div>
                    <div className="text-sm text-[#F5F5F5]">{user?.email || "Authenticated"}</div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={signOut}
                  className="inline-flex items-center gap-2 rounded-xl border border-[#2A2A2A] bg-[#111111] px-3 py-2 text-xs uppercase tracking-[0.2em] text-[#D8D8D8]"
                >
                  <LogOut size={15} />
                  <span className="hidden sm:inline">Sign out</span>
                </button>
              </div>
            </div>
          </header>

          <main className="mx-auto w-full max-w-[1600px] flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
