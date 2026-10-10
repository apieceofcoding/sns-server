import { Sidebar } from "@/components/sidebar"
import { ExploreFeed } from "@/components/explore-feed"
import { TrendingPanel } from "@/components/trending-panel"

export default function ExplorePage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 border-x border-border">
        <ExploreFeed />
      </main>
      <aside className="hidden lg:block w-80 xl:w-96">
        <TrendingPanel />
      </aside>
    </div>
  )
}
