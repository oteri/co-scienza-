import { useRef, useState } from 'react';
import { api } from '../lib/api';

export function useChat() {
  const [isStreaming, setIsStreaming] = useState(false);
  const sessionIdRef = useRef<string | null>(null);

  const sendMessage = async (
    message: string,
    onToken: (token: string) => void,
  ): Promise<void> => {
    setIsStreaming(true);
    try {
      const res = await fetch(api.chatUrl(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionIdRef.current }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const json = line.slice(6);
          try {
            const event = JSON.parse(json);
            if (event.type === 'session_id') {
              sessionIdRef.current = event.session_id;
            } else if (event.type === 'token') {
              onToken(event.text);
            }
          } catch {
            // ignore malformed lines
          }
        }
      }
    } finally {
      setIsStreaming(false);
    }
  };

  return { sendMessage, isStreaming };
}
