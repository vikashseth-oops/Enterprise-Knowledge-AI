import React, { useEffect, useState } from "react";
import { useAppStore, ViewType } from "../lib/store";
import {
  Menu,
  Moon,
  Sun,
  Command,
  Activity,
  CheckCircle2,
  AlertCircle,
  FileText,
  GitBranch,
  BarChart3,
  Settings,
  MessageSquare,
} from "lucide-react";
import { api } from "../lib/api";

const VIEW_TITLES: Record<ViewType, { title: string; subtitle: string; icon: any }> = {
  chat: { title: "Agent Workspace", subtitle: "Grounded conversational RAG with LangGraph", icon: MessageSquare },
  knowledge: { title: "Knowledge Base", subtitle: "Multi-format document parsing & vector indexing", icon: FileText },
  trace: { title: "Agent Execution Trace", subtitle: "Node-level latency, tokens & reasoning waterfall", icon: GitBranch },
  eval: { title: "Model & Retrieval Evals", subtitle: "Recall@k, MRR, nDCG & concurrency benchmarks", icon: BarChart3 },
  settings: { title: "System Settings", subtitle: "API connectivity, model selection & tuning parameters", icon: Settings },
};

export const Header: React.FC = () => {
  const { activeView, theme, setTheme, setSidebarOpen, setCommandPaletteOpen } = useAppStore();
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    api.checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  const current = VIEW_TITLES[activeView] || VIEW_TITLES.chat;
  const Icon = current.icon;

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header className="h-16 border-b border-border bg-card/60 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        {/* Mobile menu button */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted min-w-[44px] min-h-[44px] flex items-center justify-center transition-colors"
          aria-label="Open Sidebar Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground tracking-tight">{current.title}</h1>
            <p className="text-xs text-muted-foreground hidden sm:block">{current.subtitle}</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Backend health status badge */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
            isHealthy === true
              ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
              : isHealthy === false
              ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20"
              : "bg-muted text-muted-foreground border-border"
          }`}
          title={isHealthy ? "Cloud Run backend ready" : "Backend health status unknown or starting"}
        >
          <span className={`w-2 h-2 rounded-full ${isHealthy ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
          <span className="hidden md:inline">{isHealthy ? "Engine Connected" : "Local Mode"}</span>
        </div>

        {/* Command palette search shortcut */}
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-muted/40 hover:bg-muted text-muted-foreground hover:text-foreground text-xs font-medium transition-colors"
        >
          <Command className="w-3.5 h-3.5" />
          <span>Search</span>
          <kbd className="px-1.5 py-0.5 rounded bg-background border border-border text-[10px] text-muted-foreground">⌘K</kbd>
        </button>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted min-w-[44px] min-h-[44px] flex items-center justify-center transition-colors"
          aria-label="Toggle Color Theme"
        >
          {theme === "dark" ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
};
