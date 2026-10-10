"use client"

import { TweetCard } from "./tweet-card"
import { ProfileMediaGrid } from "./profile-media-grid"
import { ProfileAvatar } from "./profile-avatar"
import { useUserPosts, useUserReplies } from "@/hooks/api/use-users"
import { useMyLikes } from "@/hooks/api/use-profile"
import { useAuth } from "@/hooks/api/use-auth"
import { Loader2 } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { ko } from "date-fns/locale"
import { useRouter } from "next/navigation"
import type { UserProfileTab } from "./user-profile-header"
import type { Reply } from "@/lib/types"

interface UserProfileFeedProps {
  userId: number
  activeTab: UserProfileTab
}

function ReplyCard({ reply }: { reply: Reply }) {
  const router = useRouter()
  const formattedDate = formatDistanceToNow(new Date(reply.createdAt), {
    addSuffix: true,
    locale: ko,
  })

  const handleClick = () => {
    router.push(`/post/${reply.id}`)
  }

  return (
    <article
      onClick={handleClick}
      className="flex gap-3 p-4 border-b border-border hover:bg-accent/30 transition-colors cursor-pointer"
    >
      <ProfileAvatar
        mediaId={reply.userProfileMediaId}
        username={reply.username}
        size="md"
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 min-w-0">
          <span className="font-bold truncate">{reply.username}</span>
          <span className="text-muted-foreground truncate">
            @{reply.username} · {formattedDate}
          </span>
        </div>
        <p className="leading-relaxed">{reply.content}</p>
      </div>
    </article>
  )
}

function PostsFeed({ userId }: { userId: number }) {
  const { isAuthenticated } = useAuth()
  const { data: posts, isLoading, error } = useUserPosts(userId, isAuthenticated)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>게시물을 불러올 수 없습니다.</p>
      </div>
    )
  }

  if (!posts || posts.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>아직 작성한 게시물이 없습니다.</p>
      </div>
    )
  }

  return (
    <div>
      {posts.map((post) => (
        <TweetCard key={post.id} post={post} />
      ))}
    </div>
  )
}

function RepliesFeed({ userId }: { userId: number }) {
  const { isAuthenticated } = useAuth()
  const { data: replies, isLoading, error } = useUserReplies(userId, isAuthenticated)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>답글을 불러올 수 없습니다.</p>
      </div>
    )
  }

  if (!replies || replies.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>아직 작성한 답글이 없습니다.</p>
      </div>
    )
  }

  return (
    <div>
      {replies.map((reply) => (
        <ReplyCard key={reply.id} reply={reply} />
      ))}
    </div>
  )
}

function MediaFeed({ userId }: { userId: number }) {
  const { isAuthenticated } = useAuth()
  const { data: posts, isLoading, error } = useUserPosts(userId, isAuthenticated)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>미디어를 불러올 수 없습니다.</p>
      </div>
    )
  }

  const mediaPosts = posts?.filter(post => post.mediaIds && post.mediaIds.length > 0) ?? []

  if (mediaPosts.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>아직 미디어가 없습니다.</p>
      </div>
    )
  }

  return <ProfileMediaGrid posts={mediaPosts} />
}

function LikesFeed() {
  const { isAuthenticated } = useAuth()
  const { data: posts, isLoading, error } = useMyLikes(isAuthenticated)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>좋아요한 게시물을 불러올 수 없습니다.</p>
      </div>
    )
  }

  if (!posts || posts.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>아직 좋아요한 게시물이 없습니다.</p>
      </div>
    )
  }

  return (
    <div>
      {posts.map((post) => (
        <TweetCard key={post.id} post={post} />
      ))}
    </div>
  )
}

export function UserProfileFeed({ userId, activeTab }: UserProfileFeedProps) {
  switch (activeTab) {
    case "posts":
      return <PostsFeed userId={userId} />
    case "replies":
      return <RepliesFeed userId={userId} />
    case "media":
      return <MediaFeed userId={userId} />
    case "likes":
      return <LikesFeed />
    default:
      return <PostsFeed userId={userId} />
  }
}
