import { Sidebar } from "@/components/sidebar"
import { NotificationsFeed } from "@/components/notifications-feed"

export default function NotificationsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 border-x border-border">
        <NotificationsFeed />
      </main>
    </div>
  )
}
