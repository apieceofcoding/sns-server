'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { repostsApi } from '@/lib/api/reposts'
import type { Post } from '@/lib/types'

export function useReposts() {
  return useQuery({
    queryKey: ['reposts'],
    queryFn: () => repostsApi.getAll(),
  })
}

export function useRepost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (postId: number) => repostsApi.create({ postId }),
    // Optimistic update
    onMutate: async (postId) => {
      // 진행 중인 리페치 취소
      await queryClient.cancelQueries({ queryKey: ['posts'] })
      await queryClient.cancelQueries({ queryKey: ['timeline'] })

      // 이전 데이터 백업
      const previousPosts = queryClient.getQueryData(['posts'])
      const previousTimeline = queryClient.getQueryData(['timeline'])

      // 즉시 UI 업데이트 (리포스트 +1)
      const updatePost = (post: Post) => {
        if (post.id === postId) {
          return {
            ...post,
            repostCount: post.repostCount + 1,
            isRepostedByMe: true,
          }
        }
        return post
      }

      queryClient.setQueryData(['posts'], (old: Post[] | undefined) =>
        old?.map(updatePost)
      )
      queryClient.setQueryData(['timeline'], (old: Post[] | undefined) =>
        old?.map(updatePost)
      )

      return { previousPosts, previousTimeline }
    },
    onError: (error, postId, context) => {
      // 에러 시 롤백
      if (context?.previousPosts) {
        queryClient.setQueryData(['posts'], context.previousPosts)
      }
      if (context?.previousTimeline) {
        queryClient.setQueryData(['timeline'], context.previousTimeline)
      }
      toast.error('리포스트 실패')
      console.error('Repost error:', error)
    },
    onSuccess: () => {
      toast.success('리포스트했습니다!')
    },
    onSettled: () => {
      // 최종적으로 서버 데이터로 갱신
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      queryClient.invalidateQueries({ queryKey: ['timeline'] })
    },
  })
}

export function useUnrepost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (repostId: number) => repostsApi.delete(repostId),
    // Optimistic update
    onMutate: async ({ postId }: { postId: number; repostId: number }) => {
      // 진행 중인 리페치 취소
      await queryClient.cancelQueries({ queryKey: ['posts'] })
      await queryClient.cancelQueries({ queryKey: ['timeline'] })

      // 이전 데이터 백업
      const previousPosts = queryClient.getQueryData(['posts'])
      const previousTimeline = queryClient.getQueryData(['timeline'])

      // 즉시 UI 업데이트 (리포스트 -1)
      const updatePost = (post: Post) => {
        if (post.id === postId) {
          return {
            ...post,
            repostCount: Math.max(0, post.repostCount - 1),
            isRepostedByMe: false,
          }
        }
        return post
      }

      queryClient.setQueryData(['posts'], (old: Post[] | undefined) =>
        old?.map(updatePost)
      )
      queryClient.setQueryData(['timeline'], (old: Post[] | undefined) =>
        old?.map(updatePost)
      )

      return { previousPosts, previousTimeline }
    },
    onError: (error, variables, context) => {
      // 에러 시 롤백
      if (context?.previousPosts) {
        queryClient.setQueryData(['posts'], context.previousPosts)
      }
      if (context?.previousTimeline) {
        queryClient.setQueryData(['timeline'], context.previousTimeline)
      }
      toast.error('리포스트 취소 실패')
      console.error('Unrepost error:', error)
    },
    onSuccess: () => {
      toast.success('리포스트를 취소했습니다!')
    },
    onSettled: () => {
      // 최종적으로 서버 데이터로 갱신
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      queryClient.invalidateQueries({ queryKey: ['timeline'] })
    },
  })
}
