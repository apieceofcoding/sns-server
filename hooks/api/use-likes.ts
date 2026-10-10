'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { likesApi } from '@/lib/api/likes'
import type { Post } from '@/lib/types'

export function useLikes() {
  return useQuery({
    queryKey: ['likes'],
    queryFn: () => likesApi.getAll(),
  })
}

export function useLikePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (postId: number) => likesApi.create({ postId }),
    // Optimistic update
    onMutate: async (postId) => {
      // 진행 중인 리페치 취소
      await queryClient.cancelQueries({ queryKey: ['posts'] })
      await queryClient.cancelQueries({ queryKey: ['timeline'] })
      await queryClient.cancelQueries({ queryKey: ['posts', postId] })

      // 이전 데이터 백업
      const previousPosts = queryClient.getQueryData(['posts'])
      const previousTimeline = queryClient.getQueryData(['timeline'])
      const previousPost = queryClient.getQueryData(['posts', postId])

      // 즉시 UI 업데이트 (좋아요 +1)
      const updatePost = (post: Post) => {
        if (post.id === postId) {
          return {
            ...post,
            likeCount: post.likeCount + 1,
            isLikedByMe: true,
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
      // 단일 post 쿼리도 업데이트
      queryClient.setQueryData(['posts', postId], (old: Post | undefined) =>
        old ? { ...old, likeCount: old.likeCount + 1, isLikedByMe: true } : old
      )

      return { previousPosts, previousTimeline, previousPost, postId }
    },
    onSuccess: (data, postId, context) => {
      // 서버에서 받은 likeId를 캐시에 업데이트
      const updatePostWithLikeId = (post: Post) => {
        if (post.id === postId) {
          return {
            ...post,
            likeIdByMe: data.id,
          }
        }
        return post
      }

      queryClient.setQueryData(['posts'], (old: Post[] | undefined) =>
        old?.map(updatePostWithLikeId)
      )
      queryClient.setQueryData(['timeline'], (old: Post[] | undefined) =>
        old?.map(updatePostWithLikeId)
      )
      // 단일 post 쿼리도 업데이트
      queryClient.setQueryData(['posts', postId], (old: Post | undefined) =>
        old ? { ...old, likeIdByMe: data.id } : old
      )
    },
    onError: (error, postId, context) => {
      // 에러 시 롤백
      if (context?.previousPosts) {
        queryClient.setQueryData(['posts'], context.previousPosts)
      }
      if (context?.previousTimeline) {
        queryClient.setQueryData(['timeline'], context.previousTimeline)
      }
      if (context?.previousPost) {
        queryClient.setQueryData(['posts', postId], context.previousPost)
      }
      toast.error('좋아요 실패')
      console.error('Like post error:', error)
    },
    onSettled: (data, error, postId) => {
      // 최종적으로 서버 데이터로 갱신
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      queryClient.invalidateQueries({ queryKey: ['timeline'] })
      queryClient.invalidateQueries({ queryKey: ['posts', postId] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'likes'] })
    },
  })
}

export function useUnlikePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ likeId }: { postId: number; likeId: number }) => likesApi.delete(likeId),
    // Optimistic update
    onMutate: async ({ postId }: { postId: number; likeId: number }) => {
      // 진행 중인 리페치 취소
      await queryClient.cancelQueries({ queryKey: ['posts'] })
      await queryClient.cancelQueries({ queryKey: ['timeline'] })
      await queryClient.cancelQueries({ queryKey: ['posts', postId] })

      // 이전 데이터 백업
      const previousPosts = queryClient.getQueryData(['posts'])
      const previousTimeline = queryClient.getQueryData(['timeline'])
      const previousPost = queryClient.getQueryData(['posts', postId])

      // 즉시 UI 업데이트 (좋아요 -1)
      const updatePost = (post: Post) => {
        if (post.id === postId) {
          return {
            ...post,
            likeCount: Math.max(0, post.likeCount - 1),
            isLikedByMe: false,
            likeIdByMe: null,
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
      // 단일 post 쿼리도 업데이트
      queryClient.setQueryData(['posts', postId], (old: Post | undefined) =>
        old ? { ...old, likeCount: Math.max(0, old.likeCount - 1), isLikedByMe: false, likeIdByMe: null } : old
      )

      return { previousPosts, previousTimeline, previousPost, postId }
    },
    onError: (error, variables, context) => {
      // 에러 시 롤백
      if (context?.previousPosts) {
        queryClient.setQueryData(['posts'], context.previousPosts)
      }
      if (context?.previousTimeline) {
        queryClient.setQueryData(['timeline'], context.previousTimeline)
      }
      if (context?.previousPost && context?.postId) {
        queryClient.setQueryData(['posts', context.postId], context.previousPost)
      }
      toast.error('좋아요 취소 실패')
      console.error('Unlike post error:', error)
    },
    onSettled: (data, error, variables) => {
      // 최종적으로 서버 데이터로 갱신
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      queryClient.invalidateQueries({ queryKey: ['timeline'] })
      queryClient.invalidateQueries({ queryKey: ['posts', variables.postId] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'likes'] })
    },
  })
}
