import { useState } from "react";

import KaryaLoading from "./components/loading/KaryaLoading";

import Navbar from "./components/landing/Navbar";
import Hero from "./components/landing/Hero";
import TrustBar from "./components/landing/TrustBar";
import Problem from "./components/landing/Problem";
import Solution from "./components/landing/Solution";
import HowItWorks from "./components/landing/HowItWorks";
import Features from "./components/landing/Features";
import AIEmployeePreview from "./components/landing/AIEmployeePreview";
import UseCases from "./components/landing/UseCases";
import Security from "./components/landing/Security";
import Stats from "./components/landing/Stats";
import CTA from "./components/landing/CTA";
import Footer from "./components/landing/Footer";

function App() {
  const [loading, setLoading] = useState(true);

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {loading && (
        <KaryaLoading
          duration={5200}
          onComplete={() => setLoading(false)}
        />
      )}

      <Navbar />

      <main>
        <Hero />

        <TrustBar />

        <Problem />

        <Solution />

        <HowItWorks />

        <Features />

        <AIEmployeePreview />

        <UseCases />

        <Security />

        <Stats />

        <CTA />
      </main>

      <Footer />
    </div>
  );
}

export default App;