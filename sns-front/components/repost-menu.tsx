"use client"

import { Repeat2, Quote } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import type { Post } from "@/lib/types"
import { useRepost, useUnrepost } from "@/hooks/api/use-reposts"

interface RepostMenuProps {
  post: Post
  onQuoteClick: () => void
  disableRepost?: boolean // 이미 재게시된 글인 경우 재게시 비활성화
  isReposted?: boolean // 이미 재게시된 글인 경우 초록색 표시
}

export function RepostMenu({ post, onQuoteClick, disableRepost = false, isReposted = false }: RepostMenuProps) {
  const repost = useRepost()
  const unrepost = useUnrepost()

  const handleRepost = () => {
    if (post.isRepostedByMe) {
      unrepost.mutate({ postId: post.id, repostId: post.repostIdByMe! })
    } else {
      repost.mutate(post.id)
    }
  }

  const isLoading = repost.isPending || unrepost.isPending

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            "text-muted-foreground hover:text-green-500 hover:bg-green-500/10 gap-2",
            (post.isRepostedByMe || isReposted) && "text-green-500"
          )}
          disabled={isLoading}
        >
          <Repeat2 className="w-5 h-5" />
          <span className="text-sm">{post.repostCount}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="center"
        className="w-48 bg-background border-border shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <DropdownMenuItem
          onClick={handleRepost}
          disabled={disableRepost && !post.isRepostedByMe}
          className={cn(
            "flex items-center gap-3 py-3 cursor-pointer focus:bg-accent",
            disableRepost && !post.isRepostedByMe && "opacity-50 cursor-not-allowed"
          )}
        >
          <Repeat2 className={cn("w-5 h-5", post.isRepostedByMe && "text-green-500")} />
          <span className="font-medium">
            {post.isRepostedByMe ? "재게시 취소" : "재게시"}
          </span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={onQuoteClick}
          className="flex items-center gap-3 py-3 cursor-pointer focus:bg-accent"
        >
          <Quote className="w-5 h-5" />
          <span className="font-medium">인용하기</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
