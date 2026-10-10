import { Sidebar } from "@/components/sidebar"
import { MessagesList } from "@/components/messages-list"
import { ChatWindow } from "@/components/chat-window"

export default function MessagesPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex flex-1 border-x border-border">
        <MessagesList />
        <ChatWindow />
      </main>
    </div>
  )
}
