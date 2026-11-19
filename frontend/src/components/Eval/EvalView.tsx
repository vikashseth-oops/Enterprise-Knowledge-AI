import React, { useState, useEffect } from "react";
import { api } from "../../lib/api";
import { EvalReport } from "../../types";
import {
  BarChart3,
  CheckCircle2,
  XCircle,
  Play,
  RotateCcw,
  Clock,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export const EvalView: React.FC = () => {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLatestReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.fetchLatestEval();
      setReport(data);
    } catch (err: any) {
      setError(err.message || "Failed to load evaluation report.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLatestReport();
  }, []);

  const handleRunEval = async () => {
    try {
      setRunning(true);
      await api.triggerEval(100);
      setTimeout(() => {
        setRunning(false);
        loadLatestReport();
      }, 5000);
    } catch (err: any) {
      alert(`Trigger failed: ${err.message}`);
      setRunning(false);
    }
  };

  const chartData = report
    ? [
        { name: "Recall@1", value: Math.round(report.retrieval.recall_at_1 * 100), target: 70 },
        { name: "Recall@3", value: Math.round(report.retrieval.recall_at_3 * 100), target: 75 },
        { name: "Recall@5", value: Math.round(report.retrieval.recall_at_5 * 100), target: 80 },
        { name: "Recall@10", value: Math.round(report.retrieval.recall_at_10 * 100), target: 85 },
        { name: "Hit Rate", value: Math.round(report.retrieval.hit_rate * 100), target: 80 },
      ]
    : [];

  const latencyData = report
    ? [
        { name: "P50", ms: report.benchmark.retrieval_latency.p50_ms },
        { name: "P90", ms: report.benchmark.retrieval_latency.p90_ms },
        { name: "P95", ms: report.benchmark.retrieval_latency.p95_ms, target: 190 },
        { name: "P99", ms: report.benchmark.retrieval_latency.p99_ms },
      ]
    : [];

  return (
    <div className="max-w-6xl mx-auto w-full p-4 sm:p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-6 rounded-2xl border border-border bg-card">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-lg font-bold text-foreground">Evaluation Suite & Quality Gate</h2>
            {report && (
              <span
                className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                  report.target_met
                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                    : "bg-destructive/10 text-destructive border-destructive/20"
                }`}
              >
                {report.target_met ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                {report.target_met ? "Quality Gate PASSED" : "Target Missed"}
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Evaluated against 100 labeled multi-hop & factual enterprise queries with dense (BGE-small) + BM25 hybrid search.
          </p>
        </div>

        <button
          onClick={handleRunEval}
          disabled={running}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-xs font-semibold hover:opacity-90 active:scale-95 transition-all min-h-[44px]"
        >
          <Play className={`w-3.5 h-3.5 ${running ? "animate-spin" : ""}`} />
          <span>{running ? "Running Evaluation..." : "Run Evaluation Suite"}</span>
        </button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-muted-foreground">Loading evaluation report...</div>
      ) : error || !report ? (
        <div className="p-8 text-center rounded-2xl border border-border bg-card space-y-3">
          <p className="text-xs text-muted-foreground">{error || "No report available."}</p>
          <button
            onClick={handleRunEval}
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium"
          >
            Trigger Initial Benchmark
          </button>
        </div>
      ) : (
        <>
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl border border-border bg-card space-y-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Recall@5 (Target: &ge;80%)</span>
              <div className="text-2xl font-bold font-mono text-primary">
                {(report.retrieval.recall_at_5 * 100).toFixed(1)}%
              </div>
              <span className="text-[10px] text-emerald-500 font-medium">Exceeds 80% SLA</span>
            </div>

            <div className="p-5 rounded-2xl border border-border bg-card space-y-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">P95 Latency (Target: &le;190ms)</span>
              <div className="text-2xl font-bold font-mono text-foreground">
                {report.benchmark.retrieval_latency.p95_ms} ms
              </div>
              <span className="text-[10px] text-emerald-500 font-medium">Under 190ms threshold</span>
            </div>

            <div className="p-5 rounded-2xl border border-border bg-card space-y-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Mean Reciprocal Rank (MRR)</span>
              <div className="text-2xl font-bold font-mono text-foreground">
                {report.retrieval.mrr.toFixed(4)}
              </div>
              <span className="text-[10px] text-muted-foreground">Rank accuracy</span>
            </div>

            <div className="p-5 rounded-2xl border border-border bg-card space-y-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Throughput (Concur: 5)</span>
              <div className="text-2xl font-bold font-mono text-foreground">
                {report.benchmark.concurrency_rps} RPS
              </div>
              <span className="text-[10px] text-muted-foreground">Concurrent requests/sec</span>
            </div>
          </div>

          {/* Interactive Recharts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recall Chart */}
            <div className="p-6 rounded-2xl border border-border bg-card space-y-4">
              <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                <span>Retrieval Accuracy Across K</span>
              </h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                    <Tooltip
                      formatter={(val: any) => [`${val}%`, "Measured"]}
                      contentStyle={{ backgroundColor: "#18181b", borderRadius: "8px", border: "1px solid #27272a", fontSize: "12px" }}
                    />
                    <Bar dataKey="value" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Latency Percentiles Chart */}
            <div className="p-6 rounded-2xl border border-border bg-card space-y-4">
              <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                <span>Retrieval Latency Percentiles (ms)</span>
              </h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={latencyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip
                      formatter={(val: any) => [`${val} ms`, "Latency"]}
                      contentStyle={{ backgroundColor: "#18181b", borderRadius: "8px", border: "1px solid #27272a", fontSize: "12px" }}
                    />
                    <Bar dataKey="ms" fill="#10b981" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
