"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "ダッシュボード" },
    { href: "/channels", label: "チャンネル管理" },
    { href: "/jobs", label: "ジョブ実行" },
  ];

  return (
    <header className="bg-purple-700 text-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <span className="bg-purple-500 px-2 py-1 rounded text-xs font-bold">
              ADMIN
            </span>
            <Link href="/" className="text-xl font-bold">
              YouTuber Predictor
            </Link>
          </div>

          <nav className="flex space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-2 text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? "text-white border-b-2 border-white"
                    : "text-purple-200 hover:text-white"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
