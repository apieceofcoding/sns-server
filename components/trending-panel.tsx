import { Button } from "@/components/ui/button"
import { Search, TrendingUp } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

const trends = [
  { category: "엔터테인먼트", topic: "#최신드라마", tweets: "45.2K" },
  { category: "스포츠", topic: "#월드컵", tweets: "123K" },
  { category: "기술", topic: "#AI", tweets: "89.7K" },
  { category: "뉴스", topic: "#대한민국", tweets: "234K" },
]

const whoToFollow = [
  { name: "테크뉴스", username: "technews" },
  { name: "트렌드코리아", username: "trendkorea" },
  { name: "디자인허브", username: "designhub" },
]

export function TrendingPanel() {
  return (
    <div className="sticky top-0 p-4 space-y-4 h-screen overflow-y-auto">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <Input placeholder="검색" className="pl-12 bg-muted border-none rounded-full" />
      </div>

      <Card className="overflow-hidden">
        <div className="p-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            트렌드
          </h2>
        </div>
        {trends.map((trend, index) => (
          <div key={index} className="p-4 hover:bg-accent/50 transition-colors cursor-pointer border-t border-border">
            <div className="text-sm text-muted-foreground mb-1">{trend.category}</div>
            <div className="font-bold mb-1">{trend.topic}</div>
            <div className="text-sm text-muted-foreground">{trend.tweets} 트윗</div>
          </div>
        ))}
      </Card>

      <Card className="overflow-hidden">
        <div className="p-4">
          <h2 className="text-xl font-bold">팔로우 추천</h2>
        </div>
        {whoToFollow.map((user, index) => (
          <div
            key={index}
            className="p-4 flex items-center justify-between hover:bg-accent/50 transition-colors border-t border-border"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-muted" />
              <div>
                <div className="font-bold">{user.name}</div>
                <div className="text-sm text-muted-foreground">@{user.username}</div>
              </div>
            </div>
            <Button variant="outline" size="sm" className="rounded-full font-bold bg-transparent">
              팔로우
            </Button>
          </div>
        ))}
      </Card>
    </div>
  )
}
