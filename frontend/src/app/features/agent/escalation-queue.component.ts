import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { Escalation } from '../../shared/models';

@Component({
  selector: 'app-escalation-queue',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="max-w-6xl mx-auto p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-white tracking-tight">Human Escalation Queue</h1>
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
          </div>
          <p class="text-sm text-slate-400">Tickets requiring human intervention, angry sentiment handling, or supervisor approval</p>
        </div>
      </div>

      <!-- Escalations Table -->
      <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <table class="w-full text-left text-sm text-slate-300">
          <thead class="bg-slate-950/60 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th class="px-6 py-4">Ticket / Reason</th>
              <th class="px-6 py-4">Summary</th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4">Claimed By</th>
              <th class="px-6 py-4">Created</th>
              <th class="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            @if (loading()) {
              <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">Loading escalation queue...</td></tr>
            } @else if (escalations().length === 0) {
              <tr><td colspan="6" class="px-6 py-8 text-center text-emerald-400 font-medium">All caught up! No open escalations in queue.</td></tr>
            } @else {
              @for (e of escalations(); track e.id) {
                <tr class="hover:bg-slate-800/40 transition-colors">
                  <td class="px-6 py-4 font-medium text-white">
                    <div class="font-semibold text-amber-400 uppercase text-xs tracking-wider">{{ e.reason }}</div>
                    <div class="font-mono text-xs text-slate-500">Ticket: {{ e.ticket_id }}</div>
                  </td>
                  <td class="px-6 py-4 text-xs text-slate-300 max-w-[280px] truncate">
                    {{ e.summary || 'Human assistance requested.' }}
                  </td>
                  <td class="px-6 py-4">
                    <span class="badge" [ngClass]="{
                      'badge-amber': e.status === 'open',
                      'badge-blue': e.status === 'claimed',
                      'badge-green': e.status === 'resolved'
                    }">{{ e.status }}</span>
                  </td>
                  <td class="px-6 py-4 text-xs text-slate-400">
                    {{ e.claimed_by || 'Unassigned' }}
                  </td>
                  <td class="px-6 py-4 text-xs text-slate-400">{{ e.created_at | date:'short' }}</td>
                  <td class="px-6 py-4 text-right">
                    <a [routerLink]="['/agent/escalations', e.id]" class="btn-primary text-xs py-1.5 px-3">
                      Review & Resolve →
                    </a>
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
export class EscalationQueueComponent implements OnInit {
  private http = inject(HttpClient);
  escalations = signal<Escalation[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.fetchQueue();
  }

  fetchQueue(): void {
    this.loading.set(true);
    this.http.get<Escalation[]>('/api/v1/escalations').subscribe({
      next: (items) => {
        this.escalations.set(items || []);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }
}
