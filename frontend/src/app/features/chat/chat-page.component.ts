import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';

import { AuthService } from '../../core/auth.service';
import { RunStreamService } from '../../core/run-stream.service';
import { TracePanelComponent, TraceEventItem } from './trace-panel.component';
import { TicketMessage, Citation } from '../../shared/models';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [CommonModule, FormsModule, TracePanelComponent],
  template: `
    <div class="h-[calc(100vh-65px)] flex flex-col md:flex-row overflow-hidden">
      <!-- Main Chat Area -->
      <div class="flex-1 flex flex-col h-full bg-slate-900">
        <!-- Chat Header -->
        <div class="px-6 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div class="flex items-center gap-3">
            <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
            <div>
              <h2 class="text-sm font-semibold text-white">Support Copilot Chat</h2>
              <p class="text-xs text-slate-400">
                {{ currentTicketId() ? ('Ticket: ' + currentTicketId()) : 'Start a new conversation' }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              (click)="newConversation()"
              class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors border border-slate-700"
            >
              + New Ticket
            </button>
            <button
              (click)="toggleTrace()"
              class="text-xs px-3 py-1.5 rounded-lg border transition-colors flex items-center gap-1.5"
              [ngClass]="showTrace() ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-slate-800 border-slate-700 text-slate-400'"
            >
              <span>⚡ Trace</span>
              <span class="text-[10px] font-mono px-1 rounded bg-slate-800">{{ traceEvents().length }}</span>
            </button>
          </div>
        </div>

        <!-- Messages Container -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          @if (messages().length === 0) {
            <div class="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto text-slate-400">
              <div class="w-14 h-14 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center mb-4 text-2xl">
                💬
              </div>
              <h3 class="text-lg font-bold text-white mb-2">How can we assist you today?</h3>
              <p class="text-xs text-slate-400 mb-6">Ask technical troubleshooting questions, request billing refunds, or inquire about returns and warranty.</p>
              
              <div class="grid grid-cols-1 gap-2 w-full text-left">
                <button (click)="usePrompt('How do I factory reset my router?')" class="p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 text-xs text-slate-300 transition-colors">
                  🔧 "How do I factory reset my router?"
                </button>
                <button (click)="usePrompt('I was double charged for order ORD-10023. Please issue a refund.')" class="p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 text-xs text-slate-300 transition-colors">
                  💳 "I was double charged for order ORD-10023. Please issue a refund."
                </button>
                <button (click)="usePrompt('What is your return policy for hardware routers?')" class="p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 text-xs text-slate-300 transition-colors">
                  📦 "What is your return policy for hardware routers?"
                </button>
              </div>
            </div>
          }

          @for (msg of messages(); track msg.id || $index) {
            <div class="flex flex-col" [ngClass]="msg.role === 'customer' ? 'items-end' : 'items-start'">
              <div class="max-w-[80%] rounded-2xl px-4 py-3 shadow-md text-sm" [ngClass]="{
                'bg-blue-600 text-white rounded-tr-sm': msg.role === 'customer',
                'bg-slate-800 text-slate-100 border border-slate-700 rounded-tl-sm': msg.role === 'assistant',
                'bg-amber-900/40 border border-amber-600/50 text-amber-100 rounded-tl-sm': msg.role === 'human_agent'
              }">
                @if (msg.role === 'human_agent') {
                  <div class="flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-1">
                    <span>👤 Human Support Specialist</span>
                  </div>
                }

                <div class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>

                <!-- Citations List -->
                @if (msg.citations && msg.citations.length > 0) {
                  <div class="mt-3 pt-2 border-t border-slate-700/60 flex flex-wrap gap-1.5">
                    @for (c of msg.citations; track c.n) {
                      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900/80 border border-slate-700 text-[11px] text-blue-300">
                        <span class="font-mono font-bold text-blue-400">[{{ c.n }}]</span>
                        <span>{{ c.title }}</span>
                      </span>
                    }
                  </div>
                }

                <!-- Feedback Thumbs for assistant messages -->
                @if (msg.role === 'assistant' && msg.id) {
                  <div class="mt-2 pt-1 flex items-center justify-end gap-2 text-xs text-slate-400">
                    <button (click)="sendFeedback(msg.id, 1)" class="hover:text-emerald-400 p-1 transition-colors" title="Helpful">👍</button>
                    <button (click)="sendFeedback(msg.id, -1)" class="hover:text-rose-400 p-1 transition-colors" title="Not helpful">👎</button>
                  </div>
                }
              </div>
              <span class="text-[10px] text-slate-500 mt-1 px-1">{{ msg.role === 'customer' ? 'You' : (msg.role === 'human_agent' ? 'Human Agent' : 'Support Copilot') }}</span>
            </div>
          }

          <!-- Streaming Live Draft / Status Indicator -->
          @if (isProcessing()) {
            <div class="flex flex-col items-start">
              <div class="max-w-[80%] rounded-2xl rounded-tl-sm px-4 py-3 bg-slate-800/80 border border-slate-700 text-slate-200 text-sm">
                <div class="flex items-center gap-2 mb-1.5">
                  <div class="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                  <span class="text-xs font-medium text-blue-400">{{ currentStage() }}</span>
                </div>
                @if (liveTokens()) {
                  <div class="whitespace-pre-wrap leading-relaxed">{{ liveTokens() }}</div>
                }
              </div>
            </div>
          }
        </div>

        <!-- Input Box -->
        <div class="p-4 border-t border-slate-800 bg-slate-950/60">
          <form (ngSubmit)="sendMessage()" class="flex items-center gap-2">
            <input
              type="text"
              [(ngModel)]="userInput"
              name="message"
              placeholder="Ask a question or describe your issue..."
              [disabled]="isProcessing()"
              class="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm transition-colors"
            />
            <button
              type="submit"
              [disabled]="!userInput.trim() || isProcessing()"
              class="btn-primary py-3 px-5 rounded-xl text-sm font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Send</span>
              <span>➤</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Live Agent Trace Panel (Collapsible) -->
      @if (showTrace()) {
        <div class="w-full md:w-[380px] h-[350px] md:h-full border-t md:border-t-0 md:border-l border-slate-800">
          <app-trace-panel [events]="traceEvents()"></app-trace-panel>
        </div>
      }
    </div>
  `
})
export class ChatPageComponent implements OnInit, OnDestroy {
  private http = inject(HttpClient);
  private streamService = inject(RunStreamService);
  private authService = inject(AuthService);

  userInput = '';
  currentTicketId = signal<string | null>(null);
  currentRunId = signal<string | null>(null);
  messages = signal<TicketMessage[]>([]);
  traceEvents = signal<TraceEventItem[]>([]);
  isProcessing = signal(false);
  currentStage = signal('Analyzing message...');
  liveTokens = signal('');
  showTrace = signal(true);

  private streamSub?: Subscription;

  ngOnInit(): void {}

  ngOnDestroy(): void {
    this.streamSub?.unsubscribe();
  }

  toggleTrace(): void {
    this.showTrace.update((v) => !v);
  }

  usePrompt(text: string): void {
    this.userInput = text;
    this.sendMessage();
  }

  newConversation(): void {
    this.streamSub?.unsubscribe();
    this.currentTicketId.set(null);
    this.currentRunId.set(null);
    this.messages.set([]);
    this.traceEvents.set([]);
    this.isProcessing.set(false);
    this.liveTokens.set('');
  }

  sendMessage(): void {
    const text = this.userInput.trim();
    if (!text || this.isProcessing()) return;

    // Add user message to UI immediately
    const userMsg: TicketMessage = {
      id: '',
      ticket_id: this.currentTicketId() || '',
      role: 'customer',
      content: text,
      created_at: new Date().toISOString()
    };
    this.messages.update((msgs) => [...msgs, userMsg]);
    this.userInput = '';
    this.isProcessing.set(true);
    this.liveTokens.set('');
    this.currentStage.set('Running guardrails & classifier...');

    const ticketId = this.currentTicketId();
    if (ticketId) {
      // Follow-up message
      this.http.post<any>(`/api/v1/tickets/${ticketId}/messages`, { message: text }).subscribe({
        next: (res) => {
          this.currentRunId.set(res.run_id);
          this.listenToRunStream(ticketId, res.run_id);
        },
        error: (err) => {
          this.isProcessing.set(false);
          console.error(err);
        }
      });
    } else {
      // Create new ticket
      this.http.post<any>('/api/v1/tickets', { message: text }).subscribe({
        next: (res) => {
          this.currentTicketId.set(res.ticket_id);
          this.currentRunId.set(res.run_id);
          this.listenToRunStream(res.ticket_id, res.run_id);
        },
        error: (err) => {
          this.isProcessing.set(false);
          console.error(err);
        }
      });
    }
  }

  private listenToRunStream(ticketId: string, runId: string): void {
    this.streamSub?.unsubscribe();
    this.streamSub = this.streamService.connect(ticketId, runId).subscribe({
      next: (event) => {
        // Ignore transport ping events in UI trace
        if (event.event === 'ping') {
          return;
        }

        // Record trace event
        const nodeName = event.data?.node || (event.event.includes('classified') ? 'classify' : (event.event.includes('retrieved') ? 'tech_agent' : (event.event === 'token' ? 'finalize' : event.event)));
        const traceItem: TraceEventItem = {
          seq: this.traceEvents().length + 1,
          node: nodeName,
          event_type: event.event,
          payload: event.data,
          created_at: new Date().toISOString()
        };
        this.traceEvents.update((evs) => [...evs, traceItem]);

        // Handle specific stream events
        if (event.event === 'node_started') {
          this.currentStage.set(`Agent node: ${event.data.node}...`);
        } else if (event.event === 'classified') {
          this.currentStage.set(`Routed to ${event.data.category} specialist (${Math.round(event.data.confidence * 100)}% confidence)`);
        } else if (event.event === 'retrieved') {
          this.currentStage.set(`Retrieved ${event.data.chunks?.length || 0} knowledge sources. Fact-checking...`);
        } else if (event.event === 'critic_scored') {
          this.currentStage.set(`Critic score: ${Math.round(event.data.score * 100)}% (Loop ${event.data.loop})`);
        } else if (event.event === 'token') {
          this.liveTokens.update((t) => t + (event.data.text || ''));
        } else if (event.event === 'final') {
          const assistantMsg: TicketMessage = {
            id: event.data.message_id,
            ticket_id: ticketId,
            role: 'assistant',
            content: event.data.answer,
            citations: event.data.citations,
            created_at: new Date().toISOString()
          };
          this.messages.update((msgs) => [...msgs, assistantMsg]);
          this.liveTokens.set('');
          this.isProcessing.set(false);
        } else if (event.event === 'escalated') {
          const escMsg: TicketMessage = {
            id: '',
            ticket_id: ticketId,
            role: 'assistant',
            content: `Your ticket has been escalated to our human specialist team. Reason: ${event.data.reason}`,
            created_at: new Date().toISOString()
          };
          this.messages.update((msgs) => [...msgs, escMsg]);
          this.isProcessing.set(false);
        } else if (event.event === 'done' || event.event === 'error') {
          this.isProcessing.set(false);
        }
      },
      error: (err) => {
        this.isProcessing.set(false);
        console.error('SSE error:', err);
      }
    });
  }

  sendFeedback(messageId: string, rating: number): void {
    const ticketId = this.currentTicketId();
    if (!ticketId) return;
    this.http.post(`/api/v1/tickets/${ticketId}/feedback`, { message_id: messageId, rating }).subscribe({
      next: () => alert('Thank you for your feedback!')
    });
  }
}
