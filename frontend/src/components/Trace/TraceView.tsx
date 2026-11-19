import React from "react";
import { useAppStore } from "../../lib/store";
import {
  GitBranch,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ArrowRight,
  Database,
  Cpu,
  ShieldCheck,
  Search,
} from "lucide-react";

const NODE_ICONS: Record<string, any> = {
  route: Cpu,
  rewrite: Search,
  retrieve: Database,
  grade: ShieldCheck,
  generate: Layers,
  verify: CheckCircle2,
  tools: Cpu,
};

export const TraceView: React.FC = () => {
  const { latestTrace, sessions, activeSessionId, setActiveView } = useAppStore();

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const lastAssistantMsg = activeSession?.messages
    .slice()
    .reverse()
    .find((m) => m.role === "assistant" && m.trace && m.trace.length > 0);

  const traceData = latestTrace || (lastAssistantMsg?.trace ? { latency: lastAssistantMsg.latency!, trace: lastAssistantMsg.trace } : null);

  if (!traceData || !traceData.trace || traceData.trace.length === 0) {
    return (
      <div className="max-w-4xl mx-auto w-full p-8 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-muted border border-border flex items-center justify-center text-muted-foreground mx-auto">
          <GitBranch className="w-6 h-6" />
        </div>
        <h3 className="text-base font-semibold text-foreground">No Active Execution Trace</h3>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto">
          Ask a question in the Agent Chat workspace to observe the real-time LangGraph node execution timeline, latency breakdown, and token consumption.
        </p>
        <button
          onClick={() => setActiveView("chat")}
          className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:opacity-90"
        >
          Open Chat Workspace
        </button>
      </div>
    );
  }

  const { latency, trace } = traceData;

  return (
    <div className="max-w-4xl mx-auto w-full p-4 sm:p-6 space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl border border-border bg-card">
          <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Total Duration</span>
          <div className="text-xl font-bold font-mono text-foreground mt-1">{latency.total_ms} ms</div>
        </div>
        <div className="p-4 rounded-xl border border-border bg-card">
          <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Retrieval Latency</span>
          <div className="text-xl font-bold font-mono text-primary mt-1">{latency.retrieve_ms} ms</div>
        </div>
        <div className="p-4 rounded-xl border border-border bg-card">
          <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Generation Latency</span>
          <div className="text-xl font-bold font-mono text-foreground mt-1">{latency.generate_ms} ms</div>
        </div>
        <div className="p-4 rounded-xl border border-border bg-card">
          <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Executed Spans</span>
          <div className="text-xl font-bold font-mono text-foreground mt-1">{trace.length} Steps</div>
        </div>
      </div>

      {/* Waterfall Timeline */}
      <div className="p-6 rounded-2xl border border-border bg-card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-primary" />
            <span>LangGraph Execution Waterfall</span>
          </h3>
          <span className="text-xs text-muted-foreground font-mono">P95 Target: &le; 190ms retrieval</span>
        </div>

        <div className="space-y-3 pt-2">
          {trace.map((span, idx) => {
            const Icon = NODE_ICONS[span.node] || GitBranch;
            const percentage = Math.max(8, Math.min(100, (span.duration_ms / (latency.total_ms || 1)) * 100));

            return (
              <div key={idx} className="p-3.5 rounded-xl border border-border bg-muted/20 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2.5">
                    <div className="w-6 h-6 rounded bg-primary/10 text-primary flex items-center justify-center">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="font-semibold text-foreground uppercase tracking-wider font-mono">
                      {idx + 1}. {span.node}
                    </span>
                  </div>
                  <span className="font-mono text-muted-foreground font-medium">{span.duration_ms} ms</span>
                </div>

                {/* Duration visual bar */}
                <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>

                {/* Metadata tags */}
                {span.metadata && Object.keys(span.metadata).length > 0 && (
                  <div className="flex items-center gap-2 flex-wrap pt-1 text-[11px] font-mono text-muted-foreground">
                    {Object.entries(span.metadata).map(([k, v]) => (
                      <span key={k} className="px-1.5 py-0.5 rounded bg-muted border border-border">
                        {k}: {String(v)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
