import React, { useState, useEffect } from "react";
import { api } from "../../lib/api";
import { DocumentMetadata, DocumentChunk } from "../../types";
import {
  UploadCloud,
  FileText,
  Trash2,
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  Eye,
  RefreshCw,
  X,
} from "lucide-react";

export const KnowledgeView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDoc, setSelectedDoc] = useState<{ doc: DocumentMetadata; chunks: DocumentChunk[] } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await api.fetchDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    try {
      setUploading(true);
      setUploadProgress(`Uploading ${files.length} file(s)...`);
      await api.uploadDocuments(Array.from(files));
      setUploadProgress("Files enqueued! Indexing in background...");
      setTimeout(() => {
        setUploadProgress(null);
        loadDocuments();
      }, 1500);
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
      setUploadProgress(null);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await api.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.doc_id !== docId));
      setDeleteTarget(null);
      if (selectedDoc?.doc.doc_id === docId) setSelectedDoc(null);
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  const handleInspect = async (doc: DocumentMetadata) => {
    try {
      const details = await api.fetchDocumentDetail(doc.doc_id);
      setSelectedDoc({ doc: details.document, chunks: details.chunks_sample });
    } catch (err) {
      console.error(err);
    }
  };

  const filteredDocs = documents.filter((d) =>
    d.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.file_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto w-full p-4 sm:p-6 space-y-6">
      {/* Upload Zone */}
      <div className="p-8 rounded-2xl border-2 border-dashed border-border bg-card/60 hover:bg-muted/40 transition-colors text-center relative">
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.txt,.md,.html,.htm,.csv"
          onChange={handleFileUpload}
          disabled={uploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              {uploading ? uploadProgress : "Upload Enterprise Documents"}
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              Drag & drop files or click to browse. Supports PDF, DOCX, TXT, MD, HTML, and CSV up to 50MB.
            </p>
          </div>
        </div>
      </div>

      {/* Document Management Header */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-semibold text-foreground">Indexed Documents</h2>
          <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-muted text-muted-foreground">
            {documents.length}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Search bar */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-border bg-card text-xs text-foreground placeholder:text-muted-foreground outline-none focus:border-primary"
            />
          </div>

          {/* Refresh button */}
          <button
            onClick={loadDocuments}
            disabled={loading}
            className="p-2 rounded-lg border border-border bg-card hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            title="Refresh documents list"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Documents Table */}
      <div className="border border-border rounded-2xl bg-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/30 text-muted-foreground font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Filename</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Size</th>
                <th className="py-3 px-4">Chunks</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-muted-foreground">
                    No documents found. Upload policies or documents above to index them into Qdrant.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr key={doc.doc_id} className="hover:bg-muted/30 transition-colors">
                    <td className="py-3 px-4 font-medium text-foreground flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary shrink-0" />
                      <span className="truncate max-w-[220px]">{doc.filename}</span>
                    </td>
                    <td className="py-3 px-4 uppercase font-mono text-[11px] text-muted-foreground">
                      {doc.file_type}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-muted-foreground">
                      {(doc.file_size_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] font-semibold text-foreground">
                      {doc.chunk_count}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider border ${
                          doc.status === "indexed"
                            ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                            : doc.status === "processing"
                            ? "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20"
                            : doc.status === "failed"
                            ? "bg-destructive/10 text-destructive border-destructive/20"
                            : "bg-muted text-muted-foreground border-border"
                        }`}
                      >
                        {doc.status === "indexed" && <CheckCircle2 className="w-3 h-3" />}
                        {doc.status === "processing" && <Clock className="w-3 h-3 animate-spin" />}
                        {doc.status === "failed" && <AlertCircle className="w-3 h-3" />}
                        {doc.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleInspect(doc)}
                          className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                          title="View chunks"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setDeleteTarget(doc.doc_id)}
                          className="p-1.5 rounded hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors"
                          title="Delete document"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" onClick={() => setDeleteTarget(null)} />
          <div className="relative w-full max-w-sm bg-card border border-border rounded-2xl p-6 shadow-2xl space-y-4 z-10">
            <h3 className="text-sm font-bold text-foreground">Confirm Deletion</h3>
            <p className="text-xs text-muted-foreground">
              Are you sure you want to delete this document and its vector embeddings from Qdrant? This action cannot be undone.
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setDeleteTarget(null)}
                className="px-3 py-1.5 rounded-lg border border-border text-xs font-medium hover:bg-muted transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteTarget)}
                className="px-3 py-1.5 rounded-lg bg-destructive text-destructive-foreground text-xs font-medium hover:opacity-90 transition-opacity"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Document Chunks Drawer */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="fixed inset-0 bg-background/50 backdrop-blur-sm" onClick={() => setSelectedDoc(null)} />
          <div className="relative w-full sm:max-w-lg bg-card border-l border-border h-full shadow-2xl flex flex-col z-10 animate-in slide-in-from-right duration-200">
            <div className="h-16 px-6 border-b border-border flex items-center justify-between">
              <div className="truncate pr-4">
                <h4 className="text-sm font-semibold text-foreground truncate">{selectedDoc.doc.filename}</h4>
                <p className="text-xs text-muted-foreground">{selectedDoc.doc.chunk_count} Total Chunks</p>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 flex-1 overflow-y-auto space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Indexed Chunks Sample
              </div>
              {selectedDoc.chunks.map((chunk, idx) => (
                <div key={idx} className="p-4 rounded-xl border border-border bg-muted/20 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground">
                    <span className="font-semibold text-primary">Chunk #{chunk.chunk_index + 1}</span>
                    {chunk.page_number && <span>Page {chunk.page_number}</span>}
                  </div>
                  <p className="text-xs text-foreground font-mono whitespace-pre-wrap leading-relaxed">
                    {chunk.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
