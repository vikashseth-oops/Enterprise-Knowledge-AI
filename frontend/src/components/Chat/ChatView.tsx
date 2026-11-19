import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useAppStore } from "../../lib/store";
import { api } from "../../lib/api";
import { ChatMessage, Citation } from "../../types";
import {
  Send,
  Square,
  Sparkles,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Clock,
  Layers,
  ArrowRight,
} from "lucide-react";

const SUGGESTED_PROMPTS = [
  "What is the home office equipment stipend amount for remote workers?",
  "How many weeks of paid parental leave does the company provide?",
  "What are the rate limits for Enterprise Tier API customers?",
  "What is the SLA response time for Sev-1 critical security incidents?",
  "What is the maximum 401(k) company matching percentage?",
];

export const ChatView: React.FC = () => {
  const {
    sessions,
    activeSessionId,
    addMessage,
    updateLastMessage,
    setSelectedCitation,
    setLatestTrace,
    setActiveView,
  } = useAppStore();

  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const activeSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];
  const messages = activeSession ? activeSession.messages : [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (overridePrompt?: string) => {
    const textToSend = overridePrompt || input;
    if (!textToSend.trim() || isGenerating) return;

    setInput("");
    const userMsgId = `msg_user_${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: textToSend.trim(),
      timestamp: new Date().toISOString(),
    };
    addMessage(activeSession.id, userMsg);

    const assistantMsgId = `msg_bot_${Date.now()}`;
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      isStreaming: true,
      citations: [],
    };
    addMessage(activeSession.id, assistantMsg);
    setIsGenerating(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let accumulatedContent = "";

    api.streamChat(
      textToSend,
      activeSession.messages,
      activeSession.id,
      {
        onToken: (token) => {
          accumulatedContent += token;
          updateLastMessage(activeSession.id, {
            content: accumulatedContent,
          });
        },
        onCitation: (citations) => {
          updateLastMessage(activeSession.id, { citations });
        },
        onTrace: (data) => {
          updateLastMessage(activeSession.id, {
            latency: data.latency,
            trace: data.trace,
          });
          setLatestTrace(data);
        },
        onDone: () => {
          updateLastMessage(activeSession.id, { isStreaming: false });
          setIsGenerating(false);
        },
        onError: (err) => {
          updateLastMessage(activeSession.id, {
            content: accumulatedContent ? accumulatedContent + `\n\n*(Error: ${err})*` : `Failed to retrieve answer: ${err}`,
            isStreaming: false,
          });
          setIsGenerating(false);
        },
      },
      controller.signal
    );
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsGenerating(false);
      updateLastMessage(activeSession.id, { isStreaming: false });
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Helper to replace [N] citation markers with interactive clickable pills
  const renderMessageContent = (content: string, citations?: Citation[]) => {
    const citationMap = new Map((citations || []).map((c) => [c.citation_id, c]));

    // Regex to split on [1], [2], etc.
    const parts = content.split(/(\[\d+\])/g);

    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const id = parseInt(match[1], 10);
        const citation = citationMap.get(id);
        return (
          <button
            key={i}
            onClick={() => citation && setSelectedCitation(citation)}
            className="inline-flex items-center justify-center px-1.5 py-0.5 mx-0.5 rounded text-[11px] font-mono font-bold bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20 transition-all cursor-pointer select-none active:scale-95"
            title={citation ? `${citation.doc_name} (Page ${citation.page_number || "N/A"})` : `Citation ${id}`}
          >
            [{id}]
          </button>
        );
      }
      return part;
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto w-full px-4 sm:px-6">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6">
        {messages.length === 0 ? (
          /* Empty State */
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-6">
            <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-lg shadow-primary/5">
              <Sparkles className="w-7 h-7" />
            </div>
            <div className="space-y-2 max-w-md">
              <h2 className="text-xl font-bold tracking-tight text-foreground">
                Enterprise Knowledge AI
              </h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Ask questions across company policies, architecture, security standards, and SOPs. Grounded strictly in retrieved vector citations.
              </p>
            </div>

            {/* Suggested Prompts */}
            <div className="w-full max-w-lg space-y-2 pt-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground text-left px-1">
                Suggested Inquiries
              </div>
              <div className="grid grid-cols-1 gap-2">
                {SUGGESTED_PROMPTS.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(prompt)}
                    className="flex items-center justify-between p-3 rounded-xl border border-border bg-card/60 hover:bg-muted/70 text-left text-xs font-medium text-foreground transition-all group"
                  >
                    <span>{prompt}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Messages List */
          messages.map((msg) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shrink-0 mt-1">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] sm:max-w-[78%] rounded-2xl px-5 py-4 space-y-3 ${
                    isUser
                      ? "bg-primary text-primary-foreground font-medium rounded-tr-sm shadow-sm"
                      : "bg-card border border-border rounded-tl-sm shadow-sm text-foreground"
                  }`}
                >
                  {/* Content */}
                  <div className="text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none">
                    {isUser ? (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>

                        {/* Streaming cursor */}
                        {msg.isStreaming && (
                          <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle" />
                        )}
                      </>
                    )}
                  </div>

                  {/* Assistant Footer Info (Citations & Latency) */}
                  {!isUser && !msg.isStreaming && (
                    <div className="pt-2 border-t border-border/50 flex flex-wrap items-center justify-between gap-3 text-[11px] text-muted-foreground">
                      {/* Citations Pill List */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="font-semibold text-foreground">Sources:</span>
                          {msg.citations.map((c) => (
                            <button
                              key={c.citation_id}
                              onClick={() => setSelectedCitation(c)}
                              className="px-2 py-0.5 rounded bg-muted hover:bg-muted/80 text-foreground font-mono font-medium border border-border transition-colors truncate max-w-[140px]"
                              title={c.doc_name}
                            >
                              [{c.citation_id}] {c.doc_name}
                            </button>
                          ))}
                        </div>
                      )}

                      {/* Execution Latency & Actions */}
                      <div className="flex items-center gap-3 ml-auto">
                        {msg.latency && (
                          <button
                            onClick={() => setActiveView("trace")}
                            className="flex items-center gap-1 hover:text-foreground font-mono transition-colors"
                            title="View LangGraph node trace"
                          >
                            <Clock className="w-3 h-3 text-primary" />
                            <span>{msg.latency.total_ms}ms</span>
                          </button>
                        )}

                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="hover:text-foreground p-1 transition-colors"
                          title="Copy message"
                        >
                          {copiedId === msg.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-500" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="py-4 border-t border-border bg-background">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center gap-2 rounded-2xl border border-border bg-card/80 p-2 shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask anything about enterprise documents, policies, or SOPs..."
            rows={1}
            disabled={isGenerating}
            className="flex-1 bg-transparent px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none resize-none max-h-32"
          />

          {isGenerating ? (
            <button
              type="button"
              onClick={handleStop}
              className="p-2.5 rounded-xl bg-destructive text-destructive-foreground hover:opacity-90 transition-all flex items-center justify-center min-w-[40px] min-h-[40px]"
              title="Stop Generation"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="p-2.5 rounded-xl bg-primary text-primary-foreground disabled:opacity-40 hover:opacity-90 active:scale-95 transition-all flex items-center justify-center min-w-[40px] min-h-[40px]"
              title="Send Prompt (Enter)"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </form>
        <div className="text-center pt-2">
          <span className="text-[11px] text-muted-foreground">
            Press <kbd className="px-1 py-0.5 bg-muted rounded border border-border font-mono text-[10px]">Enter</kbd> to send • <kbd className="px-1 py-0.5 bg-muted rounded border border-border font-mono text-[10px]">Shift+Enter</kbd> for newline
          </span>
        </div>
      </div>
    </div>
  );
};
