import { useNavigate } from "react-router-dom";

import Navbar from "../components/landing/Navbar";
import Hero from "../components/landing/Hero";
import TrustBar from "../components/landing/TrustBar";
import Problem from "../components/landing/Problem";
import Solution from "../components/landing/Solution";
import Features from "../components/landing/Features";
import HowItWorks from "../components/landing/HowItWorks";
import AIEmployeePreview from "../components/landing/AIEmployeePreview";
import Security from "../components/landing/Security";
import UseCases from "../components/landing/UseCases";
import Stats from "../components/landing/Stats";
import CTA from "../components/landing/CTA";
import Footer from "../components/landing/Footer";

function Landing() {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-[#050505] text-white">
      <Navbar onRegister={() => navigate("/register")} onLogin={() => navigate("/login")} />

      <Hero onStart={() => navigate("/login")} />

      <TrustBar />

      <Problem />

      <Solution />

      <Features />

      <HowItWorks />

      <AIEmployeePreview />

      <Security />

      <UseCases />

      <Stats />

      <CTA onStart={() => navigate("/login")} />

      <Footer onLogin={() => navigate("/login")} />
    </main>
  );
}

export default Landing;