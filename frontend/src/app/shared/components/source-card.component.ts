import { Component, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-source-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs transition-colors hover:border-slate-700">
      <div class="flex items-center justify-between cursor-pointer" (click)="toggleExpanded()">
        <div class="flex items-center gap-2 truncate">
          <span class="font-mono text-blue-400 font-bold">[{{ n || 1 }}]</span>
          <span class="font-medium text-slate-200 truncate max-w-[200px]">{{ title }}</span>
        </div>
        <div class="flex items-center gap-2">
          @if (score) {
            <span class="font-mono text-[10px] text-emerald-400 font-semibold">{{ (score * 100) | number:'1.0-0' }}% match</span>
          }
          <span class="text-slate-500 text-[10px]">{{ expanded() ? '▲' : '▼' }}</span>
        </div>
      </div>

      @if (expanded() && text) {
        <div class="mt-2 pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 leading-relaxed font-mono whitespace-pre-wrap max-h-32 overflow-y-auto">
          {{ text }}
        </div>
      }
    </div>
  `
})
export class SourceCardComponent {
  @Input() n: number = 1;
  @Input() title: string = '';
  @Input() score?: number;
  @Input() text?: string;

  expanded = signal(false);

  toggleExpanded(): void {
    this.expanded.update((v) => !v);
  }
}
