import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type PipelineStage = 'intake' | 'routing' | 'retrieval' | 'critic' | 'finalizing';

@Component({
  selector: 'app-stage-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="px-4 py-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-2 text-xs">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping"></div>
        <span class="font-medium text-slate-200">{{ message || 'Processing your request...' }}</span>
      </div>

      <div class="flex items-center gap-1.5 font-mono text-[10px] text-slate-500">
        <span [class.text-blue-400]="stage === 'intake' || stage === 'routing' || stage === 'retrieval' || stage === 'critic' || stage === 'finalizing'">Intake</span>
        <span>→</span>
        <span [class.text-blue-400]="stage === 'routing' || stage === 'retrieval' || stage === 'critic' || stage === 'finalizing'">Classify</span>
        <span>→</span>
        <span [class.text-blue-400]="stage === 'retrieval' || stage === 'critic' || stage === 'finalizing'">RAG</span>
        <span>→</span>
        <span [class.text-purple-400]="stage === 'critic' || stage === 'finalizing'">Critic</span>
        <span>→</span>
        <span [class.text-emerald-400]="stage === 'finalizing'">Answer</span>
      </div>
    </div>
  `
})
export class StageIndicatorComponent {
  @Input() stage: PipelineStage = 'routing';
  @Input() message: string = '';
}
