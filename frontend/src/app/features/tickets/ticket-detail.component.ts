import { Component, inject, signal, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { TracePanelComponent, TraceEventItem } from '../chat/trace-panel.component';
import { Ticket, TicketMessage } from '../../shared/models';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, TracePanelComponent],
  template: `
    <div class="max-w-6xl mx-auto p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <a routerLink="/tickets" class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 text-sm">← Back</a>
          <div>
            <h1 class="text-xl font-bold text-white">{{ ticket()?.subject || 'Ticket Detail' }}</h1>
            <p class="font-mono text-xs text-slate-500">ID: {{ id }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="badge badge-blue">{{ ticket()?.category }}</span>
          <span class="badge" [ngClass]="{
            'badge-green': ticket()?.status === 'answered' || ticket()?.status === 'resolved',
            'badge-amber': ticket()?.status === 'escalated'
          }">{{ ticket()?.status }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Conversation -->
        <div class="lg:col-span-2 glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <h2 class="text-sm font-semibold text-white uppercase tracking-wider mb-2">Conversation History</h2>
          @if (ticket()?.messages?.length === 0) {
            <p class="text-xs text-slate-500">No messages found.</p>
          }
          @for (m of ticket()?.messages; track m.id) {
            <div class="p-4 rounded-xl text-sm" [ngClass]="{
              'bg-blue-600/20 border border-blue-500/40 text-blue-100': m.role === 'customer',
              'bg-slate-900 border border-slate-800 text-slate-200': m.role === 'assistant',
              'bg-amber-900/20 border border-amber-600/40 text-amber-200': m.role === 'human_agent'
            }">
              <div class="flex items-center justify-between mb-1.5 text-xs text-slate-400">
                <span class="font-semibold capitalize text-slate-300">{{ m.role }}</span>
                <span>{{ m.created_at | date:'shortTime' }}</span>
              </div>
              <div class="whitespace-pre-wrap">{{ m.content }}</div>
            </div>
          }
        </div>

        <!-- Trace Timeline -->
        <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800 h-[600px]">
          <app-trace-panel [events]="traceEvents()"></app-trace-panel>
        </div>
      </div>
    </div>
  `
})
export class TicketDetailComponent implements OnInit {
  @Input() id!: string;
  private http = inject(HttpClient);

  ticket = signal<Ticket | null>(null);
  traceEvents = signal<TraceEventItem[]>([]);

  ngOnInit(): void {
    if (this.id) {
      this.http.get<Ticket>(`/api/v1/tickets/${this.id}`).subscribe({
        next: (t) => this.ticket.set(t)
      });
      this.http.get<{ ticket_id: string; runs: { run_id: string; events: TraceEventItem[] }[] }>(`/api/v1/tickets/${this.id}/trace`).subscribe({
        next: (res) => {
          const allEvents: TraceEventItem[] = [];
          for (const r of res.runs) {
            allEvents.push(...r.events);
          }
          this.traceEvents.set(allEvents);
        }
      });
    }
  }
}
