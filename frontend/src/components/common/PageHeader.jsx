import { ChevronRight } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

export default function PageHeader({ eyebrow, title, description, action }) {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);
  const breadcrumbs = segments
    .filter((segment) => segment !== "app")
    .map((segment) => segment.replace(/-/g, " "));

  return (
    <div className="mb-8 flex flex-col gap-4 border-b border-[#202020] pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <div className="mb-4 flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.18em] text-[#555550]">
          <Link to="/app" className="transition hover:text-white">Workspace</Link>
          {breadcrumbs.map((crumb) => (
            <span key={crumb} className="flex items-center gap-2">
              <ChevronRight size={11} />
              <span>{crumb}</span>
            </span>
          ))}
        </div>
        {eyebrow ? (
          <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">{eyebrow}</p>
        ) : null}
        <h1 className="mt-4 text-3xl font-semibold tracking-[-0.04em] text-[#F5F5F5] sm:text-5xl">
          {title}
        </h1>
        {description ? <p className="mt-3 text-sm text-[#8A8A85]">{description}</p> : null}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
