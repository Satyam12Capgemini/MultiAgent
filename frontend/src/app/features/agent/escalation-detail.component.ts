import { Component, inject, signal, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { RouterLink, Router } from '@angular/router';

@Component({
  selector: 'app-escalation-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="max-w-5xl mx-auto p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <a routerLink="/agent/escalations" class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 text-sm">← Queue</a>
          <div>
            <h1 class="text-xl font-bold text-white">Escalation Review</h1>
            <p class="font-mono text-xs text-slate-500">ID: {{ id }}</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <span class="badge" [ngClass]="{
            'badge-amber': escalation()?.status === 'open',
            'badge-blue': escalation()?.status === 'claimed',
            'badge-green': escalation()?.status === 'resolved'
          }">{{ escalation()?.status }}</span>

          @if (escalation()?.status === 'open') {
            <button (click)="claimEscalation()" class="btn-primary text-xs py-2 px-4">Claim Escalation</button>
          }
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Context & Reply Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Summary Banner -->
          <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold uppercase text-amber-400">Escalation Trigger</span>
              <span class="font-mono text-xs text-slate-400">{{ escalation()?.created_at | date:'medium' }}</span>
            </div>
            <p class="text-sm text-slate-200">{{ escalation()?.summary }}</p>
          </div>

          <!-- Supervisor Refund Approval Card (if applicable) -->
          @if (escalation()?.context?.pending_refund) {
            <div class="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-3">
              <div class="flex items-center justify-between">
                <span class="font-bold text-amber-300 text-sm">⚠️ High-Value Refund Approval Required</span>
                <span class="badge badge-amber">Over Limit</span>
              </div>
              <p class="text-xs text-amber-200">
                Customer requested refund of <strong>₹{{ escalation()?.context?.pending_refund?.amount }}</strong> for Order <strong>{{ escalation()?.context?.pending_refund?.order_id }}</strong> (System limit: ₹{{ escalation()?.context?.pending_refund?.limit }}).
              </p>
              <div class="flex items-center gap-3 pt-2">
                <button (click)="approveRefund(escalation()?.context?.pending_refund?.refund_id, 'approve')" class="btn-primary bg-emerald-600 hover:bg-emerald-700 text-xs py-2 px-4 font-semibold">
                  ✓ Approve Refund (₹{{ escalation()?.context?.pending_refund?.amount }})
                </button>
                <button (click)="approveRefund(escalation()?.context?.pending_refund?.refund_id, 'reject')" class="btn-secondary text-xs py-2 px-4 text-red-300 hover:text-red-200">
                  ✗ Reject Refund
                </button>
              </div>
            </div>
          }

          <!-- Agent Human Reply Box -->
          <div class="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h2 class="text-sm font-semibold text-white uppercase tracking-wider">Send Human Response</h2>
            <textarea
              [(ngModel)]="replyMessage"
              rows="4"
              placeholder="Type your message to the customer..."
              class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 transition-colors"
            ></textarea>

            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input type="checkbox" [(ngModel)]="resolveTicket" class="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-0" />
                <span>Resolve ticket upon reply</span>
              </label>

              <button
                (click)="sendReply()"
                [disabled]="!replyMessage.trim()"
                class="btn-primary text-xs py-2.5 px-5 font-semibold disabled:opacity-50"
              >
                Send to Customer →
              </button>
            </div>
          </div>
        </div>

        <!-- Captured Diagnostic Context Side Panel -->
        <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 h-fit text-xs">
          <h3 class="font-bold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-2">Diagnostic Context</h3>
          
          <div>
            <span class="text-slate-400 block mb-1 font-medium">Classified Category:</span>
            <span class="badge badge-blue">{{ escalation()?.context?.category || 'General' }}</span>
          </div>

          <div>
            <span class="text-slate-400 block mb-1 font-medium">Customer Sentiment:</span>
            <span class="capitalize text-slate-200">{{ escalation()?.context?.sentiment || 'Neutral' }}</span>
          </div>

          @if (escalation()?.context?.last_draft) {
            <div>
              <span class="text-slate-400 block mb-1 font-medium">Last Assistant Draft:</span>
              <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-300 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">
                {{ escalation()?.context?.last_draft }}
              </div>
            </div>
          }

          @if (escalation()?.context?.retrieved_chunks?.length > 0) {
            <div>
              <span class="text-slate-400 block mb-1 font-medium">Retrieved KB Chunks:</span>
              <div class="space-y-1">
                @for (c of escalation()?.context?.retrieved_chunks; track c.chunk_id) {
                  <div class="p-2 rounded bg-slate-950/60 border border-slate-800 text-slate-300 text-[11px]">
                    <div class="font-semibold text-blue-400">{{ c.title }}</div>
                    <div class="truncate text-slate-500 text-[10px] mt-0.5">{{ c.text }}</div>
                  </div>
                }
              </div>
            </div>
          }
        </div>
      </div>
    </div>
  `
})
export class EscalationDetailComponent implements OnInit {
  @Input() id!: string;
  private http = inject(HttpClient);
  private router = inject(Router);

  escalation = signal<any | null>(null);
  replyMessage = '';
  resolveTicket = true;

  ngOnInit(): void {
    if (this.id) {
      this.fetchDetail();
    }
  }

  fetchDetail(): void {
    this.http.get(`/api/v1/escalations/${this.id}`).subscribe({
      next: (res) => this.escalation.set(res)
    });
  }

  claimEscalation(): void {
    this.http.post(`/api/v1/escalations/${this.id}/claim`, {}).subscribe({
      next: () => this.fetchDetail()
    });
  }

  sendReply(): void {
    if (!this.replyMessage.trim()) return;
    this.http.post(`/api/v1/escalations/${this.id}/reply`, {
      message: this.replyMessage,
      resolve: this.resolveTicket
    }).subscribe({
      next: () => {
        alert('Reply sent to customer.');
        this.router.navigate(['/agent/escalations']);
      }
    });
  }

  approveRefund(refundId: string, decision: string): void {
    this.http.post(`/api/v1/escalations/${this.id}/approve-refund`, {
      refund_id: refundId,
      decision: decision,
      note: 'Supervisor verified charge.'
    }).subscribe({
      next: () => {
        alert(`Refund decision '${decision}' executed.`);
        this.fetchDetail();
      }
    });
  }
}
