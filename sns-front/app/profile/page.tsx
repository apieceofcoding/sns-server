"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { ProfileHeader } from "@/components/profile-header"
import { ProfileFeed } from "@/components/profile-feed"
import { TrendingPanel } from "@/components/trending-panel"

export type ProfileTab = "posts" | "replies" | "media" | "likes"

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<ProfileTab>("posts")

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 border-x border-border">
        <div className="w-full max-w-2xl mx-auto">
          <ProfileHeader activeTab={activeTab} onTabChange={setActiveTab} />
          <ProfileFeed activeTab={activeTab} />
        </div>
      </main>
      <aside className="hidden lg:block w-80 xl:w-96">
        <TrendingPanel />
      </aside>
    </div>
  )
}
