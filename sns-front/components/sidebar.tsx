"use client"

import { Home, Search, Bell, Mail, User, MoreHorizontal, Feather, LogOut } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { useAuth } from "@/hooks/api/use-auth"

const navItems = [
  { icon: Home, label: "홈", href: "/" },
  { icon: Search, label: "탐색", href: "/explore" },
  { icon: Bell, label: "알림", href: "/notifications" },
  { icon: Mail, label: "쪽지", href: "/messages" },
  { icon: User, label: "프로필", href: "/profile" },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside className="w-20 xl:w-72 flex flex-col items-center xl:items-start p-3 sticky top-0 h-screen">
      <div className="flex items-center justify-center xl:justify-start w-full mb-4 p-3">
        <Feather className="w-8 h-8 text-primary" />
      </div>

      <nav className="flex flex-col gap-2 w-full">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "flex items-center gap-4 px-4 py-3 rounded-full transition-colors hover:bg-accent",
                  isActive && "font-bold",
                )}
              >
                <Icon className={cn("w-7 h-7", isActive && "stroke-[2.5]")} />
                <span className="hidden xl:block text-xl">{item.label}</span>
              </div>
            </Link>
          )
        })}

        <Button className="mt-2 w-14 h-14 xl:w-full xl:h-auto rounded-full" size="lg">
          <Feather className="w-6 h-6 xl:hidden" />
          <span className="hidden xl:block text-lg font-bold">게시하기</span>
        </Button>
      </nav>

      <div className="mt-auto w-full">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-3 p-3 rounded-full hover:bg-accent transition-colors w-full">
              <div className="w-10 h-10 rounded-full bg-muted overflow-hidden">
                {user?.profileImageUrl ? (
                  <img
                    src={user.profileImageUrl}
                    alt={user.username}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground font-medium">
                    {user?.username?.charAt(0).toUpperCase() || <User className="w-6 h-6" />}
                  </div>
                )}
              </div>
              <div className="hidden xl:flex flex-1 flex-col items-start">
                <div className="font-semibold text-sm">{user?.username || '로딩중...'}</div>
                <div className="text-muted-foreground text-sm">@{user?.username || 'username'}</div>
              </div>
              <MoreHorizontal className="hidden xl:block w-5 h-5" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem onClick={() => logout()} className="text-red-600 cursor-pointer">
              <LogOut className="w-4 h-4 mr-2" />
              로그아웃
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  )
}
