"use client"

import { formatDistanceToNow } from "date-fns"
import { ko } from "date-fns/locale"
import type { Post } from "@/lib/types"
import { ProfileAvatar } from "./profile-avatar"
import { MediaGallery } from "./media-gallery"

interface QuotedTweetCardProps {
  post: Post
  onClick?: () => void
}

export function QuotedTweetCard({ post, onClick }: QuotedTweetCardProps) {
  const formattedDate = formatDistanceToNow(new Date(post.createdAt), {
    addSuffix: false,
    locale: ko,
  })

  return (
    <div
      onClick={(e) => {
        e.stopPropagation()
        onClick?.()
      }}
      className="mt-3 border border-border rounded-2xl overflow-hidden hover:bg-accent/20 transition-colors cursor-pointer"
    >
      <div className="p-3">
        <div className="flex items-center gap-2 mb-1">
          <ProfileAvatar
            mediaId={post.userProfileMediaId}
            username={post.username}
            size="sm"
          />
          <span className="font-bold text-sm truncate">{post.username}</span>
          <span className="text-muted-foreground text-sm">
            @{post.username} · {formattedDate}
          </span>
        </div>
        {post.content && (
          <p className="text-sm leading-relaxed line-clamp-3">{post.content}</p>
        )}
        {post.mediaIds && post.mediaIds.length > 0 && (
          <MediaGallery mediaIds={post.mediaIds} className="mt-2" />
        )}
      </div>
    </div>
  )
}
