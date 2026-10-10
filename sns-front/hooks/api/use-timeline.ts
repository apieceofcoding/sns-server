'use client'

import { useInfiniteQuery } from '@tanstack/react-query'
import { timelineApi } from '@/lib/api/timeline'

export function useTimeline(limit = 20) {
  return useInfiniteQuery({
    queryKey: ['timeline', limit],
    queryFn: ({ pageParam }) => timelineApi.getTimeline(pageParam, limit),
    initialPageParam: undefined as number | undefined,
    getNextPageParam: (lastPage) => {
      if (!lastPage.hasMore || lastPage.nextCursor === null) {
        return undefined
      }
      return lastPage.nextCursor
    },
  })
}
