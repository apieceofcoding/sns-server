"use client"

import { useEffect, useRef, useCallback } from "react"
import { TweetComposer } from "./tweet-composer"
import { TweetCard } from "./tweet-card"
import { useTimeline } from "@/hooks/api/use-timeline"
import { Loader2 } from "lucide-react"

export function HomeFeed() {
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useTimeline(20)

  const observerRef = useRef<IntersectionObserver | null>(null)
  const loadMoreRef = useRef<HTMLDivElement>(null)

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries
      if (entry.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage()
      }
    },
    [fetchNextPage, hasNextPage, isFetchingNextPage]
  )

  useEffect(() => {
    const element = loadMoreRef.current
    if (!element) return

    observerRef.current = new IntersectionObserver(handleObserver, {
      threshold: 0.1,
    })

    observerRef.current.observe(element)

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [handleObserver])

  const posts = data?.pages.flatMap((page) => page.posts) ?? []

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border">
        <h1 className="text-xl font-bold p-4">홈</h1>
      </div>

      <TweetComposer />

      <div className="border-t border-border h-2 bg-muted/30" />

      <div>
        {isLoading && (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <div className="text-center p-8 text-muted-foreground">
            <p>타임라인을 불러올 수 없습니다.</p>
            <p className="text-sm mt-2">나중에 다시 시도해주세요.</p>
          </div>
        )}

        {!isLoading && posts.length === 0 && (
          <div className="text-center p-8 text-muted-foreground">
            <p>아직 게시물이 없습니다.</p>
            <p className="text-sm mt-2">첫 번째 게시물을 작성해보세요!</p>
          </div>
        )}

        {posts.map((post) => (
          <TweetCard key={post.id} post={post} />
        ))}

        {/* Infinite scroll trigger */}
        <div ref={loadMoreRef} className="h-10">
          {isFetchingNextPage && (
            <div className="flex items-center justify-center p-4">
              <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
