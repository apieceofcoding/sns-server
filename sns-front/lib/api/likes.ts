import { apiClient } from './client'
import type { Like, LikeCreateRequest, LikeResponse } from '@/lib/types'

export const likesApi = {
  getAll: () => {
    return apiClient.get<Like[]>('/api/v1/likes')
  },

  getById: (id: number) => {
    return apiClient.get<LikeResponse>(`/api/v1/likes/${id}`)
  },

  create: (data: LikeCreateRequest) => {
    return apiClient.post<LikeResponse>('/api/v1/likes', data)
  },

  delete: (id: number) => {
    return apiClient.delete<void>(`/api/v1/likes/${id}`)
  },
}
