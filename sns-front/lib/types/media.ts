export type MediaType = 'IMAGE' | 'VIDEO' | 'GIF'
export type MediaStatus = 'INIT' | 'UPLOADED' | 'COMPLETED' | 'FAILED'

export interface Media {
  id: number
  mediaType: MediaType
  path: string
  status: MediaStatus
  userId: number
  attributes?: Record<string, unknown>
  createdAt: string
  modifiedAt: string
}

export interface MediaInitRequest {
  mediaType: MediaType
  fileSize: number
}

export interface PresignedUrlPart {
  partNumber: number
  presignedUrl: string
}

export interface MediaInitResponse {
  id: number
  mediaType: MediaType
  path: string
  status: MediaStatus
  userId: number
  presignedUrl?: string
  uploadId?: string
  presignedUrlParts?: PresignedUrlPart[]
  createdAt: string
  modifiedAt: string
}

export interface MediaUploadPart {
  partNumber: number
  eTag: string
}

export interface MediaUploadedRequest {
  mediaId: number
  parts?: MediaUploadPart[]
}

export interface MediaResponse {
  id: number
  mediaType: MediaType
  path: string
  status: MediaStatus
  userId: number
  attributes?: Record<string, unknown>
  createdAt: string
  modifiedAt: string
}

export interface PresignedUrlResponse {
  presignedUrl: string
  media: MediaResponse
}
