import React, { useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAppStore } from "./lib/store";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { CommandPalette } from "./components/CommandPalette";
import { CitationDrawer } from "./components/Chat/CitationDrawer";
import { ChatView } from "./components/Chat/ChatView";
import { KnowledgeView } from "./components/Knowledge/KnowledgeView";
import { TraceView } from "./components/Trace/TraceView";
import { EvalView } from "./components/Eval/EvalView";
import { SettingsView } from "./components/Settings/SettingsView";

const queryClient = new QueryClient();

export const App: React.FC = () => {
  const { activeView, theme, setTheme } = useAppStore();

  useEffect(() => {
    // Initialize theme
    if (theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const renderActiveView = () => {
    switch (activeView) {
      case "chat":
        return <ChatView />;
      case "knowledge":
        return <KnowledgeView />;
      case "trace":
        return <TraceView />;
      case "eval":
        return <EvalView />;
      case "settings":
        return <SettingsView />;
      default:
        return <ChatView />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground antialiased font-sans">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto">
            {renderActiveView()}
          </main>
        </div>

        {/* Global Modals & Drawers */}
        <CitationDrawer />
        <CommandPalette />
      </div>
    </QueryClientProvider>
  );
};

export default App;
