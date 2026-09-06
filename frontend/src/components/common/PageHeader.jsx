export default function PageHeader({ eyebrow, title, description, action }) {
  return (
    <div className="mb-8 flex flex-col gap-4 border-b border-[#202020] pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div>
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
