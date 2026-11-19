import React, { useState } from "react";
import { useAppStore, ThemeMode } from "../../lib/store";
import { Settings as SettingsIcon, Save, RotateCcw, Check, Shield, Cpu, Sliders } from "lucide-react";

export const SettingsView: React.FC = () => {
  const { theme, setTheme } = useAppStore();

  const [apiUrl, setApiUrl] = useState(
    localStorage.getItem("ekai_api_url") || import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
  );
  const [apiKey, setApiKey] = useState(
    localStorage.getItem("ekai_api_key") || import.meta.env.VITE_API_KEY || "ekai_test_secret_key_12345"
  );
  const [genModel, setGenModel] = useState("llama-3.3-70b-versatile");
  const [fastModel, setFastModel] = useState("llama-3.1-8b-instant");
  const [topK, setTopK] = useState(5);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem("ekai_api_url", apiUrl);
    localStorage.setItem("ekai_api_key", apiKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    localStorage.removeItem("ekai_api_url");
    localStorage.removeItem("ekai_api_key");
    setApiUrl("http://localhost:8000");
    setApiKey("ekai_test_secret_key_12345");
    setGenModel("llama-3.3-70b-versatile");
    setFastModel("llama-3.1-8b-instant");
    setTopK(5);
  };

  return (
    <div className="max-w-3xl mx-auto w-full p-4 sm:p-6 space-y-6">
      <div className="p-6 rounded-2xl border border-border bg-card space-y-6">
        <div>
          <h2 className="text-base font-bold text-foreground flex items-center gap-2">
            <SettingsIcon className="w-4 h-4 text-primary" />
            <span>Platform Configuration</span>
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Manage your API gateway credentials, Groq model architectures, and retrieval hyperparameters.
          </p>
        </div>

        {/* API Gateway Settings */}
        <div className="space-y-4 pt-2 border-t border-border">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Shield className="w-3.5 h-3.5 text-primary" />
            <span>API Gateway & Security</span>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1">Backend API Base URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
                className="w-full px-3 py-2 rounded-xl border border-border bg-muted/30 text-xs font-mono text-foreground outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-foreground mb-1">X-API-Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Secret API key"
                className="w-full px-3 py-2 rounded-xl border border-border bg-muted/30 text-xs font-mono text-foreground outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Model Selection */}
        <div className="space-y-4 pt-2 border-t border-border">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Cpu className="w-3.5 h-3.5 text-primary" />
            <span>LLM Architecture (Groq API)</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1">Generation Model (70B)</label>
              <select
                value={genModel}
                onChange={(e) => setGenModel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-muted/30 text-xs text-foreground outline-none focus:border-primary"
              >
                <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile (Default)</option>
                <option value="llama-3.1-70b-versatile">llama-3.1-70b-versatile</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-foreground mb-1">Routing & Grading Model (8B)</label>
              <select
                value={fastModel}
                onChange={(e) => setFastModel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-muted/30 text-xs text-foreground outline-none focus:border-primary"
              >
                <option value="llama-3.1-8b-instant">llama-3.1-8b-instant (Fast)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Hyperparameters */}
        <div className="space-y-4 pt-2 border-t border-border">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Sliders className="w-3.5 h-3.5 text-primary" />
            <span>Retrieval Hyperparameters</span>
          </div>

          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="font-medium text-foreground">Top-K Retrieved Chunks</span>
              <span className="font-mono font-bold text-primary">{topK}</span>
            </div>
            <input
              type="range"
              min="1"
              max="20"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value, 10))}
              className="w-full accent-primary cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
              <span>1</span>
              <span>Default (5)</span>
              <span>20</span>
            </div>
          </div>
        </div>

        {/* Theme Settings */}
        <div className="space-y-3 pt-2 border-t border-border">
          <label className="block text-xs font-medium text-foreground">Appearance Theme</label>
          <div className="flex gap-2">
            {(["dark", "light", "system"] as ThemeMode[]).map((t) => (
              <button
                key={t}
                onClick={() => setTheme(t)}
                className={`px-4 py-2 rounded-xl text-xs font-medium capitalize border transition-colors ${
                  theme === t
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-border bg-muted/40 text-muted-foreground hover:text-foreground"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors min-h-[44px]"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-primary text-primary-foreground text-xs font-semibold hover:opacity-90 active:scale-95 transition-all min-h-[44px]"
          >
            {saved ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
            <span>{saved ? "Saved Successfully" : "Save Changes"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
