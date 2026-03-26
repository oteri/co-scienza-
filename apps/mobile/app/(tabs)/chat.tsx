import { useRef, useState } from 'react';
import {
  FlatList, KeyboardAvoidingView, Platform,
  Pressable, StyleSheet, Text, TextInput, View,
} from 'react-native';
import Markdown from 'react-native-markdown-display';

import { useChat } from '../../hooks/useChat';

type Message = { role: 'user' | 'assistant'; text: string };

export default function ChatScreen() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const { sendMessage, isStreaming } = useChat();
  const listRef = useRef<FlatList>(null);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text }]);
    const reply = await sendMessage(text, (token) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === 'assistant') {
          return [...prev.slice(0, -1), { role: 'assistant', text: last.text + token }];
        }
        return [...prev, { role: 'assistant', text: token }];
      });
    });
    listRef.current?.scrollToEnd({ animated: true });
  };

  return (
    <KeyboardAvoidingView
      style={s.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={88}
    >
      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={s.messages}
        renderItem={({ item }) => (
          <View style={[s.bubble, item.role === 'user' ? s.userBubble : s.assistantBubble]}>
            {item.role === 'assistant' ? (
              <Markdown style={{ body: s.assistantText }}>{item.text}</Markdown>
            ) : (
              <Text style={s.userText}>{item.text}</Text>
            )}
          </View>
        )}
        ListEmptyComponent={
          <Text style={s.empty}>Ask anything about your library.</Text>
        }
      />
      <View style={s.inputRow}>
        <TextInput
          style={s.input}
          value={input}
          onChangeText={setInput}
          placeholder="Ask your library..."
          multiline
          returnKeyType="send"
          onSubmitEditing={handleSend}
        />
        <Pressable
          style={[s.sendBtn, (!input.trim() || isStreaming) && s.sendBtnDisabled]}
          onPress={handleSend}
          disabled={!input.trim() || isStreaming}
        >
          <Text style={s.sendText}>↑</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  messages: { padding: 16, paddingBottom: 8 },
  bubble: { marginBottom: 12, maxWidth: '85%', borderRadius: 16, padding: 12 },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#2563eb' },
  assistantBubble: { alignSelf: 'flex-start', backgroundColor: '#f3f4f6' },
  userText: { color: '#fff', fontSize: 15 },
  assistantText: { fontSize: 15 } as any,
  empty: { textAlign: 'center', color: '#9ca3af', marginTop: 48 },
  inputRow: {
    flexDirection: 'row', padding: 12, borderTopWidth: StyleSheet.hairlineWidth,
    borderColor: '#e5e7eb', alignItems: 'flex-end', gap: 8,
  },
  input: {
    flex: 1, minHeight: 40, maxHeight: 120, borderRadius: 20,
    borderWidth: 1, borderColor: '#d1d5db', paddingHorizontal: 14,
    paddingVertical: 10, fontSize: 15, backgroundColor: '#f9fafb',
  },
  sendBtn: {
    width: 40, height: 40, borderRadius: 20,
    backgroundColor: '#2563eb', alignItems: 'center', justifyContent: 'center',
  },
  sendBtnDisabled: { backgroundColor: '#93c5fd' },
  sendText: { color: '#fff', fontSize: 18, fontWeight: '600' },
});
