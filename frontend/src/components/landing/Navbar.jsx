import React, { useEffect, useState } from "react";

const NAV_ITEMS = [
  { label: "PRODUCT", target: "product" },
  { label: "CAPABILITIES", target: "capabilities" },
  { label: "HOW IT WORKS", target: "how-it-works" },
  { label: "SECURITY", target: "security" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState("home");
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 24);

      const sections = [
        "home",
        "product",
        "capabilities",
        "how-it-works",
        "security",
      ];

      let current = "home";

      sections.forEach((id) => {
        const element = document.getElementById(id);

        if (!element) return;

        const rect = element.getBoundingClientRect();

        if (rect.top <= window.innerHeight * 0.42) {
          current = id;
        }
      });

      setActive(current);
    };

    handleScroll();

    window.addEventListener("scroll", handleScroll, {
      passive: true,
    });

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const scrollTo = (target) => {
    const element = document.getElementById(target);

    if (!element) return;

    element.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

    setMenuOpen(false);
  };

  return (
    <>
      <header
        className={`
          fixed
          left-0
          right-0
          top-0
          z-[100]
          border-b
          transition-all
          duration-700
          ${
            scrolled
              ? "border-[#242424] bg-[#050505]/95 backdrop-blur-xl"
              : "border-transparent bg-transparent"
          }
        `}
      >
        <div className="mx-auto flex h-[76px] max-w-[1500px] items-center justify-between px-6 sm:px-10 lg:px-14">
          {/* LOGO */}

          <button
            type="button"
            onClick={() => scrollTo("home")}
            className="group flex items-center gap-3"
          >
            <span
              className="
                relative
                flex
                h-9
                w-9
                items-center
                justify-center
                border
                border-[#3A3A3A]
                font-sans
                text-sm
                font-semibold
                tracking-[-0.08em]
                text-white
                transition-all
                duration-500
                group-hover:border-white
              "
            >
              K
            </span>

            <span className="font-mono text-[10px] font-semibold tracking-[0.3em] text-white">
              KARYA
            </span>
          </button>

          {/* DESKTOP NAV */}

          <nav className="hidden items-center gap-9 lg:flex">
            {NAV_ITEMS.map((item) => {
              const isActive = active === item.target;

              return (
                <button
                  key={item.target}
                  type="button"
                  onClick={() => scrollTo(item.target)}
                  className="
                    group
                    relative
                    py-3
                    font-mono
                    text-[8px]
                    font-medium
                    uppercase
                    tracking-[0.2em]
                    text-[#777772]
                    transition-colors
                    duration-300
                    hover:text-white
                  "
                >
                  {item.label}

                  <span
                    className={`
                      absolute
                      bottom-0
                      left-0
                      h-px
                      bg-white
                      transition-all
                      duration-500
                      ${
                        isActive
                          ? "w-full"
                          : "w-0 group-hover:w-full"
                      }
                    `}
                  />
                </button>
              );
            })}
          </nav>

          {/* RIGHT */}

          <div className="flex items-center gap-3">
            <span className="hidden font-mono text-[8px] tracking-[0.18em] text-[#555550] sm:block">
              LOCAL_RUNTIME
            </span>

            <a
              href="/app"
              className="
                group
                flex
                h-10
                items-center
                gap-3
                border
                border-[#383838]
                px-4
                font-mono
                text-[8px]
                font-semibold
                uppercase
                tracking-[0.18em]
                text-white
                transition-all
                duration-500
                hover:border-white
                hover:bg-white
                hover:text-black
              "
            >
              ENTER KARYA

              <span className="transition-transform duration-500 group-hover:translate-x-1">
                →
              </span>
            </a>

            {/* MOBILE */}

            <button
              type="button"
              onClick={() => setMenuOpen((value) => !value)}
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                border
                border-[#292929]
                lg:hidden
              "
              aria-label="Toggle navigation"
            >
              <div className="space-y-1.5">
                <span
                  className={`
                    block
                    h-px
                    w-4
                    bg-white
                    transition-all
                    ${
                      menuOpen
                        ? "translate-y-[3px] rotate-45"
                        : ""
                    }
                  `}
                />

                <span
                  className={`
                    block
                    h-px
                    w-4
                    bg-white
                    transition-all
                    ${
                      menuOpen
                        ? "-translate-y-[2px] -rotate-45"
                        : ""
                    }
                  `}
                />
              </div>
            </button>
          </div>
        </div>

        {/* MOBILE MENU */}

        <div
          className={`
            overflow-hidden
            border-t
            border-[#242424]
            bg-[#050505]
            transition-all
            duration-700
            lg:hidden
            ${
              menuOpen
                ? "max-h-[360px] opacity-100"
                : "max-h-0 opacity-0"
            }
          `}
        >
          <div className="px-6 py-6 sm:px-10">
            {NAV_ITEMS.map((item, index) => (
              <button
                key={item.target}
                type="button"
                onClick={() => scrollTo(item.target)}
                className="
                  flex
                  w-full
                  items-center
                  justify-between
                  border-b
                  border-[#1C1C1C]
                  py-5
                  text-left
                  font-mono
                  text-[9px]
                  uppercase
                  tracking-[0.2em]
                  text-[#888883]
                "
              >
                <span>{item.label}</span>

                <span className="text-[#444440]">
                  0{index + 1}
                </span>
              </button>
            ))}
          </div>
        </div>
      </header>
    </>
  );
}