import { ArrowRight } from "lucide-react";

function CTA({ onStart }) {
  return (
    <section className="border-b border-[#1A1A1A] bg-[#050505] py-32">
      <div className="mx-auto max-w-5xl px-6 text-center">
        <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
          Deploy KARYA
        </p>

        <h2 className="mt-6 text-5xl font-semibold tracking-[-0.04em] text-white sm:text-7xl">
          Build your
          <br />
          AI workforce.
        </h2>

        <p className="mx-auto mt-6 max-w-xl text-sm leading-7 text-[#8A8A85]">
          Move from fragmented operational intelligence to autonomous
          execution.
        </p>

        <button
          onClick={onStart}
          className="group mt-10 inline-flex items-center gap-3 bg-white px-7 py-4 text-xs font-semibold uppercase tracking-widest text-black transition hover:bg-[#D8D8D8]"
        >
          Get Started
          <ArrowRight
            size={16}
            className="transition-transform group-hover:translate-x-1"
          />
        </button>
      </div>
    </section>
  );
}

export default CTA;