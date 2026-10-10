export interface Reply {
  id: number
  content: string
  userId: number
  username: string
  userProfileMediaId: number | null
  parentId: number
  mediaIds?: number[]
  createdAt: string
  modifiedAt: string
}

export interface ReplyCreateRequest {
  content: string
  mediaIds?: number[]
}

export interface ReplyUpdateRequest {
  content: string
}

export interface ReplyResponse {
  id: number
  content: string
  userId: number
  username: string
  parentId: number
  createdAt: string
  modifiedAt: string
}
