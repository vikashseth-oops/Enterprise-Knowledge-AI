import React, { useState, useEffect } from "react";
import { useAppStore, ViewType } from "../lib/store";
import {
  MessageSquare,
  FileText,
  GitBranch,
  BarChart3,
  Settings,
  Plus,
  Sun,
  Moon,
  Search,
} from "lucide-react";

export const CommandPalette: React.FC = () => {
  const {
    isCommandPaletteOpen,
    setCommandPaletteOpen,
    setActiveView,
    createSession,
    setActiveSessionId,
    theme,
    setTheme,
  } = useAppStore();

  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      }
      if (e.key === "Escape" && isCommandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  const actions = [
    {
      id: "new-chat",
      label: "Start New Chat",
      icon: Plus,
      category: "Chat",
      run: () => {
        const id = createSession();
        setActiveSessionId(id);
        setActiveView("chat");
      },
    },
    {
      id: "view-chat",
      label: "Go to Chat Workspace",
      icon: MessageSquare,
      category: "Navigation",
      run: () => setActiveView("chat"),
    },
    {
      id: "view-knowledge",
      label: "Manage Documents & Ingestion",
      icon: FileText,
      category: "Navigation",
      run: () => setActiveView("knowledge"),
    },
    {
      id: "view-trace",
      label: "Open Agent Trace Timeline",
      icon: GitBranch,
      category: "Navigation",
      run: () => setActiveView("trace"),
    },
    {
      id: "view-eval",
      label: "View Retrieval & Model Evals",
      icon: BarChart3,
      category: "Navigation",
      run: () => setActiveView("eval"),
    },
    {
      id: "view-settings",
      label: "Open System Settings",
      icon: Settings,
      category: "Navigation",
      run: () => setActiveView("settings"),
    },
    {
      id: "toggle-theme",
      label: `Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`,
      icon: theme === "dark" ? Sun : Moon,
      category: "Appearance",
      run: () => setTheme(theme === "dark" ? "light" : "dark"),
    },
  ];

  const filtered = actions.filter((a) =>
    a.label.toLowerCase().includes(query.toLowerCase()) ||
    a.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (idx: number) => {
    if (filtered[idx]) {
      filtered[idx].run();
      setCommandPaletteOpen(false);
      setQuery("");
    }
  };

  if (!isCommandPaletteOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
        onClick={() => setCommandPaletteOpen(false)}
      />

      {/* Palette Modal */}
      <div className="relative w-full max-w-lg bg-card border border-border shadow-2xl rounded-2xl overflow-hidden z-10 animate-in fade-in-0 zoom-in-95 duration-150">
        <div className="flex items-center px-4 border-b border-border">
          <Search className="w-4 h-4 text-muted-foreground mr-3" />
          <input
            type="text"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setSelectedIndex((prev) => (prev + 1) % filtered.length);
              } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setSelectedIndex((prev) => (prev - 1 + filtered.length) % filtered.length);
              } else if (e.key === "Enter") {
                e.preventDefault();
                handleSelect(selectedIndex);
              }
            }}
            autoFocus
            className="w-full h-12 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
          />
          <kbd className="px-2 py-0.5 rounded bg-muted border border-border text-[10px] text-muted-foreground font-mono">
            ESC
          </kbd>
        </div>

        <div className="max-h-72 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="p-4 text-center text-xs text-muted-foreground">
              No matching commands or actions found.
            </div>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={() => handleSelect(idx)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs cursor-pointer transition-colors ${
                    isSelected ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground hover:bg-muted/50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-primary" />
                    <span className="text-foreground">{item.label}</span>
                  </div>
                  <span className="text-[10px] uppercase font-mono text-muted-foreground px-1.5 py-0.5 rounded bg-muted">
                    {item.category}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
