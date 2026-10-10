export interface Repost {
  id: number
  userId: number
  username: string
  repostId: number
  createdAt: string
}

export interface RepostCreateRequest {
  postId: number
}

export interface RepostResponse {
  id: number
  userId: number
  username: string
  repostId: number
  createdAt: string
}
