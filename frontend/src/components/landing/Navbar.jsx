import React, { useEffect, useRef, useState } from "react";

const NAV_ITEMS = [
  {
    label: "PRODUCT",
    target: "product",
    index: "01",
  },
  {
    label: "CAPABILITIES",
    target: "capabilities",
    index: "02",
  },
  {
    label: "HOW IT WORKS",
    target: "how-it-works",
    index: "03",
  },
  {
    label: "SECURITY",
    target: "security",
    index: "04",
  },
];

const OBSERVED_SECTIONS = [
  "home",
  "product",
  "capabilities",
  "how-it-works",
  "security",
];

export default function Navbar({ onLogin, onRegister }) {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState("home");
  const [menuOpen, setMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [progress, setProgress] = useState(0);

  const headerRef = useRef(null);
  const ticking = useRef(false);

  /*
  |--------------------------------------------------------------------------
  | INITIAL ENTRANCE
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setMounted(true);

      window.dispatchEvent(
        new CustomEvent("karya:nav-ready")
      );
    }, 120);

    return () => window.clearTimeout(timer);
  }, []);

  /*
  |--------------------------------------------------------------------------
  | SCROLL STATE + PAGE PROGRESS
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    const handleScroll = () => {
      if (ticking.current) return;

      ticking.current = true;

      window.requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        const documentHeight =
          document.documentElement.scrollHeight - window.innerHeight;

        const nextProgress =
          documentHeight > 0
            ? Math.min(
                100,
                Math.max(
                  0,
                  (scrollY / documentHeight) * 100
                )
              )
            : 0;

        setScrolled(scrollY > 24);
        setProgress(nextProgress);

        ticking.current = false;
      });
    };

    handleScroll();

    window.addEventListener(
      "scroll",
      handleScroll,
      { passive: true }
    );

    return () => {
      window.removeEventListener(
        "scroll",
        handleScroll
      );
    };
  }, []);

  /*
  |--------------------------------------------------------------------------
  | SECTION OBSERVER
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    const sections = OBSERVED_SECTIONS
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    if (!sections.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort(
            (a, b) =>
              b.intersectionRatio -
              a.intersectionRatio
          );

        if (!visible.length) return;

        const currentId =
          visible[0].target.id;

        setActive(currentId);

        /*
         * Broadcast the active section so other KARYA
         * components can synchronize their own motion.
         */
        window.dispatchEvent(
          new CustomEvent("karya:section", {
            detail: {
              id: currentId,
            },
          })
        );
      },
      {
        root: null,
        rootMargin:
          "-18% 0px -58% 0px",
        threshold: [0.05, 0.2, 0.4, 0.7],
      }
    );

    sections.forEach((section) => {
      observer.observe(section);
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  /*
  |--------------------------------------------------------------------------
  | CLOSE MOBILE MENU ON DESKTOP RESIZE
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMenuOpen(false);
      }
    };

    window.addEventListener(
      "resize",
      handleResize
    );

    return () => {
      window.removeEventListener(
        "resize",
        handleResize
      );
    };
  }, []);

  /*
  |--------------------------------------------------------------------------
  | ESCAPE KEY
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setMenuOpen(false);
      }
    };

    window.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, []);

  /*
  |--------------------------------------------------------------------------
  | SCROLL LOCK FOR MOBILE NAV
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    if (window.innerWidth >= 1024) return;

    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  /*
  |--------------------------------------------------------------------------
  | NAVIGATION
  |--------------------------------------------------------------------------
  */

  const scrollTo = (target) => {
    const element =
      document.getElementById(target);

    if (!element) return;

    setMenuOpen(false);

    /*
     * Broadcast navigation intent.
     */
    window.dispatchEvent(
      new CustomEvent("karya:navigation", {
        detail: {
          target,
        },
      })
    );

    const headerHeight =
      headerRef.current?.offsetHeight || 76;

    const elementTop =
      element.getBoundingClientRect().top +
      window.scrollY;

    const offsetTop =
      Math.max(0, elementTop - headerHeight);

    window.scrollTo({
      top: offsetTop,
      behavior: "smooth",
    });
  };

  /*
  |--------------------------------------------------------------------------
  | LOGIN
  |--------------------------------------------------------------------------
  */

  const handleLogin = () => {
    window.dispatchEvent(
      new CustomEvent("karya:login-intent")
    );

    if (onLogin) {
      onLogin();
      return;
    }

    window.location.href = "/login";
  };

  const handleRegister = () => {
    window.dispatchEvent(
      new CustomEvent("karya:register-intent")
    );

    if (onRegister) {
      onRegister();
      return;
    }

    window.location.href = "/register";
  };

  /*
  |--------------------------------------------------------------------------
  | LOGO
  |--------------------------------------------------------------------------
  */

  const handleLogoClick = () => {
    scrollTo("home");
  };

  return (
    <>
      {/* ==================================================================
          NAVIGATION SYSTEM
      ================================================================== */}

      <header
        ref={headerRef}
        className={`
          fixed
          inset-x-0
          top-0
          z-[100]
          transition-all
          duration-700
          ease-[cubic-bezier(0.16,1,0.3,1)]
          ${
            mounted
              ? "translate-y-0 opacity-100"
              : "-translate-y-5 opacity-0"
          }
        `}
      >
        {/* ================================================================
            SCROLL PROGRESS
        ================================================================ */}

        <div
          className="
            absolute
            bottom-0
            left-0
            h-px
            bg-white
            transition-[width]
            duration-150
            ease-linear
          "
          style={{
            width: `${progress}%`,
            opacity: scrolled ? 0.9 : 0,
          }}
          aria-hidden="true"
        />

        {/* ================================================================
            MAIN NAV
        ================================================================ */}

        <div
          className={`
            border-b
            transition-all
            duration-700
            ${
              scrolled
                ? "border-[#262626] bg-[#050505]"
                : "border-transparent bg-transparent"
            }
          `}
        >
          <div
            className="
              mx-auto
              flex
              h-[76px]
              max-w-[1500px]
              items-center
              justify-between
              px-5
              sm:px-8
              lg:px-12
              xl:px-14
            "
          >
            {/* ============================================================
                KARYA BRAND
            ============================================================ */}

            <button
              type="button"
              onClick={handleLogoClick}
              className="
                group
                relative
                flex
                items-center
                gap-3
                outline-none
              "
              aria-label="Go to KARYA home"
            >
              {/* K MARK */}

              <span
                className="
                  relative
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  overflow-hidden
                  border
                  border-[#363636]
                  text-white
                  transition-all
                  duration-500
                  ease-[cubic-bezier(0.16,1,0.3,1)]
                  group-hover:border-white
                  group-focus-visible:border-white
                "
              >
                {/* rotating frame */}

                <span
                  className="
                    pointer-events-none
                    absolute
                    inset-[4px]
                    border
                    border-[#242424]
                    transition-transform
                    duration-700
                    ease-[cubic-bezier(0.16,1,0.3,1)]
                    group-hover:rotate-45
                  "
                />

                {/* K */}

                <span
                  className="
                    relative
                    z-10
                    font-sans
                    text-sm
                    font-semibold
                    tracking-[-0.1em]
                  "
                >
                  K
                </span>

                {/* corner marker */}

                <span
                  className="
                    absolute
                    right-0
                    top-0
                    h-[3px]
                    w-[3px]
                    bg-white
                    opacity-0
                    transition-opacity
                    duration-300
                    group-hover:opacity-100
                  "
                />
              </span>

              {/* WORDMARK */}

              <span
                className="
                  hidden
                  font-mono
                  text-[10px]
                  font-semibold
                  tracking-[0.32em]
                  text-white
                  sm:block
                "
              >
                KARYA
              </span>
            </button>

            {/* ============================================================
                DESKTOP NAVIGATION
            ============================================================ */}

            <nav
              className="
                hidden
                items-center
                gap-7
                lg:flex
                xl:gap-9
              "
              aria-label="Primary navigation"
            >
              {NAV_ITEMS.map((item) => {
                const isActive =
                  active === item.target;

                return (
                  <button
                    key={item.target}
                    type="button"
                    onClick={() =>
                      scrollTo(item.target)
                    }
                    aria-current={
                      isActive
                        ? "page"
                        : undefined
                    }
                    className="
                      group
                      relative
                      flex
                      items-center
                      gap-2
                      py-3
                      outline-none
                    "
                  >
                    {/* index */}

                    <span
                      className={`
                        font-mono
                        text-[7px]
                        tracking-[0.16em]
                        transition-colors
                        duration-300
                        ${
                          isActive
                            ? "text-white"
                            : "text-[#444440]"
                        }
                      `}
                    >
                      {item.index}
                    </span>

                    {/* label */}

                    <span
                      className={`
                        font-mono
                        text-[8px]
                        font-medium
                        tracking-[0.2em]
                        transition-colors
                        duration-300
                        ${
                          isActive
                            ? "text-white"
                            : "text-[#777772] group-hover:text-white"
                        }
                      `}
                    >
                      {item.label}
                    </span>

                    {/* active line */}

                    <span
                      className={`
                        absolute
                        bottom-0
                        left-0
                        h-px
                        bg-white
                        transition-all
                        duration-500
                        ease-[cubic-bezier(0.16,1,0.3,1)]
                        ${
                          isActive
                            ? "w-full"
                            : "w-0 group-hover:w-full"
                        }
                      `}
                    />

                    {/* active node */}

                    <span
                      className={`
                        absolute
                        -right-2
                        top-1/2
                        h-1
                        w-1
                        -translate-y-1/2
                        bg-white
                        transition-all
                        duration-500
                        ${
                          isActive
                            ? "scale-100 opacity-100"
                            : "scale-0 opacity-0"
                        }
                      `}
                    />
                  </button>
                );
              })}
            </nav>

            {/* ============================================================
                RIGHT CONTROL AREA
            ============================================================ */}

            <div className="flex items-center gap-2 sm:gap-3">
              {/* SYSTEM STATUS */}

              <div
                className="
                  hidden
                  items-center
                  gap-2
                  pr-2
                  sm:flex
                  xl:pr-3
                "
              >
                <span
                  className="
                    h-1.5
                    w-1.5
                    rounded-full
                    bg-white
                    shadow-[0_0_0_2px_#202020]
                  "
                />

                <span
                  className="
                    font-mono
                    text-[7px]
                    tracking-[0.18em]
                    text-[#555550]
                  "
                >
                  LOCAL_RUNTIME
                </span>
              </div>

              {/* REGISTER */}

              <button
                type="button"
                onClick={handleRegister}
                className="hidden h-10 items-center border border-[#363636] px-4 font-mono text-[8px] font-semibold tracking-[0.18em] text-[#C8C8C3] outline-none transition-all duration-500 hover:border-white hover:bg-white hover:text-black focus-visible:border-white focus-visible:bg-white focus-visible:text-black sm:flex"
              >
                REGISTER
              </button>

              {/* LOGIN */}

              <button
                type="button"
                onClick={handleLogin}
                className="
                  group
                  flex
                  h-10
                  items-center
                  gap-3
                  border
                  border-[#363636]
                  px-4
                  font-mono
                  text-[8px]
                  font-semibold
                  tracking-[0.18em]
                  text-white
                  outline-none
                  transition-all
                  duration-500
                  ease-[cubic-bezier(0.16,1,0.3,1)]
                  hover:border-white
                  hover:bg-white
                  hover:text-black
                  focus-visible:border-white
                  focus-visible:bg-white
                  focus-visible:text-black
                "
              >
                <span className="hidden sm:inline">
                  LOGIN TO KARYA
                </span>

                <span className="sm:hidden">
                  LOGIN
                </span>

                <span
                  className="
                    inline-block
                    transition-transform
                    duration-500
                    ease-[cubic-bezier(0.16,1,0.3,1)]
                    group-hover:translate-x-1
                  "
                >
                  →
                </span>
              </button>

              {/* ========================================================
                  MOBILE MENU BUTTON
              ======================================================== */}

              <button
                type="button"
                onClick={() =>
                  setMenuOpen(
                    (value) => !value
                  )
                }
                className="
                  relative
                  flex
                  h-10
                  w-10
                  items-center
                  justify-center
                  border
                  border-[#292929]
                  outline-none
                  transition-all
                  duration-300
                  hover:border-[#555555]
                  focus-visible:border-white
                  lg:hidden
                "
                aria-label={
                  menuOpen
                    ? "Close navigation"
                    : "Open navigation"
                }
                aria-expanded={menuOpen}
              >
                <div className="relative h-4 w-4">
                  <span
                    className={`
                      absolute
                      left-0
                      top-[5px]
                      block
                      h-px
                      w-4
                      bg-white
                      transition-all
                      duration-500
                      ease-[cubic-bezier(0.16,1,0.3,1)]
                      ${
                        menuOpen
                          ? "translate-y-[1.5px] rotate-45"
                          : ""
                      }
                    `}
                  />

                  <span
                    className={`
                      absolute
                      left-0
                      top-[11px]
                      block
                      h-px
                      w-4
                      bg-white
                      transition-all
                      duration-500
                      ease-[cubic-bezier(0.16,1,0.3,1)]
                      ${
                        menuOpen
                          ? "-translate-y-[4.5px] -rotate-45"
                          : ""
                      }
                    `}
                  />
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* ================================================================
            MOBILE NAVIGATION
        ================================================================ */}

        <div
          className={`
            absolute
            left-0
            right-0
            top-[76px]
            overflow-hidden
            border-b
            border-[#242424]
            bg-[#050505]
            transition-all
            duration-700
            ease-[cubic-bezier(0.16,1,0.3,1)]
            lg:hidden
            ${
              menuOpen
                ? "max-h-[480px] opacity-100"
                : "pointer-events-none max-h-0 opacity-0"
            }
          `}
        >
          <div className="px-5 pb-6 pt-2 sm:px-8">
            {/* SYSTEM LABEL */}

            <div className="flex items-center justify-between border-b border-[#1D1D1D] py-4">
              <span
                className="
                  font-mono
                  text-[7px]
                  tracking-[0.24em]
                  text-[#4D4D49]
                "
              >
                KARYA / NAVIGATION
              </span>

              <span
                className="
                  font-mono
                  text-[7px]
                  tracking-[0.18em]
                  text-[#4D4D49]
                "
              >
                {String(
                  Math.round(progress)
                ).padStart(3, "0")}
                %
              </span>
            </div>

            {/* NAV ITEMS */}

            <nav
              aria-label="Mobile navigation"
              className="divide-y divide-[#1D1D1D]"
            >
              {NAV_ITEMS.map(
                (item, index) => {
                  const isActive =
                    active === item.target;

                  return (
                    <button
                      key={item.target}
                      type="button"
                      onClick={() =>
                        scrollTo(item.target)
                      }
                      className="
                        group
                        flex
                        w-full
                        items-center
                        justify-between
                        py-5
                        text-left
                        outline-none
                      "
                      style={{
                        transitionDelay: menuOpen
                          ? `${index * 55}ms`
                          : "0ms",
                      }}
                    >
                      <div className="flex items-center gap-4">
                        {/* index */}

                        <span
                          className={`
                            font-mono
                            text-[8px]
                            tracking-[0.15em]
                            transition-colors
                            duration-300
                            ${
                              isActive
                                ? "text-white"
                                : "text-[#41413D]"
                            }
                          `}
                        >
                          {item.index}
                        </span>

                        {/* label */}

                        <span
                          className={`
                            font-mono
                            text-[10px]
                            font-medium
                            tracking-[0.2em]
                            transition-colors
                            duration-300
                            ${
                              isActive
                                ? "text-white"
                                : "text-[#777772] group-hover:text-white"
                            }
                          `}
                        >
                          {item.label}
                        </span>
                      </div>

                      {/* arrow */}

                      <span
                        className={`
                          font-mono
                          text-sm
                          transition-all
                          duration-500
                          ${
                            isActive
                              ? "translate-x-0 text-white"
                              : "translate-x-2 text-[#444440] group-hover:translate-x-0 group-hover:text-white"
                          }
                        `}
                      >
                        →
                      </span>
                    </button>
                  );
                }
              )}
            </nav>

            {/* MOBILE SYSTEM FOOTER */}

            <div className="mt-5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-white" />

                <span
                  className="
                    font-mono
                    text-[7px]
                    tracking-[0.18em]
                    text-[#555550]
                  "
                >
                  SYSTEM ONLINE
                </span>
              </div>

              <span
                className="
                  font-mono
                  text-[7px]
                  tracking-[0.18em]
                  text-[#555550]
                "
              >
                LOCAL / PRIVATE
              </span>
            </div>

            <button
              type="button"
              onClick={handleRegister}
              className="mt-5 flex w-full items-center justify-between border border-[#363636] px-4 py-4 font-mono text-[9px] font-semibold tracking-[0.18em] text-white transition hover:border-white hover:bg-white hover:text-black"
            >
              REGISTER NEW WORKSPACE
              <span>→</span>
            </button>
          </div>
        </div>
      </header>

      {/* ==================================================================
          GLOBAL NAVIGATION MOTION
      ================================================================== */}

      <style>{`
        @media (prefers-reduced-motion: reduce) {
          header,
          header *,
          header *::before,
          header *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
          }
        }

        @media (max-width: 640px) {
          header {
            --karya-mobile-nav-height: 72px;
          }
        }
      `}</style>
    </>
  );
}