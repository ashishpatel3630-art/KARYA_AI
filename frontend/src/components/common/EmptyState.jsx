export default function EmptyState({ title, description, action }) {
  return (
    <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-8 text-center">
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-[#2A2A2A] text-lg text-[#F5F5F5]">
        •
      </div>
      <h3 className="text-xl font-medium text-[#F5F5F5]">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-[#8A8A85]">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}
