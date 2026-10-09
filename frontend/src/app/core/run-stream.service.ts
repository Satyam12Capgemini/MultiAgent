import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface StreamEvent {
  event: string;
  data: any;
}

@Injectable({
  providedIn: 'root'
})
export class RunStreamService {
  connect(ticketId: string, runId: string): Observable<StreamEvent> {
    return new Observable<StreamEvent>((observer) => {
      const url = `/api/v1/tickets/${ticketId}/runs/${runId}/stream`;
      const token = localStorage.getItem('sc_token');

      const controller = new AbortController();
      const signal = controller.signal;

      fetch(url, {
        headers: {
          'Accept': 'text/event-stream',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        signal
      })
        .then(async (response) => {
          if (!response.body) {
            observer.error(new Error('ReadableStream not supported.'));
            return;
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder('utf-8');
          let buffer = '';

          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              observer.complete();
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            let currentEvent = 'message';
            let currentData = '';

            for (let rawLine of lines) {
              const line = rawLine.replace(/\r$/, '');
              if (line.startsWith(':')) {
                // Keep-alive comment
                continue;
              }
              if (line.startsWith('event:')) {
                currentEvent = line.substring(6).trim();
              } else if (line.startsWith('data:')) {
                currentData = line.substring(5).trim();
              } else if (line === '') {
                if (currentData) {
                  try {
                    const parsed = JSON.parse(currentData);
                    observer.next({ event: currentEvent, data: parsed });
                  } catch {
                    observer.next({ event: currentEvent, data: currentData });
                  }
                  currentEvent = 'message';
                  currentData = '';
                }
              }
            }
          }
        })
        .catch((err) => {
          if (err.name !== 'AbortError') {
            observer.error(err);
          }
        });

      return () => {
        controller.abort();
      };
    });
  }
}
