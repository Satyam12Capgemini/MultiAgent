import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { Ticket } from '../../shared/models';

@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="max-w-6xl mx-auto p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">Support Tickets</h1>
          <p class="text-sm text-slate-400">View and track all customer support conversations and status</p>
        </div>
        <a routerLink="/chat" class="btn-primary text-sm flex items-center gap-2">
          <span>+ New Ticket</span>
        </a>
      </div>

      <!-- Filters -->
      <div class="flex items-center gap-2 pb-2 overflow-x-auto">
        <button (click)="filterStatus('')" class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors" [ngClass]="!selectedStatus() ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-800 text-slate-300 border-slate-700'">All</button>
        <button (click)="filterStatus('open')" class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors" [ngClass]="selectedStatus() === 'open' ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-800 text-slate-300 border-slate-700'">Open</button>
        <button (click)="filterStatus('answered')" class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors" [ngClass]="selectedStatus() === 'answered' ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-slate-800 text-slate-300 border-slate-700'">Answered</button>
        <button (click)="filterStatus('escalated')" class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors" [ngClass]="selectedStatus() === 'escalated' ? 'bg-amber-600 text-white border-amber-500' : 'bg-slate-800 text-slate-300 border-slate-700'">Escalated</button>
        <button (click)="filterStatus('resolved')" class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors" [ngClass]="selectedStatus() === 'resolved' ? 'bg-purple-600 text-white border-purple-500' : 'bg-slate-800 text-slate-300 border-slate-700'">Resolved</button>
      </div>

      <!-- Tickets Table -->
      <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <table class="w-full text-left text-sm text-slate-300">
          <thead class="bg-slate-950/60 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th class="px-6 py-4">Ticket</th>
              <th class="px-6 py-4">Category</th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4">Critic Score</th>
              <th class="px-6 py-4">Updated</th>
              <th class="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            @if (loading()) {
              <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">Loading tickets...</td></tr>
            } @else if (tickets().length === 0) {
              <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">No tickets found.</td></tr>
            } @else {
              @for (t of tickets(); track t.id) {
                <tr class="hover:bg-slate-800/40 transition-colors">
                  <td class="px-6 py-4 font-medium text-white">
                    <div class="truncate max-w-[280px]">{{ t.subject || 'Support Ticket' }}</div>
                    <div class="font-mono text-xs text-slate-500">{{ t.id }}</div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="badge" [ngClass]="{
                      'badge-blue': t.category === 'billing',
                      'badge-purple': t.category === 'tech',
                      'badge-green': t.category === 'general'
                    }">{{ t.category || 'TBD' }}</span>
                  </td>
                  <td class="px-6 py-4">
                    <span class="badge" [ngClass]="{
                      'badge-blue': t.status === 'open',
                      'badge-green': t.status === 'answered' || t.status === 'resolved',
                      'badge-amber': t.status === 'escalated'
                    }">{{ t.status }}</span>
                  </td>
                  <td class="px-6 py-4 font-mono text-xs">
                    @if (t.last_critic_score !== null && t.last_critic_score !== undefined) {
                      <span [ngClass]="t.last_critic_score >= 0.8 ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'">
                        {{ (t.last_critic_score * 100) | number:'1.0-0' }}%
                      </span>
                    } @else {
                      <span class="text-slate-600">—</span>
                    }
                  </td>
                  <td class="px-6 py-4 text-xs text-slate-400">{{ t.updated_at | date:'short' }}</td>
                  <td class="px-6 py-4 text-right">
                    <a [routerLink]="['/tickets', t.id]" class="text-xs font-semibold text-blue-400 hover:text-blue-300">View Trace →</a>
                  </td>
                </tr>
              }
            }
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class TicketListComponent implements OnInit {
  private http = inject(HttpClient);
  tickets = signal<Ticket[]>([]);
  loading = signal(true);
  selectedStatus = signal('');

  ngOnInit(): void {
    this.fetchTickets();
  }

  filterStatus(status: string): void {
    this.selectedStatus.set(status);
    this.fetchTickets();
  }

  fetchTickets(): void {
    this.loading.set(true);
    const params: any = {};
    if (this.selectedStatus()) {
      params.status = this.selectedStatus();
    }
    this.http.get<{ items: Ticket[] }>('/api/v1/tickets', { params }).subscribe({
      next: (res) => {
        this.tickets.set(res.items || []);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }
}
