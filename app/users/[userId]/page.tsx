"use client"

import { use, useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { UserProfileHeader, type UserProfileTab } from "@/components/user-profile-header"
import { UserProfileFeed } from "@/components/user-profile-feed"
import { TrendingPanel } from "@/components/trending-panel"

interface UserProfilePageProps {
  params: Promise<{ userId: string }>
}

export default function UserProfilePage({ params }: UserProfilePageProps) {
  const { userId } = use(params)
  const userIdNum = parseInt(userId, 10)
  const [activeTab, setActiveTab] = useState<UserProfileTab>("posts")

  if (isNaN(userIdNum)) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 border-x border-border">
          <div className="w-full max-w-2xl mx-auto p-8 text-center text-muted-foreground">
            잘못된 사용자 ID입니다.
          </div>
        </main>
        <aside className="hidden lg:block w-80 xl:w-96">
          <TrendingPanel />
        </aside>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 border-x border-border">
        <div className="w-full max-w-2xl mx-auto">
          <UserProfileHeader userId={userIdNum} activeTab={activeTab} onTabChange={setActiveTab} />
          <UserProfileFeed userId={userIdNum} activeTab={activeTab} />
        </div>
      </main>
      <aside className="hidden lg:block w-80 xl:w-96">
        <TrendingPanel />
      </aside>
    </div>
  )
}
