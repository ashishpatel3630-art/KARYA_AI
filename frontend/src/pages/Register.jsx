import { useState } from "react";
import { ArrowLeft, ArrowRight, Clipboard, LoaderCircle, RefreshCw } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [role, setRole] = useState("user");

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { signUp } = useAuth();
  const navigate = useNavigate();

  function generateSecretKey() {
    const bytes = new Uint8Array(18);
    crypto.getRandomValues(bytes);
    const value = Array.from(bytes, (byte) => byte.toString(36).padStart(2, "0"))
      .join("")
      .toUpperCase();
    setSecretKey(`KRYA-${value.slice(0, 6)}-${value.slice(6, 12)}-${value.slice(12, 18)}`);
  }

  async function copySecretKey() {
    if (secretKey) {
      await navigator.clipboard.writeText(secretKey);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (password !== confirmPassword) {
      setError("Passwords must match.");
      return;
    }

    setIsSubmitting(true);

    try {
      await signUp({
        name,
        email,
        password,
        secret_key: secretKey,
        role,
      });

      navigate("/login", {
        state: {
          message: "Account created. Sign in to open your workspace.",
        },
      });
    } catch (requestError) {
      setError(
        requestError.message ||
          "The registration service is unavailable.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#050505] px-6 py-10 text-white">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-6xl flex-col justify-between">

        {/* Back */}
        <Link
          to="/"
          className="flex w-fit items-center gap-3 text-xs uppercase tracking-[0.25em] text-[#8A8A85] transition hover:text-white"
        >
          <ArrowLeft size={15} />
          Karya
        </Link>

        {/* Register Card */}
        <section className="mx-auto w-full max-w-md border border-[#242424] bg-[#0A0A0A] p-8 sm:p-10">

          <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
            Create access
          </p>

          <h1 className="mt-5 text-4xl font-semibold tracking-[-0.04em]">
            Build your workspace.
          </h1>

          <p className="mt-4 text-sm leading-6 text-[#8A8A85]">
            Create a secure KARYA account and configure your workspace access.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">

            <p className="border-b border-[#1A1A1A] pb-2 text-[10px] uppercase tracking-[0.25em] text-[#8A8A85]">Identity</p>
            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Full name

              <input
                required
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="mt-2 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#555550] focus:border-white"
                placeholder="John Doe"
              />
            </label>

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

            <p className="border-b border-[#1A1A1A] pb-2 pt-2 text-[10px] uppercase tracking-[0.25em] text-[#8A8A85]">Security</p>
            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Password

              <input
                required
                minLength={8}
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-2 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#555550] focus:border-white"
                placeholder="At least 8 characters"
              />
            </label>

            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Confirm password
              <input
                required
                minLength={8}
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                className="mt-2 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#555550] focus:border-white"
                placeholder="Repeat your password"
              />
            </label>

            <p className="border-b border-[#1A1A1A] pb-2 pt-2 text-[10px] uppercase tracking-[0.25em] text-[#8A8A85]">Access</p>
            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Secret key

              <div className="mt-2 flex gap-2">
                <input
                  required
                  type="text"
                  value={secretKey}
                  onChange={(event) => setSecretKey(event.target.value)}
                  className="min-w-0 flex-1 border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#555550] focus:border-white"
                  placeholder="Generate an access key"
                />
                <button type="button" onClick={generateSecretKey} title="Generate secret key" className="border border-[#2A2A2A] px-3 text-[#8A8A85] transition hover:border-white hover:text-white">
                  <RefreshCw size={16} />
                </button>
                <button type="button" onClick={copySecretKey} disabled={!secretKey} title="Copy secret key" className="border border-[#2A2A2A] px-3 text-[#8A8A85] transition hover:border-white hover:text-white disabled:opacity-40">
                  <Clipboard size={16} />
                </button>
              </div>

              <span className="mt-2 block text-[10px] normal-case tracking-normal text-[#555550]">
                Required to verify your registration access.
              </span>
            </label>

            <label className="block text-xs uppercase tracking-widest text-[#8A8A85]">
              Account role

              <select
                required
                value={role}
                onChange={(event) => setRole(event.target.value)}
                className="mt-2 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none transition focus:border-white"
              >
                <option value="user">User</option>
                <option value="manager">Manager</option>
                <option value="admin">Administrator</option>
              </select>
              <span className="mt-2 block text-[10px] normal-case tracking-normal text-[#555550]">Elevated roles require backend-issued authorization.</span>
            </label>

            {error && (
              <p className="border border-[#6f2424] bg-[#241010] px-4 py-3 text-sm text-[#ff8b8b]">
                {error}
              </p>
            )}

            {/* SUBMIT */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="group flex w-full items-center justify-center gap-3 bg-white px-5 py-3.5 text-xs font-semibold uppercase tracking-widest text-black transition hover:bg-[#D8D8D8] disabled:cursor-wait disabled:opacity-60"
            >
              {isSubmitting ? (
                <LoaderCircle
                  size={16}
                  className="animate-spin"
                />
              ) : (
                "Create account"
              )}

              {!isSubmitting && (
                <ArrowRight
                  size={16}
                  className="transition-transform group-hover:translate-x-1"
                />
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-[#8A8A85]">
            Already have access?{" "}
            <Link
              to="/login"
              className="text-white underline underline-offset-4"
            >
              Sign in
            </Link>
          </p>
        </section>

        <p className="text-[9px] uppercase tracking-[0.2em] text-[#555550]">
          Karya // Authenticated operations
        </p>
      </div>
    </main>
  );
}

export default Register;
