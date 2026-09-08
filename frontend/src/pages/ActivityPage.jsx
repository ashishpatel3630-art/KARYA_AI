import { Activity as ActivityIcon } from "lucide-react";
import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

export default function ActivityPage() {
  const { activities } = useOperations();
  return <div><PageHeader eyebrow="Observability" title="Activity" description="Every meaningful system transition is recorded in one chronological execution trail." /><div className="border-l border-[#2A2A2A]">{activities.map((activity) => <article key={activity.id} className="relative border-b border-[#202020] py-5 pl-7"><span className="absolute -left-[5px] top-7 h-2 w-2 bg-white" /><div className="flex flex-wrap items-center gap-3 font-mono text-[9px] uppercase tracking-[0.16em] text-[#777772]"><span>{activity.timestamp}</span><span>{activity.type}</span><span className="text-[#C8C8C3]">{activity.severity}</span></div><h2 className="mt-3 text-lg text-white">{activity.description}</h2><p className="mt-2 text-sm text-[#777772]">{activity.actor} · {activity.entity}</p></article>)}</div><div className="mt-8 flex items-center gap-3 text-xs text-[#777772]"><ActivityIcon size={15} /> Local activity stream · API audit events can replace this state later.</div></div>;
}
