import { apiClient } from './client'
import type { Quote, QuoteCreateRequest } from '@/lib/types'

export const quotesApi = {
  create: (postId: number, data: QuoteCreateRequest) => {
    return apiClient.post<Quote>(`/api/v1/posts/${postId}/quotes`, data)
  },

  getAll: () => {
    return apiClient.get<Quote[]>('/api/v1/quotes')
  },

  getById: (id: number) => {
    return apiClient.get<Quote>(`/api/v1/quotes/${id}`)
  },

  delete: (id: number) => {
    return apiClient.delete<void>(`/api/v1/quotes/${id}`)
  },
}
