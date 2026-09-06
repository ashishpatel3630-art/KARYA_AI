import { useState } from "react";
import { Menu, X } from "lucide-react";

function Navbar({ onRegister, onLogin }) {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-[#1A1A1A] bg-[#050505]/95 backdrop-blur">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">
        
        <a href="#top" className="text-xl font-bold tracking-[0.25em] text-white">
          KARYA
        </a>

        <div className="hidden items-center gap-8 md:flex">
          <a href="#solution" className="text-xs uppercase tracking-widest text-[#8A8A85] hover:text-white">
            Solution
          </a>
          <a href="#features" className="text-xs uppercase tracking-widest text-[#8A8A85] hover:text-white">
            Capabilities
          </a>
          <a href="#security" className="text-xs uppercase tracking-widest text-[#8A8A85] hover:text-white">
            Security
          </a>
          <a href="#use-cases" className="text-xs uppercase tracking-widest text-[#8A8A85] hover:text-white">
            Use Cases
          </a>
        </div>

        <button
          onClick={onRegister}
          className="hidden border border-[#2A2A2A] bg-white px-5 py-2.5 text-xs font-semibold uppercase tracking-widest text-black transition hover:bg-[#D8D8D8] md:block"
        >
          Register
        </button>
        <button
          onClick={onLogin}
          className="hidden border border-[#2A2A2A] bg-white px-5 py-2.5 text-xs font-semibold uppercase tracking-widest text-black transition hover:bg-[#D8D8D8] md:block"
        >
          Login 
        </button>

        <button
          onClick={() => setOpen(!open)}
          className="text-white md:hidden"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-[#1A1A1A] bg-[#050505] px-6 py-6 md:hidden">
          <div className="flex flex-col gap-6">
            <a href="#solution" onClick={() => setOpen(false)} className="text-xs uppercase tracking-widest text-[#8A8A85]">
              Solution
            </a>
            <a href="#features" onClick={() => setOpen(false)} className="text-xs uppercase tracking-widest text-[#8A8A85]">
              Capabilities
            </a>
            <a href="#security" onClick={() => setOpen(false)} className="text-xs uppercase tracking-widest text-[#8A8A85]">
              Security
            </a>
            <a href="#use-cases" onClick={() => setOpen(false)} className="text-xs uppercase tracking-widest text-[#8A8A85]">
              Use Cases
            </a>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;