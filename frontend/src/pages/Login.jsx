import { useState } from "react";
import { ArrowLeft, ArrowRight, LoaderCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate("/app");
    } catch (requestError) {
      setError(requestError.message || "The authentication service is unavailable.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#050505] px-6 py-10 text-white">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-6xl flex-col justify-between">
        <a href="/" className="flex w-fit items-center gap-3 text-xs uppercase tracking-[0.25em] text-[#8A8A85] transition hover:text-white">
          <ArrowLeft size={15} />
          Karya
        </a>

        <section className="mx-auto w-full max-w-md border border-[#242424] bg-[#0A0A0A] p-8 sm:p-10">
          <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">Secure access</p>
          <h1 className="mt-5 text-4xl font-semibold tracking-[-0.04em]">Enter your workspace.</h1>
          <p className="mt-4 text-sm leading-6 text-[#8A8A85]">Sign in to connect with your KARYA operating system.</p>
          {location.state?.message && <p className="mt-5 border border-[#2A2A2A] bg-[#111111] px-4 py-3 text-sm text-[#F5F5F5]">{location.state.message}</p>}

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Work email
              <input
                required
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-2 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#555550] focus:border-white"
                placeholder="you@company.com"
              />
            </label>

            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Password
              <input
                required
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-2 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#555550] focus:border-white"
                placeholder="Enter your password"
              />
            </label>

            {error && <p className="border border-[#6f2424] bg-[#241010] px-4 py-3 text-sm text-[#ff8b8b]">{error}</p>}

            <button
              type="submit"
              disabled={isSubmitting}
              className="group flex w-full items-center justify-center gap-3 bg-white px-5 py-3.5 text-xs font-semibold uppercase tracking-widest text-black transition hover:bg-[#D8D8D8] disabled:cursor-wait disabled:opacity-60"
            >
              {isSubmitting ? <LoaderCircle size={16} className="animate-spin" /> : "Open desktop"}
              {!isSubmitting && <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />}
            </button>
          </form>
        </section>

        <p className="text-[9px] uppercase tracking-[0.2em] text-[#555550]">Karya // Authenticated operations</p>
      </div>
    </main>
  );
}

export default Login;
