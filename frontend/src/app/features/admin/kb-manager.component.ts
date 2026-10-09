import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { KBDocument } from '../../shared/models';

@Component({
  selector: 'app-kb-manager',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="max-w-6xl mx-auto p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">Knowledge Base Management</h1>
          <p class="text-sm text-slate-400">Manage documents, chunks, vectors in ChromaDB, and run search diagnostics</p>
        </div>
        <button (click)="reconcileStores()" class="btn-secondary text-xs flex items-center gap-1.5">
          <span>🔄 Sync Check</span>
        </button>
      </div>

      <!-- Upload Section -->
      <div class="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h2 class="text-sm font-semibold text-white uppercase tracking-wider">Upload New Knowledge Document</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs text-slate-400 mb-1">Document Title</label>
            <input type="text" [(ngModel)]="newDocTitle" placeholder="e.g. Wi-Fi Router Setup Manual" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1">Category</label>
            <select [(ngModel)]="newDocCategory" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white">
              <option value="tech">Technical Support</option>
              <option value="general">FAQ / Policies</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1">File (PDF, Markdown, HTML, TXT)</label>
            <input type="file" (change)="onFileSelected($event)" class="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-blue-400 hover:file:bg-slate-700" />
          </div>
        </div>
        <button (click)="uploadDoc()" [disabled]="!selectedFile || !newDocTitle.trim() || uploading()" class="btn-primary text-xs py-2.5 px-5 font-semibold disabled:opacity-50">
          {{ uploading() ? 'Ingesting Chunks & Generating Vectors...' : 'Upload & Ingest to Vector DB' }}
        </button>
      </div>

      <!-- Documents Registry Table -->
      <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between">
          <span class="text-xs font-semibold uppercase text-slate-400">Indexed Knowledge Documents</span>
          <span class="text-xs text-slate-500">{{ documents().length }} documents</span>
        </div>
        <table class="w-full text-left text-sm text-slate-300">
          <thead class="bg-slate-950/60 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th class="px-6 py-3.5">Title</th>
              <th class="px-6 py-3.5">Category</th>
              <th class="px-6 py-3.5">Chunks</th>
              <th class="px-6 py-3.5">Status</th>
              <th class="px-6 py-3.5">Indexed Date</th>
              <th class="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            @for (doc of documents(); track doc.id) {
              <tr class="hover:bg-slate-800/40 transition-colors">
                <td class="px-6 py-4 font-medium text-white">
                  <div>{{ doc.title }}</div>
                  <div class="font-mono text-xs text-slate-500">{{ doc.source }}</div>
                </td>
                <td class="px-6 py-4">
                  <span class="badge" [ngClass]="doc.category === 'tech' ? 'badge-purple' : 'badge-green'">{{ doc.category }}</span>
                </td>
                <td class="px-6 py-4 font-mono text-xs">{{ doc.chunk_count }}</td>
                <td class="px-6 py-4">
                  <span class="badge badge-green">{{ doc.status }}</span>
                </td>
                <td class="px-6 py-4 text-xs text-slate-400">{{ doc.created_at | date:'short' }}</td>
                <td class="px-6 py-4 text-right">
                  <button (click)="deleteDoc(doc.id)" class="text-xs text-red-400 hover:text-red-300 transition-colors">Delete</button>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class KbManagerComponent implements OnInit {
  private http = inject(HttpClient);

  documents = signal<KBDocument[]>([]);
  newDocTitle = '';
  newDocCategory = 'tech';
  selectedFile: File | null = null;
  uploading = signal(false);

  ngOnInit(): void {
    this.fetchDocs();
  }

  fetchDocs(): void {
    this.http.get<KBDocument[]>('/api/v1/kb/documents').subscribe({
      next: (docs) => this.documents.set(docs || [])
    });
  }

  onFileSelected(event: any): void {
    if (event.target.files && event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
      if (!this.newDocTitle) {
        this.newDocTitle = this.selectedFile?.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ") || '';
      }
    }
  }

  uploadDoc(): void {
    if (!this.selectedFile || !this.newDocTitle.trim()) return;
    this.uploading.set(true);

    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('title', this.newDocTitle);
    formData.append('category', this.newDocCategory);

    this.http.post('/api/v1/kb/documents', formData).subscribe({
      next: () => {
        this.uploading.set(false);
        this.newDocTitle = '';
        this.selectedFile = null;
        this.fetchDocs();
      },
      error: (err) => {
        this.uploading.set(false);
        alert(err.error?.error?.message || 'Upload failed');
      }
    });
  }

  deleteDoc(id: string): void {
    if (!confirm('Are you sure you want to delete this document from MSSQL and ChromaDB?')) return;
    this.http.delete(`/api/v1/kb/documents/${id}`).subscribe({
      next: () => this.fetchDocs()
    });
  }

  reconcileStores(): void {
    this.http.post<any>('/api/v1/kb/reconcile', {}).subscribe({
      next: (res) => {
        alert(`Storage Sync Check:\nMSSQL Chunks: ${res.mssql_chunks_count}\nChromaDB Vectors: ${res.chroma_vectors_count}\nSynchronized: ${res.in_sync ? 'YES ✅' : 'NO ⚠️'}`);
      }
    });
  }
}
