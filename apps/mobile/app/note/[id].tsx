import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import Markdown from 'react-native-markdown-display';

import { useNote, useUpdateNote } from '../../hooks/useNotes';

export default function NoteScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { data: note, isLoading } = useNote(id);
  const { mutate: updateNote } = useUpdateNote();

  const [editing, setEditing] = useState(id === 'new');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    if (note) {
      setTitle(note.title ?? '');
      setContent(note.content ?? '');
    }
  }, [note]);

  const save = () => {
    updateNote({ id, title, content });
    setEditing(false);
  };

  if (isLoading && id !== 'new') {
    return <View style={s.center}><Text>Loading...</Text></View>;
  }

  return (
    <View style={s.container}>
      <View style={s.toolbar}>
        <TextInput
          style={s.titleInput}
          value={title}
          onChangeText={setTitle}
          placeholder="Note title"
        />
        <Pressable style={s.btn} onPress={() => (editing ? save() : setEditing(true))}>
          <Text style={s.btnText}>{editing ? 'Done' : 'Edit'}</Text>
        </Pressable>
      </View>

      {editing ? (
        <TextInput
          style={s.editor}
          value={content}
          onChangeText={setContent}
          multiline
          placeholder="Write in markdown..."
          autoFocus
          textAlignVertical="top"
        />
      ) : (
        <Markdown style={{ body: s.preview as any }}>{content || '*Empty note*'}</Markdown>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  toolbar: {
    flexDirection: 'row', alignItems: 'center', padding: 12,
    borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#e5e7eb', gap: 8,
  },
  titleInput: { flex: 1, fontSize: 18, fontWeight: '600' },
  btn: {
    paddingHorizontal: 14, paddingVertical: 6,
    backgroundColor: '#2563eb', borderRadius: 8,
  },
  btnText: { color: '#fff', fontWeight: '600' },
  editor: {
    flex: 1, padding: 16, fontSize: 15, fontFamily: 'monospace',
    lineHeight: 22,
  },
  preview: { flex: 1, padding: 16, fontSize: 15 },
});
