import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login.component';
import { ChatPageComponent } from './features/chat/chat-page.component';
import { TicketListComponent } from './features/tickets/ticket-list.component';
import { TicketDetailComponent } from './features/tickets/ticket-detail.component';
import { EscalationQueueComponent } from './features/agent/escalation-queue.component';
import { EscalationDetailComponent } from './features/agent/escalation-detail.component';
import { KbManagerComponent } from './features/admin/kb-manager.component';
import { EvalDashboardComponent } from './features/admin/eval-dashboard.component';
import { AnalyticsComponent } from './features/admin/analytics.component';
import { roleGuard } from './core/role.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'chat', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'chat', component: ChatPageComponent },
  { path: 'tickets', component: TicketListComponent },
  { path: 'tickets/:id', component: TicketDetailComponent },
  {
    path: 'agent/escalations',
    component: EscalationQueueComponent,
    canActivate: [roleGuard(['agent', 'admin'])]
  },
  {
    path: 'agent/escalations/:id',
    component: EscalationDetailComponent,
    canActivate: [roleGuard(['agent', 'admin'])]
  },
  {
    path: 'admin/kb',
    component: KbManagerComponent,
    canActivate: [roleGuard(['admin'])]
  },
  {
    path: 'admin/eval',
    component: EvalDashboardComponent,
    canActivate: [roleGuard(['admin'])]
  },
  {
    path: 'admin/analytics',
    component: AnalyticsComponent,
    canActivate: [roleGuard(['admin'])]
  },
  { path: '**', redirectTo: 'chat' }
];
