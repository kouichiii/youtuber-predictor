import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "YouTuber予測 - 成長予測ランキング",
  description: "YouTuberの成長を予測するアプリ",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-grow container mx-auto px-4 py-6 max-w-6xl">
            {children}
          </main>
          <footer className="py-6 text-center text-sm text-gray-400 border-t border-gray-100">
            <p>YouTuber予測</p>
          </footer>
        </div>
      </body>
    </html>
  );
}
