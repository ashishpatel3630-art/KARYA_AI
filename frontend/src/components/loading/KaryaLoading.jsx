import { useEffect, useState } from "react";

const KaryaLoader = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          onComplete?.();
          return 100;
        }

        return prev + 1;
      });
    }, 25);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 flex min-h-screen items-center justify-center bg-[#050505] text-white">
      <div className="w-[360px]">
       
        <div className="mb-3 text-center">
          <h1 className="animate-pulse text-5xl font-semibold tracking-[0.35em]">
            KARYA
          </h1>
        </div>

   
        <p className="mb-10 text-center text-[10px] uppercase tracking-[0.35em] text-[#8A8A85]">
          Sovereign Industrial AI
        </p>

        
        <div className="h-[4px] w-full overflow-hidden bg-[#1A1A1A]">
          <div
            className="h-full bg-[#f43131] transition-all duration-100 ease-linear"
            style={{ width: `${progress}%` }}
          />
        </div>

       
        <div className="mt-4 flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-[0.2em] text-[#8A8A85]">
            Initializing System
          </span>

          <span className="font-mono text-xs text-[#F5F5F5]">{progress}%</span>
        </div>

        
        <div className="mt-8 space-y-2 font-mono text-[10px] text-[#555]">
          <p>
            <span className="text-[#F5F5F5]">✓</span> Secure environment
          </p>

          <p>
            <span className="text-[#F5F5F5]">✓</span> Local AI engine
          </p>

          <p>
            <span className="text-[#F5F5F5]">✓</span> Knowledge system
          </p>

          <p>
            <span className="text-[#F5F5F5]">✓</span> Workbench
          </p>
        </div>
      </div>

     
      <div className="absolute bottom-6 text-[9px] uppercase tracking-[0.25em] text-[#444]">
        KARYA — v0.1.0
      </div>
    </div>
  );
};

export default KaryaLoader;
