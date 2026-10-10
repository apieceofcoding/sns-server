export interface Like {
  id: number
  userId: number
  username: string
  postId: number
  postContent: string
  createdAt: string
}

export interface LikeCreateRequest {
  postId: number
}

export interface LikeResponse {
  id: number
  userId: number
  username: string
  postId: number
  postContent: string
  createdAt: string
}
