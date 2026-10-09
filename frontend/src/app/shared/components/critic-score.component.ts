import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-critic-score',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
      <div class="flex items-center justify-between text-xs">
        <span class="font-semibold text-slate-300">Grounding Critic Rubric</span>
        <span class="font-mono font-bold" [ngClass]="score >= threshold ? 'text-emerald-400' : 'text-amber-400'">
          {{ (score * 100) | number:'1.0-0' }}%
          <span class="text-[10px] font-normal text-slate-500">({{ score >= threshold ? 'Passed' : 'Needs Correction' }})</span>
        </span>
      </div>

      <!-- Score Bar with Threshold Marker at 80% -->
      <div class="relative w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
        <!-- Passing threshold line -->
        <div class="absolute top-0 bottom-0 w-0.5 bg-white/40 z-10" [style.left.%]="threshold * 100" title="Pass threshold (80%)"></div>
        
        <!-- Progress fill -->
        <div class="h-full rounded-full transition-all duration-500" [ngClass]="score >= threshold ? 'bg-emerald-500' : 'bg-amber-500'" [style.width.%]="score * 100"></div>
      </div>

      <div class="flex items-center justify-between text-[10px] text-slate-500 font-mono">
        <span>0%</span>
        <span>Pass Threshold: {{ (threshold * 100) | number:'1.0-0' }}%</span>
        <span>100%</span>
      </div>

      <!-- Unsupported Claims Warning -->
      @if (unsupportedClaims.length > 0) {
        <div class="mt-2 pt-2 border-t border-slate-800/80 text-[11px] text-amber-300 space-y-1">
          <div class="font-semibold text-amber-400 flex items-center gap-1">
            <span>⚠️ Claims requiring verification:</span>
          </div>
          <ul class="list-disc list-inside space-y-0.5 text-slate-300">
            @for (c of unsupportedClaims; track c) {
              <li>{{ c }}</li>
            }
          </ul>
        </div>
      }

      <!-- Actionable Feedback -->
      @if (feedback.length > 0) {
        <div class="mt-2 pt-2 border-t border-slate-800/80 text-[11px] space-y-1">
          <div class="font-semibold text-indigo-300">Critic Corrections Feedback:</div>
          <div class="space-y-1">
            @for (f of feedback; track f) {
              <div class="p-1.5 rounded bg-indigo-950/40 border border-indigo-500/30 text-indigo-200">
                • {{ f }}
              </div>
            }
          </div>
        </div>
      }
    </div>
  `
})
export class CriticScoreComponent {
  @Input() score: number = 1.0;
  @Input() threshold: number = 0.8;
  @Input() unsupportedClaims: string[] = [];
  @Input() feedback: string[] = [];
}
