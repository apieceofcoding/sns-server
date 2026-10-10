"use client"

import { Send, ImageIcon, Smile } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

const messages = [
  { id: "1", content: "안녕하세요!", sender: "other", timestamp: "오후 2:30" },
  { id: "2", content: "안녕하세요! 무엇을 도와드릴까요?", sender: "me", timestamp: "오후 2:31" },
  { id: "3", content: "프로젝트에 대해 논의하고 싶습니다", sender: "other", timestamp: "오후 2:32" },
  { id: "4", content: "네, 알겠습니다!", sender: "me", timestamp: "오후 2:33" },
]

export function ChatWindow() {
  return (
    <div className="hidden md:flex flex-1 flex-col">
      <div className="sticky top-0 z-10 bg-background border-b border-border p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-muted" />
          <div>
            <div className="font-bold">김철수</div>
            <div className="text-sm text-muted-foreground">@kimcs</div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === "me" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-sm rounded-2xl px-4 py-2 ${
                message.sender === "me" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
              }`}
            >
              <div>{message.content}</div>
              <div
                className={`text-xs mt-1 ${
                  message.sender === "me" ? "text-primary-foreground/70" : "text-muted-foreground"
                }`}
              >
                {message.timestamp}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-border p-4">
        <div className="flex items-end gap-2">
          <div className="flex-1 relative">
            <Textarea placeholder="메시지 보내기" className="min-h-[48px] resize-none pr-20" rows={1} />
            <div className="absolute right-2 bottom-2 flex gap-1">
              <Button size="icon" variant="ghost" className="h-8 w-8">
                <ImageIcon className="w-4 h-4" />
              </Button>
              <Button size="icon" variant="ghost" className="h-8 w-8">
                <Smile className="w-4 h-4" />
              </Button>
            </div>
          </div>
          <Button size="icon" className="h-12 w-12 rounded-full">
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
