"use client"

import { Heart, Repeat2, User, MessageCircle } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const notifications = [
  {
    id: "1",
    type: "like",
    user: { name: "김철수", username: "kimcs" },
    content: "당신의 트윗을 좋아합니다",
    timestamp: "2시간 전",
  },
  {
    id: "2",
    type: "retweet",
    user: { name: "이영희", username: "leeyh" },
    content: "당신의 트윗을 리트윗했습니다",
    timestamp: "4시간 전",
  },
  {
    id: "3",
    type: "follow",
    user: { name: "박민수", username: "parkms" },
    content: "당신을 팔로우하기 시작했습니다",
    timestamp: "1일 전",
  },
  {
    id: "4",
    type: "reply",
    user: { name: "최지우", username: "choijw" },
    content: "당신의 트윗에 답글을 남겼습니다",
    timestamp: "2일 전",
  },
]

function getNotificationIcon(type: string) {
  switch (type) {
    case "like":
      return <Heart className="w-8 h-8 text-red-500 fill-red-500" />
    case "retweet":
      return <Repeat2 className="w-8 h-8 text-green-500" />
    case "follow":
      return <User className="w-8 h-8 text-primary" />
    case "reply":
      return <MessageCircle className="w-8 h-8 text-primary" />
    default:
      return null
  }
}

export function NotificationsFeed() {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border">
        <h1 className="text-xl font-bold p-4">알림</h1>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="w-full justify-start rounded-none border-b border-border bg-transparent h-auto p-0">
          <TabsTrigger
            value="all"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
          >
            전체
          </TabsTrigger>
          <TabsTrigger
            value="mentions"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
          >
            멘션
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-0">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className="flex gap-4 p-4 border-b border-border hover:bg-accent/50 transition-colors cursor-pointer"
            >
              <div className="flex-shrink-0 mt-1">{getNotificationIcon(notification.type)}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-8 h-8 rounded-full bg-muted" />
                </div>
                <div className="text-sm">
                  <span className="font-bold">{notification.user.name}</span>
                  <span className="text-muted-foreground ml-1">{notification.content}</span>
                </div>
                <div className="text-muted-foreground text-sm mt-1">{notification.timestamp}</div>
              </div>
            </div>
          ))}
        </TabsContent>

        <TabsContent value="mentions" className="mt-0">
          <div className="p-8 text-center text-muted-foreground">멘션이 없습니다</div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
