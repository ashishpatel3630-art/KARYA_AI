import React from "react";

function Hero({ onStart }) {
  return (
    <section className="relative min-h-[calc(100vh-80px)] overflow-hidden bg-[#050505] text-[#F5F5F5]">
      
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage: `
            linear-gradient(#F5F5F5 1px, transparent 1px),
            linear-gradient(90deg, #F5F5F5 1px, transparent 1px)
          `,
          backgroundSize: "80px 80px",
        }}
      />

      
      <div className="relative mx-auto flex min-h-[calc(100vh-80px)] max-w-7xl flex-col items-center px-6 pt-28 text-center">
        
     
        <div className="mb-8 flex w-fit items-center gap-2 border border-[#2A2A2A] bg-[#0A0A0A] px-3 py-1.5">
          <span className="h-1.5 w-1.5 bg-[#F5F5F5]" />

          <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-[#8A8A85]">
            Confidential Industrial AI
          </p>
        </div>

        
        <h1 className="select-none text-[clamp(6rem,18vw,15rem)] font-black leading-[0.75] tracking-[-0.08em] text-[#F5F5F5]">
          KARYA
        </h1>

        
        <div className="my-10 h-px w-24 bg-[#2A2A2A]" />

       
        <h2 className="max-w-4xl text-balance text-2xl font-medium uppercase leading-tight tracking-[-0.02em] text-[#F5F5F5] md:text-4xl lg:text-5xl">
          Your AI Employee
          <span className="text-[#8A8A85]"> for </span>
          Industrial Operations
        </h2>

       
        <p className="mt-7 max-w-2xl text-sm leading-7 text-[#8A8A85] md:text-base">
          An autonomous intelligence layer built for industrial operations —
          monitoring systems, analyzing data, coordinating workflows, and
          executing operational tasks.
        </p>

       
        <div className="mt-10 flex flex-col gap-3 sm:flex-row">
          <button
            onClick={onStart}
            className="group border border-[#F5F5F5] bg-[#F5F5F5] px-7 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-[#050505] transition hover:bg-transparent hover:text-[#F5F5F5]"
          >
            Work KARYA
            <span className="ml-3 inline-block transition-transform group-hover:translate-x-1">
              →
            </span>
          </button>

          <button className="border border-[#2A2A2A] bg-[#0A0A0A] px-7 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-[#8A8A85] transition hover:border-[#F5F5F5] hover:text-[#F5F5F5]">
            Explore System
          </button>
        </div>

        
        <div className="mt-auto flex w-full max-w-5xl items-center justify-between border-t border-[#1A1A1A] py-5 text-[9px] uppercase tracking-[0.2em] text-[#555550]">
          <span>Autonomous Operations Layer</span>

          <span>System // 001</span>

          <span>AI Core Active</span>
        </div>
      </div>
    </section>
  );
}

export default Hero;