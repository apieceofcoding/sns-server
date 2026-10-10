import { apiClient } from './client'
import type { Repost, RepostCreateRequest, RepostResponse } from '@/lib/types'

export const repostsApi = {
  getAll: () => {
    return apiClient.get<Repost[]>('/api/v1/reposts')
  },

  getById: (id: number) => {
    return apiClient.get<RepostResponse>(`/api/v1/reposts/${id}`)
  },

  create: (data: RepostCreateRequest) => {
    return apiClient.post<RepostResponse>('/api/v1/reposts', data)
  },

  delete: (id: number) => {
    return apiClient.delete<void>(`/api/v1/reposts/${id}`)
  },
}
