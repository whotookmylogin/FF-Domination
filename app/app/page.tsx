import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Trophy, TrendingUp, Zap, Shield } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">FF Domination</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/pricing">
              <Button variant="ghost">Pricing</Button>
            </Link>
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1">
        <div className="container flex flex-col items-center gap-8 py-24 text-center">
          <div className="inline-block rounded-lg bg-muted px-3 py-1 text-sm">
            🏆 Your AI-Powered Fantasy Football Coach
          </div>

          <h1 className="max-w-4xl text-5xl font-bold tracking-tighter sm:text-6xl md:text-7xl">
            Transform Into a{" "}
            <span className="bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
              League Champion
            </span>
          </h1>

          <p className="max-w-2xl text-lg text-muted-foreground sm:text-xl">
            24/7 AI analysis, expert draft strategy, and automated trade discovery.
            Win your league with the intelligence of a 30-year fantasy veteran.
          </p>

          <div className="flex gap-4">
            <Link href="/register">
              <Button size="lg" className="h-12 px-8">
                Start Winning - Free
              </Button>
            </Link>
            <Link href="/pricing">
              <Button size="lg" variant="outline" className="h-12 px-8">
                View Pricing
              </Button>
            </Link>
          </div>

          {/* Features Grid */}
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div className="flex flex-col items-center gap-2 rounded-lg border p-6">
              <Zap className="h-10 w-10 text-primary" />
              <h3 className="font-bold">AI Trade Analyzer</h3>
              <p className="text-sm text-muted-foreground text-center">
                Discover hidden trade opportunities across your entire league
              </p>
            </div>

            <div className="flex flex-col items-center gap-2 rounded-lg border p-6">
              <Trophy className="h-10 w-10 text-primary" />
              <h3 className="font-bold">Expert Draft Tool</h3>
              <p className="text-sm text-muted-foreground text-center">
                Live pick grading and strategy from AI with 30 years experience
              </p>
            </div>

            <div className="flex flex-col items-center gap-2 rounded-lg border p-6">
              <TrendingUp className="h-10 w-10 text-primary" />
              <h3 className="font-bold">Waiver Wire Optimizer</h3>
              <p className="text-sm text-muted-foreground text-center">
                Automated FAAB bidding based on breaking news and matchups
              </p>
            </div>

            <div className="flex flex-col items-center gap-2 rounded-lg border p-6">
              <Shield className="h-10 w-10 text-primary" />
              <h3 className="font-bold">Real-Time Monitoring</h3>
              <p className="text-sm text-muted-foreground text-center">
                Instant alerts on injuries, trades, and roster opportunities
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-6">
        <div className="container flex items-center justify-between text-sm text-muted-foreground">
          <p>© 2026 FF Domination. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
