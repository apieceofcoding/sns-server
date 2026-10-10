import { apiClient } from './client'
import type { Post, Reply, MediaInitResponse, ProfileImageInitRequest } from '@/lib/types'

export const profileApi = {
  getMyPosts: () => {
    return apiClient.get<Post[]>('/api/v1/profile/posts')
  },

  getMyReplies: () => {
    return apiClient.get<Reply[]>('/api/v1/profile/replies')
  },

  getMyLikes: () => {
    return apiClient.get<Post[]>('/api/v1/profile/likes')
  },

  // 프로필 이미지 업로드 초기화 (presigned URL 발급)
  initProfileImage: (data: ProfileImageInitRequest) => {
    return apiClient.post<MediaInitResponse>('/api/v1/profile/image/init', data)
  },

  // 프로필 이미지 업로드 완료
  uploadedProfileImage: (mediaId: number) => {
    return apiClient.post<void>('/api/v1/profile/image/uploaded', { mediaId })
  },
}
