import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { ThemeStore } from '../core/theme.store';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <nav class="glass-panel sticky top-0 z-50 border-b border-slate-800/80 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-6">
        <a routerLink="/chat" class="flex items-center gap-2.5 text-base font-bold tracking-tight text-white hover:text-indigo-400 transition-colors">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <span class="text-white text-base">🤖</span>
          </div>
          <span>Support <span class="text-indigo-400 font-semibold">Copilot</span></span>
        </a>

        @if (authService.isAuthenticated()) {
          <div class="hidden md:flex items-center gap-1 text-xs font-semibold uppercase tracking-wider">
            @if (userRole() === 'customer') {
              <a routerLink="/chat" routerLinkActive="bg-slate-800 text-indigo-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all">Chat & Trace</a>
              <a routerLink="/tickets" routerLinkActive="bg-slate-800 text-indigo-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all">My Tickets</a>
            }

            @if (userRole() === 'agent' || userRole() === 'admin') {
              <a routerLink="/agent/escalations" routerLinkActive="bg-slate-800 text-amber-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all flex items-center gap-1.5">
                <span>Escalations Queue</span>
                <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
              </a>
              <a routerLink="/tickets" routerLinkActive="bg-slate-800 text-indigo-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all">All Tickets</a>
            }

            @if (userRole() === 'admin') {
              <a routerLink="/admin/kb" routerLinkActive="bg-slate-800 text-indigo-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all">KB Admin</a>
              <a routerLink="/admin/eval" routerLinkActive="bg-slate-800 text-indigo-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all">Evaluation</a>
              <a routerLink="/admin/analytics" routerLinkActive="bg-slate-800 text-indigo-400" class="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all">Analytics</a>
            }
          </div>
        }
      </div>

      <div class="flex items-center gap-3">
        <!-- Theme Mode Toggle Button -->
        <button
          (click)="themeStore.toggleTheme()"
          class="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700 transition-colors flex items-center gap-1"
          title="Toggle Theme Mode (Dark/Light/System)"
        >
          <span>{{ themeIcon() }}</span>
          <span class="text-[11px] font-mono capitalize hidden sm:inline">{{ themeStore.mode() }}</span>
        </button>

        @if (authService.isAuthenticated()) {
          <div class="flex items-center gap-3">
            <div class="text-right hidden sm:block">
              <div class="text-xs font-semibold text-slate-200">{{ currentUser()?.email }}</div>
              <span class="badge" [ngClass]="{
                'badge-blue': userRole() === 'customer',
                'badge-amber': userRole() === 'agent',
                'badge-purple': userRole() === 'admin'
              }">{{ userRole() }}</span>
            </div>
            <button (click)="authService.logout()" class="text-xs text-slate-400 hover:text-red-400 px-2.5 py-1.5 rounded-lg border border-slate-700 hover:border-red-500/50 transition-colors">
              Sign Out
            </button>
          </div>
        } @else {
          <a routerLink="/login" class="btn-primary text-xs py-2 px-4">Sign In</a>
        }
      </div>
    </nav>
  `
})
export class NavbarComponent {
  authService = inject(AuthService);
  themeStore = inject(ThemeStore);

  currentUser = this.authService.currentUser;
  userRole = this.authService.userRole;

  themeIcon(): string {
    const mode = this.themeStore.mode();
    if (mode === 'light') return '☀️';
    if (mode === 'dark') return '🌙';
    return '🌓';
  }
}
