"use client"

import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"

const conversations = [
  {
    id: "1",
    user: { name: "김철수", username: "kimcs" },
    lastMessage: "네, 알겠습니다!",
    timestamp: "2시간 전",
    unread: true,
  },
  {
    id: "2",
    user: { name: "이영희", username: "leeyh" },
    lastMessage: "내일 봐요~",
    timestamp: "4시간 전",
    unread: false,
  },
  {
    id: "3",
    user: { name: "박민수", username: "parkms" },
    lastMessage: "좋은 아이디어네요",
    timestamp: "1일 전",
    unread: false,
  },
]

export function MessagesList() {
  return (
    <div className="w-full md:w-96 border-r border-border flex flex-col">
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <h1 className="text-xl font-bold p-4">쪽지</h1>
        <div className="p-4 pt-0">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input placeholder="쪽지 검색" className="pl-12 bg-muted border-none rounded-full" />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className="flex gap-3 p-4 border-b border-border hover:bg-accent/50 transition-colors cursor-pointer"
          >
            <div className="w-12 h-12 rounded-full bg-muted flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <div className="font-bold truncate">{conv.user.name}</div>
                <div className="text-muted-foreground text-sm flex-shrink-0">{conv.timestamp}</div>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className={`text-sm truncate ${
                    conv.unread ? "font-semibold text-foreground" : "text-muted-foreground"
                  }`}
                >
                  {conv.lastMessage}
                </div>
                {conv.unread && <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0" />}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
