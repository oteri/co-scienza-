import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, SourceCreate } from '../lib/api';

export const useSources = () =>
  useQuery({ queryKey: ['sources'], queryFn: api.getSources });

export const useSource = (id: string) =>
  useQuery({ queryKey: ['sources', id], queryFn: () => api.getSource(id), enabled: !!id });

export const useCreateSource = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: SourceCreate) => api.createSource(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  });
};

export const useDeleteSource = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteSource(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  });
};
