import { Sidebar } from "@/components/sidebar"
import { HomeFeed } from "@/components/home-feed"
import { TrendingPanel } from "@/components/trending-panel"

export default function HomePage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 border-x border-border">
        <HomeFeed />
      </main>
      <aside className="hidden lg:block w-80 xl:w-96">
        <TrendingPanel />
      </aside>
    </div>
  )
}
