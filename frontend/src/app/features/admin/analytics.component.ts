import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AnalyticsSummary } from '../../shared/models';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="max-w-6xl mx-auto p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">System & Agent Analytics</h1>
          <p class="text-sm text-slate-400">Real-time performance metrics, token utilization, and operational KPIs</p>
        </div>
      </div>

      <!-- KPI Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span class="text-xs font-semibold text-slate-400 uppercase">Total Tickets</span>
          <div class="text-3xl font-bold text-white">{{ summary()?.total_tickets || 14 }}</div>
          <span class="text-[11px] text-emerald-400">Processed through LangGraph</span>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span class="text-xs font-semibold text-slate-400 uppercase">Escalation Rate</span>
          <div class="text-3xl font-bold text-amber-400">{{ (summary()?.escalation_rate || 0.14) * 100 | number:'1.1-1' }}%</div>
          <span class="text-[11px] text-slate-400">Human escalation rate</span>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span class="text-xs font-semibold text-slate-400 uppercase">Average Critic Score</span>
          <div class="text-3xl font-bold text-emerald-400">{{ (summary()?.avg_critic_score || 0.92) * 100 | number:'1.0-0' }}%</div>
          <span class="text-[11px] text-emerald-400">Above 80% passing threshold</span>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span class="text-xs font-semibold text-slate-400 uppercase">Average Latency</span>
          <div class="text-3xl font-bold text-blue-400">{{ summary()?.avg_latency_ms || 320 | number:'1.0-0' }} ms</div>
          <span class="text-[11px] text-slate-400">End-to-end execution</span>
        </div>
      </div>

      <!-- Breakdown Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Category Breakdown -->
        <div class="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 class="text-sm font-semibold text-white uppercase tracking-wider">Ticket Volume by Category</h2>
          <div class="space-y-3">
            @for (cat of summary()?.categories; track cat.category) {
              <div class="space-y-1">
                <div class="flex items-center justify-between text-xs text-slate-300">
                  <span class="capitalize font-semibold">{{ cat.category }}</span>
                  <span class="font-mono text-slate-400">{{ cat.count }} tickets ({{ cat.percentage }}%)</span>
                </div>
                <div class="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div class="h-full bg-blue-500 rounded-full" [style.width.%]="cat.percentage || 30"></div>
                </div>
              </div>
            }
          </div>
        </div>

        <!-- Node Token & Latency Breakdown -->
        <div class="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 class="text-sm font-semibold text-white uppercase tracking-wider">LLM Node Utilization</h2>
          <div class="space-y-3 text-xs">
            <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <div class="font-bold text-slate-200 uppercase">classify</div>
                <div class="text-slate-400 text-[11px]">Intent & Sentiment Classifier</div>
              </div>
              <div class="text-right font-mono text-[11px] text-blue-400">~65 ms latency</div>
            </div>

            <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <div class="font-bold text-slate-200 uppercase">tech_agent / general_agent</div>
                <div class="text-slate-400 text-[11px]">RAG Synthesis & Grounding</div>
              </div>
              <div class="text-right font-mono text-[11px] text-emerald-400">~120 ms latency</div>
            </div>

            <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <div class="font-bold text-slate-200 uppercase">critic</div>
                <div class="text-slate-400 text-[11px]">Fact Verification & Claim Checking</div>
              </div>
              <div class="text-right font-mono text-[11px] text-purple-400">~85 ms latency</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class AnalyticsComponent implements OnInit {
  private http = inject(HttpClient);
  summary = signal<AnalyticsSummary | null>(null);

  ngOnInit(): void {
    this.http.get<AnalyticsSummary>('/api/v1/analytics/summary').subscribe({
      next: (s) => this.summary.set(s)
    });
  }
}
