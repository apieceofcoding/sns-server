"use client"

import { useState } from "react"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { QuotedTweetCard } from "./quoted-tweet-card"
import { useCreateQuote } from "@/hooks/api/use-quotes"
import { cn } from "@/lib/utils"
import type { Post } from "@/lib/types"

interface QuoteDialogProps {
  post: Post
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function QuoteDialog({ post, open, onOpenChange }: QuoteDialogProps) {
  const [content, setContent] = useState("")
  const createQuote = useCreateQuote()

  const handleSubmit = async () => {
    if (!content.trim()) return

    try {
      await createQuote.mutateAsync({
        postId: post.id,
        data: { content: content.trim() },
      })
      setContent("")
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to create quote:", error)
    }
  }

  const handleClose = () => {
    setContent("")
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] p-0 gap-0 bg-background border-border">
        <DialogHeader className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full"
              onClick={handleClose}
            >
              <X className="w-5 h-5" />
            </Button>
            <DialogTitle className="sr-only">인용하기</DialogTitle>
            <Button
              className="rounded-full font-bold px-5"
              onClick={handleSubmit}
              disabled={!content.trim() || createQuote.isPending}
            >
              {createQuote.isPending ? "작성 중..." : "게시하기"}
            </Button>
          </div>
        </DialogHeader>

        <div className="p-4">
          <div className="flex gap-3">
            <div className="w-10 h-10 rounded-full bg-muted flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <Textarea
                placeholder="댓글 추가"
                className="min-h-[80px] resize-none border-none p-0 text-lg focus-visible:ring-0 placeholder:text-muted-foreground"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                autoFocus
              />
              <QuotedTweetCard post={post} />
            </div>
          </div>
        </div>

        <div className="px-4 pb-4 pt-2 border-t border-border">
          <div className="flex justify-end">
            <span className={cn(
              "text-sm",
              content.length > 280 ? "text-destructive" : "text-muted-foreground"
            )}>
              {content.length}/280
            </span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
