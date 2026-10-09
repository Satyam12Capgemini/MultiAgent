import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CriticScoreComponent } from '../../shared/components/critic-score.component';
import { SourceCardComponent } from '../../shared/components/source-card.component';

export interface TraceEventItem {
  seq: number;
  node: string;
  event_type: string;
  payload?: any;
  duration_ms?: number;
  created_at?: string;
}

@Component({
  selector: 'app-trace-panel',
  standalone: true,
  imports: [CommonModule, CriticScoreComponent, SourceCardComponent],
  template: `
    <div class="h-full flex flex-col bg-slate-950/90 border-l border-slate-800 p-4 overflow-y-auto">
      <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-white uppercase tracking-wider">Multi-Agent Trace</span>
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>
        <span class="text-xs font-mono text-slate-500">{{ events.length }} events</span>
      </div>

      @if (events.length === 0) {
        <div class="flex-1 flex flex-col items-center justify-center text-center p-6 text-slate-500">
          <div class="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mb-2">
            <span>⚡</span>
          </div>
          <p class="text-xs font-semibold text-slate-400">Trace Timeline Inactive</p>
          <p class="text-[11px] text-slate-600 mt-1">Submit a message to monitor routing, tool execution, and grounding critic passes in real time.</p>
        </div>
      } @else {
        <div class="space-y-3.5">
          @for (ev of events; track ev.seq) {
            <div class="p-3.5 rounded-xl border transition-all text-xs" [ngClass]="{
              'bg-slate-900/90 border-slate-800': ev.node !== 'critic' && ev.node !== 'escalate',
              'bg-indigo-950/30 border-indigo-500/40': ev.node === 'critic',
              'bg-amber-950/30 border-amber-500/40': ev.node === 'escalate'
            }">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-[10px] text-slate-500">#{{ ev.seq }}</span>
                  <span class="font-semibold text-slate-200 uppercase tracking-wider text-[11px]">{{ ev.node }}</span>
                  <span class="badge" [ngClass]="{
                    'badge-blue': ev.event_type === 'classified' || ev.event_type === 'retrieved',
                    'badge-green': ev.event_type === 'node_completed' || ev.event_type === 'final',
                    'badge-rose': ev.event_type === 'critic_scored',
                    'badge-amber': ev.event_type === 'escalated'
                  }">{{ ev.event_type }}</span>
                </div>
                @if (ev.duration_ms) {
                  <span class="font-mono text-[10px] text-slate-400">{{ ev.duration_ms }}ms</span>
                }
              </div>

              <!-- Guard Node Payload -->
              @if (ev.node === 'guard' && ev.payload) {
                <div class="space-y-1 mt-2 pt-2 border-t border-slate-800/80 text-slate-300">
                  <div class="flex items-center justify-between">
                    <span>PII Masked:</span>
                    <span class="font-mono text-emerald-400 font-semibold">{{ ev.payload.pii_masked?.join(', ') || 'None' }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span>Prompt Injection Scan:</span>
                    <span [class.text-red-400]="ev.payload.injection_detected" [class.text-emerald-400]="!ev.payload.injection_detected">
                      {{ ev.payload.injection_detected ? 'DETECTED ⚠️' : 'Passed ✓' }}
                    </span>
                  </div>
                </div>
              }

              <!-- Classify Node Payload -->
              @if (ev.node === 'classify' && ev.payload) {
                <div class="space-y-1.5 mt-2 pt-2 border-t border-slate-800/80 text-slate-300">
                  <div class="flex items-center justify-between">
                    <span>Routed Specialist:</span>
                    <span class="font-bold uppercase text-indigo-400">{{ ev.payload.category }} Agent</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span>Routing Confidence:</span>
                    <span class="font-mono text-emerald-400 font-semibold">{{ (ev.payload.confidence * 100) | number:'1.0-0' }}%</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span>Customer Sentiment:</span>
                    <span class="capitalize font-medium" [ngClass]="{
                      'text-red-400': ev.payload.sentiment === 'angry',
                      'text-amber-400': ev.payload.sentiment === 'negative',
                      'text-slate-400': ev.payload.sentiment === 'neutral'
                    }">{{ ev.payload.sentiment }}</span>
                  </div>
                </div>
              }

              <!-- Retrieved Knowledge Sources -->
              @if (ev.event_type === 'retrieved' && ev.payload?.chunks) {
                <div class="mt-2 pt-2 border-t border-slate-800/80 space-y-1.5">
                  <span class="text-slate-400 text-[11px] font-semibold">Grounded Context Chunks:</span>
                  @for (chunk of ev.payload.chunks; track chunk.chunk_id) {
                    <app-source-card [n]="$index + 1" [title]="chunk.title" [score]="chunk.score" [text]="chunk.text"></app-source-card>
                  }
                </div>
              }

              <!-- Grounding Critic Rubric -->
              @if (ev.node === 'critic' && ev.payload) {
                <div class="mt-2 pt-2 border-t border-indigo-800/40">
                  <app-critic-score
                    [score]="ev.payload.score"
                    [threshold]="0.8"
                    [unsupportedClaims]="ev.payload.unsupported_claims || []"
                    [feedback]="ev.payload.feedback || []"
                  ></app-critic-score>
                </div>
              }

              <!-- Escalation Node Payload -->
              @if (ev.node === 'escalate' && ev.payload) {
                <div class="mt-2 pt-2 border-t border-amber-800/40 text-amber-200">
                  <div class="font-semibold text-amber-400">Escalated to Human Specialist</div>
                  <div class="text-[11px] text-slate-300 mt-0.5"><span class="text-slate-500">Reason:</span> {{ ev.payload.reason }}</div>
                </div>
              }
            </div>
          }
        </div>
      }
    </div>
  `
})
export class TracePanelComponent {
  @Input() events: TraceEventItem[] = [];
}
