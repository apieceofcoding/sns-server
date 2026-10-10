export interface User {
  id: number
  username: string
  profileMediaId: number | null
  profileImageUrl: string | null
}

export interface UserSignupRequest {
  username: string
  password: string
}

export interface UserResponse {
  id: number
  username: string
  profileMediaId: number | null
  profileImageUrl: string | null
}

export interface ProfileImageInitRequest {
  fileSize: number
}
