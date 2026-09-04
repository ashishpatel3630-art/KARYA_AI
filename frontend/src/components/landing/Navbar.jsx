import { Bell, Search, ShieldCheck, User } from "lucide-react";

const Navbar = () => {
  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-[#2A2A2A] bg-[#050505] px-6">
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-sm font-medium text-[#F5F5F5]">AI Workbench</h1>

          <p className="text-[10px] text-[#8A8A85]">Sovereign Industrial AI</p>
        </div>
      </div>

      <div className="flex items-center gap-5">
        <div className="hidden items-center gap-2 rounded-md border border-[#2A2A2A] px-3 py-1.5 sm:flex">
          <ShieldCheck size={14} className="text-[#F5F5F5]" />

          <span className="text-[10px] uppercase tracking-wider text-[#8A8A85]">
            On-Premise
          </span>
        </div>

        <button
          className="text-[#8A8A85] transition-colors hover:text-[#F5F5F5]"
          aria-label="Search"
        >
          <Search size={18} strokeWidth={1.7} />
        </button>

        <button
          className="relative text-[#8A8A85] transition-colors hover:text-[#F5F5F5]"
          aria-label="Notifications"
        >
          <Bell size={18} strokeWidth={1.7} />

          <span className="absolute -right-1 -top-1 h-1.5 w-1.5 rounded-full bg-[#F5F5F5]" />
        </button>

        <div className="h-6 w-px bg-[#2A2A2A]" />

        <button className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[#2A2A2A] bg-[#111111]">
            <User size={15} className="text-[#8A8A85]" />
          </div>

          <div className="hidden text-left md:block">
            <p className="text-xs font-medium text-[#F5F5F5]">Engineer</p>

            <p className="text-[10px] text-[#8A8A85]">Administrator</p>
          </div>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
