import { Injectable, signal, effect } from '@angular/core';

export type ThemeMode = 'system' | 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeStore {
  readonly mode = signal<ThemeMode>(this.loadInitialTheme());

  constructor() {
    effect(() => {
      const currentMode = this.mode();
      localStorage.setItem('sc.theme', currentMode);
      this.applyTheme(currentMode);
    });

    // Listen for OS system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (this.mode() === 'system') {
        this.applyTheme('system');
      }
    });
  }

  private loadInitialTheme(): ThemeMode {
    const saved = localStorage.getItem('sc.theme') as ThemeMode;
    if (saved === 'light' || saved === 'dark' || saved === 'system') {
      return saved;
    }
    return 'dark'; // Default to modern dark console
  }

  toggleTheme(): void {
    const next: Record<ThemeMode, ThemeMode> = {
      'system': 'light',
      'light': 'dark',
      'dark': 'system'
    };
    this.mode.set(next[this.mode()]);
  }

  setTheme(mode: ThemeMode): void {
    this.mode.set(mode);
  }

  private applyTheme(mode: ThemeMode): void {
    const root = document.documentElement;
    if (mode === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else if (mode === 'light') {
      root.removeAttribute('data-theme');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        root.setAttribute('data-theme', 'dark');
      } else {
        root.removeAttribute('data-theme');
      }
    }
  }
}
