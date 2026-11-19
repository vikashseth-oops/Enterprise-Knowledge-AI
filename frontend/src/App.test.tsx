import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

// Mock fetch
global.fetch = vi.fn().mockImplementation((url: string) => {
  if (url.includes("/healthz")) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    });
  }
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  });
});

describe("App Root Component", () => {
  it("renders the sidebar and brand title", () => {
    render(<App />);
    expect(screen.getByText("Enterprise AI")).toBeInTheDocument();
    expect(screen.getByText("Agentic RAG")).toBeInTheDocument();
  });

  it("renders the chat workspace by default", () => {
    render(<App />);
    expect(screen.getByText("Enterprise Knowledge AI")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ask anything about enterprise documents/i)).toBeInTheDocument();
  });
});
