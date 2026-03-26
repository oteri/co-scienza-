import { useRouter } from 'expo-router';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { useSources } from '../../hooks/useSources';

export default function LibraryScreen() {
  const router = useRouter();
  const { data: sources = [], isLoading } = useSources();

  if (isLoading) return <View style={s.center}><Text>Loading...</Text></View>;

  return (
    <View style={s.container}>
      <FlatList
        data={sources}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <Pressable style={s.item} onPress={() => router.push(`/source/${item.id}`)}>
            <Text style={s.title}>{item.title ?? 'Untitled'}</Text>
            <Text style={s.meta}>{item.type} · {item.status}</Text>
          </Pressable>
        )}
        ListEmptyComponent={<Text style={s.empty}>No sources yet. Import something!</Text>}
      />
      <Pressable style={s.fab} onPress={() => router.push('/source/new')}>
        <Text style={s.fabText}>+</Text>
      </Pressable>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  item: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#e5e7eb' },
  title: { fontSize: 16, fontWeight: '500' },
  meta: { fontSize: 12, color: '#6b7280', marginTop: 2 },
  empty: { textAlign: 'center', color: '#9ca3af', marginTop: 48 },
  fab: {
    position: 'absolute', bottom: 24, right: 24,
    width: 56, height: 56, borderRadius: 28,
    backgroundColor: '#2563eb', alignItems: 'center', justifyContent: 'center',
    shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 8, elevation: 4,
  },
  fabText: { color: '#fff', fontSize: 28, lineHeight: 32 },
});
