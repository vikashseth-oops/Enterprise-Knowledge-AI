import React from "react";
import { useAppStore } from "../../lib/store";
import { X, FileText, Bookmark, Copy, Check, ExternalLink } from "lucide-react";

export const CitationDrawer: React.FC = () => {
  const { selectedCitation, setSelectedCitation } = useAppStore();
  const [copied, setCopied] = React.useState(false);

  if (!selectedCitation) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedCitation.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-background/50 backdrop-blur-sm transition-opacity"
        onClick={() => setSelectedCitation(null)}
      />

      {/* Drawer Panel */}
      <div className="relative w-full sm:max-w-md bg-card border-l border-border h-full shadow-2xl flex flex-col z-10 animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="h-16 px-6 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded bg-primary/10 text-primary font-mono text-xs font-semibold flex items-center justify-center border border-primary/20">
              [{selectedCitation.citation_id}]
            </span>
            <span className="text-sm font-semibold text-foreground">Grounded Source Snippet</span>
          </div>
          <button
            onClick={() => setSelectedCitation(null)}
            className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            aria-label="Close Source Panel"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 flex-1 overflow-y-auto space-y-5">
          {/* Document metadata card */}
          <div className="p-4 rounded-xl border border-border bg-muted/30 space-y-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <FileText className="w-4 h-4 text-primary" />
              <span className="font-medium text-foreground truncate">{selectedCitation.doc_name}</span>
            </div>
            <div className="flex items-center gap-4 text-[11px] text-muted-foreground font-mono">
              {selectedCitation.page_number && (
                <span>Page {selectedCitation.page_number}</span>
              )}
              <span>Score: {(selectedCitation.score * 100).toFixed(1)}%</span>
              <span className="truncate">ID: {selectedCitation.chunk_id.slice(-8)}</span>
            </div>
          </div>

          {/* Highlighted text snippet */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Document Excerpt
              </span>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-2 py-1 rounded text-xs text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? "Copied" : "Copy"}</span>
              </button>
            </div>
            <div className="p-4 rounded-xl border border-border bg-card text-xs leading-relaxed text-foreground font-mono whitespace-pre-wrap">
              {selectedCitation.snippet}
            </div>
          </div>

          {/* Grounding guarantee info */}
          <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 text-xs text-muted-foreground space-y-1">
            <div className="font-semibold text-foreground flex items-center gap-1.5 text-primary">
              <Bookmark className="w-3.5 h-3.5" />
              <span>Grounded Retrieval</span>
            </div>
            <p>
              This text was retrieved from Qdrant via hybrid dense + BM25 vector search and verified by the LangGraph relevance grader.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
