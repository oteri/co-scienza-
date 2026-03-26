import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

export const useNotes = () =>
  useQuery({ queryKey: ['notes'], queryFn: api.getNotes });

export const useNote = (id: string) =>
  useQuery({
    queryKey: ['notes', id],
    queryFn: () => api.getNote(id),
    enabled: !!id && id !== 'new',
  });

export const useUpdateNote = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: { id: string; title: string; content: string }) =>
      id === 'new'
        ? api.createNote(body)
        : api.updateNote(id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  });
};
