"use client"

import { useState } from "react"
import { ArrowLeft } from "lucide-react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuth } from "@/hooks/api/use-auth"
import { useUser, useUserFollowCounts, useUserPosts } from "@/hooks/api/use-users"
import { useIsFollowing, useFollow, useUnfollow } from "@/hooks/api/use-follows"
import { ProfileEditDialog } from "@/components/profile-edit-dialog"

export type UserProfileTab = "posts" | "replies" | "media" | "likes"

interface UserProfileHeaderProps {
  userId: number
  activeTab: UserProfileTab
  onTabChange: (tab: UserProfileTab) => void
}

export function UserProfileHeader({ userId, activeTab, onTabChange }: UserProfileHeaderProps) {
  const router = useRouter()
  const { user: me, isAuthenticated } = useAuth()
  const { data: user, isLoading: isUserLoading } = useUser(userId)
  const { data: followCounts } = useUserFollowCounts(userId)
  const { data: posts } = useUserPosts(userId, isAuthenticated)
  const { data: isFollowing, isLoading: isFollowingLoading } = useIsFollowing(userId, isAuthenticated && me?.id !== userId)
  const followMutation = useFollow()
  const unfollowMutation = useUnfollow()
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)

  const isMe = me?.id === userId
  const isLoading = isUserLoading || isFollowingLoading
  const isMutating = followMutation.isPending || unfollowMutation.isPending

  const postCount = posts?.length ?? 0
  const followingCount = followCounts?.followeesCount ?? 0
  const followerCount = followCounts?.followersCount ?? 0

  const handleFollowClick = () => {
    if (isFollowing) {
      unfollowMutation.mutate(userId)
    } else {
      followMutation.mutate(userId)
    }
  }

  if (isUserLoading) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        로딩 중...
      </div>
    )
  }

  if (!user) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        사용자를 찾을 수 없습니다.
      </div>
    )
  }

  return (
    <>
      <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="flex items-center gap-4 p-4">
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
            onClick={() => router.back()}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold">{user.username}</h1>
            <div className="text-sm text-muted-foreground">{postCount}개 게시물</div>
          </div>
        </div>
      </div>

      <div>
        <div className="h-48 bg-gradient-to-r from-primary/20 to-primary/40" />
        <div className="px-4">
          <div className="flex justify-between items-start -mt-16 mb-4">
            <div className="w-32 h-32 rounded-full border-4 border-background bg-muted overflow-hidden">
              {user.profileImageUrl ? (
                <img
                  src={user.profileImageUrl}
                  alt={user.username}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-4xl text-muted-foreground font-medium">
                  {user.username?.charAt(0).toUpperCase() || '?'}
                </div>
              )}
            </div>
            {isAuthenticated && !isMe && (
              <Button
                variant={isFollowing ? "outline" : "default"}
                className="mt-20 rounded-full font-bold cursor-pointer"
                onClick={handleFollowClick}
                disabled={isMutating || isLoading}
              >
                {isMutating ? "..." : isFollowing ? "팔로잉" : "팔로우"}
              </Button>
            )}
            {isMe && (
              <Button
                variant="outline"
                className="mt-20 rounded-full font-bold bg-transparent cursor-pointer"
                onClick={() => setIsEditDialogOpen(true)}
              >
                프로필 수정
              </Button>
            )}
          </div>

          <div className="mb-4">
            <h2 className="text-2xl font-bold">{user.username}</h2>
            <div className="text-muted-foreground">@{user.username}</div>
          </div>

          <div className="flex gap-6 mb-4 text-sm">
            <div>
              <span className="font-bold text-foreground">{followingCount.toLocaleString()}</span>
              <span className="text-muted-foreground ml-1">팔로잉</span>
            </div>
            <div>
              <span className="font-bold text-foreground">{followerCount.toLocaleString()}</span>
              <span className="text-muted-foreground ml-1">팔로워</span>
            </div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={(value) => onTabChange(value as UserProfileTab)} className="w-full">
          <TabsList className="w-full justify-start rounded-none border-b border-border bg-transparent h-auto p-0">
            <TabsTrigger
              value="posts"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent flex-1"
            >
              게시글
            </TabsTrigger>
            <TabsTrigger
              value="replies"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent flex-1"
            >
              답글
            </TabsTrigger>
            <TabsTrigger
              value="media"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent flex-1"
            >
              미디어
            </TabsTrigger>
            {isMe && (
              <TabsTrigger
                value="likes"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent flex-1"
              >
                마음에 들어요
              </TabsTrigger>
            )}
          </TabsList>
        </Tabs>
      </div>

      {isMe && (
        <ProfileEditDialog
          open={isEditDialogOpen}
          onOpenChange={setIsEditDialogOpen}
        />
      )}
    </>
  )
}
