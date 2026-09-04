function Footer() {
  return (
    <footer className="bg-[#050505]">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        
        <div className="flex flex-col gap-10 md:flex-row md:items-start md:justify-between">
          
          <div>
            <p className="text-xl font-bold tracking-[0.25em] text-white">
              KARYA
            </p>

            <p className="mt-4 max-w-xs text-xs leading-6 text-[#555]">
              Confidential industrial intelligence for autonomous operations.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-x-16 gap-y-4">
            <a href="#solution" className="text-[10px] uppercase tracking-widest text-[#8A8A85] hover:text-white">
              Solution
            </a>
            <a href="#features" className="text-[10px] uppercase tracking-widest text-[#8A8A85] hover:text-white">
              Capabilities
            </a>
            <a href="#security" className="text-[10px] uppercase tracking-widest text-[#8A8A85] hover:text-white">
              Security
            </a>
            <a href="#use-cases" className="text-[10px] uppercase tracking-widest text-[#8A8A85] hover:text-white">
              Use Cases
            </a>
          </div>
        </div>

        <div className="mt-16 flex flex-col justify-between gap-4 border-t border-[#1A1A1A] pt-6 text-[10px] uppercase tracking-widest text-[#555] sm:flex-row">
          <span>© 2026 KARYA</span>
          <span>Confidential Industrial AI</span>
        </div>

      </div>
    </footer>
  );
}

export default Footer;