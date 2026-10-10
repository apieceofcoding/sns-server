import { apiClient } from './client'
import type { Follow, FollowRequest, FollowResponse, FollowCountResponse } from '@/lib/types'

export const followsApi = {
  follow: (data: FollowRequest) => {
    return apiClient.post<FollowResponse>('/api/v1/follows', data)
  },

  unfollow: (data: FollowRequest) => {
    return apiClient.delete<void>('/api/v1/follows', { body: JSON.stringify(data) })
  },

  getFollowers: () => {
    return apiClient.get<Follow[]>('/api/v1/follows/followers')
  },

  getFollowees: () => {
    return apiClient.get<Follow[]>('/api/v1/follows/followees')
  },

  getFollowCounts: () => {
    return apiClient.get<FollowCountResponse>('/api/v1/follow_counts')
  },

  isFollowing: (followeeId: number) => {
    return apiClient.get<boolean>(`/api/v1/follows/check/${followeeId}`)
  },
}
