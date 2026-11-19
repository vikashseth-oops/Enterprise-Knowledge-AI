import React from "react";
import { useAppStore, ViewType } from "../lib/store";
import {
  MessageSquare,
  FileText,
  GitBranch,
  BarChart3,
  Settings,
  Plus,
  Trash2,
  Layers,
  X,
  ExternalLink,
} from "lucide-react";

interface NavItem {
  id: ViewType;
  label: string;
  icon: any;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: "chat", label: "Agent Chat", icon: MessageSquare },
  { id: "knowledge", label: "Knowledge Base", icon: FileText },
  { id: "trace", label: "Agent Trace", icon: GitBranch },
  { id: "eval", label: "Evaluation", icon: BarChart3, badge: "CI" },
  { id: "settings", label: "Settings", icon: Settings },
];

export const Sidebar: React.FC = () => {
  const {
    activeView,
    setActiveView,
    isSidebarOpen,
    setSidebarOpen,
    sessions,
    activeSessionId,
    setActiveSessionId,
    createSession,
    deleteSession,
  } = useAppStore();

  const handleNavClick = (view: ViewType) => {
    setActiveView(view);
    setSidebarOpen(false);
  };

  const handleNewChat = () => {
    const id = createSession();
    setActiveSessionId(id);
    setActiveView("chat");
    setSidebarOpen(false);
  };

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
    setActiveView("chat");
    setSidebarOpen(false);
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-card border-r border-border select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-blue-400 flex items-center justify-center text-primary-foreground shadow-sm shadow-primary/20">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-foreground block">Enterprise AI</span>
            <span className="text-[10px] text-muted-foreground uppercase tracking-widest block font-mono">Agentic RAG</span>
          </div>
        </div>

        {/* Mobile close button */}
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Primary Navigation */}
      <div className="p-3">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-medium text-sm shadow-sm hover:opacity-90 active:scale-[0.99] transition-all min-h-[44px]"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>

        <nav className="mt-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors min-h-[44px] ${
                  isActive
                    ? "bg-primary/10 text-primary font-semibold"
                    : "text-muted-foreground hover:bg-muted/70 hover:text-foreground"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-primary/20 text-primary">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Session History */}
      <div className="flex-1 overflow-y-auto px-3 py-2 border-t border-border/60">
        <div className="px-2 pb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Recent Conversations
        </div>
        <div className="space-y-1">
          {sessions.map((session) => {
            const isSelected = activeSessionId === session.id && activeView === "chat";
            return (
              <div
                key={session.id}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition-colors min-h-[40px] ${
                  isSelected
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                }`}
                onClick={() => handleSelectSession(session.id)}
              >
                <span className="truncate pr-2">{session.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 hover:text-destructive text-muted-foreground transition-all"
                  title="Delete chat"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-border bg-muted/20 text-xs text-muted-foreground flex items-center justify-between">
        <div>
          <span className="block font-medium text-foreground">Cloud-Native RAG</span>
          <span className="text-[11px] font-mono text-muted-foreground">LangGraph • Qdrant • Groq</span>
        </div>
        <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono text-[10px] border border-emerald-500/20">
          v1.0.0
        </span>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden lg:block w-64 h-screen sticky top-0 shrink-0">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {isSidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 w-72 shadow-2xl z-50 animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
