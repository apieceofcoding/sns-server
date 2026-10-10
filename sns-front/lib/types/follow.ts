export interface Follow {
  id: number
  followerId: number
  followerUsername: string
  followeeId: number
  followeeUsername: string
  createdAt: string
}

export interface FollowRequest {
  followeeId: number
}

export interface FollowResponse {
  id: number
  followerId: number
  followerUsername: string
  followeeId: number
  followeeUsername: string
  createdAt: string
}

export interface FollowCountResponse {
  followersCount: number
  followeesCount: number
}
