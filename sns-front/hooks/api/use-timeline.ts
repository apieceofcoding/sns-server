'use client'

import { useInfiniteQuery } from '@tanstack/react-query'
import { timelineApi, type Feed } from '@/lib/api/timeline'

export function useTimeline(limit = 20, feed: Feed = 'timelines') {
  return useInfiniteQuery({
    queryKey: ['timeline', feed, limit],
    queryFn: ({ pageParam }) => timelineApi.getTimeline(pageParam, limit, feed),
    initialPageParam: undefined as number | string | undefined,
    getNextPageParam: (lastPage) => {
      if (!lastPage.hasMore || lastPage.nextCursor === null) {
        return undefined
      }
      return lastPage.nextCursor
    },
  })
}
