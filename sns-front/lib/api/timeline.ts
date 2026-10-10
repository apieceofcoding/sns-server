import { apiClient } from './client'
import type { Post } from '@/lib/types'

export interface TimelineResponse {
  posts: Post[]
  nextCursor: number | null
  hasMore: boolean
}

export const timelineApi = {
  getTimeline: (cursor?: number, limit = 20) => {
    const params = new URLSearchParams()
    if (cursor !== undefined) {
      params.append('cursor', cursor.toString())
    }
    params.append('limit', limit.toString())
    return apiClient.get<TimelineResponse>(`/api/v1/timelines?${params.toString()}`)
  },
}
