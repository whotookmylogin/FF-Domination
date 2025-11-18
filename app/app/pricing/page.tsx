import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Check } from "lucide-react";

const tiers = [
  {
    name: "Rookie",
    price: "$0",
    period: "forever",
    description: "Perfect for trying out the platform",
    features: [
      "1 league connection (ESPN or Sleeper)",
      "Basic roster analysis",
      "Weekly waiver wire suggestions (top 3)",
      "5 AI queries per month",
      "Standard email notifications"
    ],
    cta: "Get Started Free",
    href: "/register",
    highlighted: false
  },
  {
    name: "Pro",
    price: "$14.99",
    period: "per month",
    description: "For serious fantasy managers",
    features: [
      "Unlimited leagues",
      "Full AI Trade Analyzer",
      "Expert Draft Tool with live grading",
      "100 AI queries per month",
      "Priority news monitoring (hourly)",
      "Push notifications + SMS alerts",
      "FAAB budget optimizer"
    ],
    cta: "Upgrade to Pro",
    href: "/register?tier=pro",
    highlighted: true
  },
  {
    name: "Champion",
    price: "$29.99",
    period: "per month",
    description: "Maximum competitive advantage",
    features: [
      "Everything in Pro",
      "Unlimited AI queries",
      "Multi-team trade discovery",
      "Custom AI training on league history",
      "Playoff probability simulations",
      "White-glove onboarding",
      "Priority support (24h response)",
      "BYOK (Bring Your Own OpenAI Key)"
    ],
    cta: "Go Champion",
    href: "/register?tier=champion",
    highlighted: false
  }
];

export default function PricingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-xl font-bold">FF Domination</span>
          </Link>
          <nav className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Pricing Section */}
      <section className="flex-1 py-16">
        <div className="container">
          <div className="mx-auto mb-16 max-w-3xl text-center">
            <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl">
              Choose Your Path to Victory
            </h1>
            <p className="text-lg text-muted-foreground">
              Start free and upgrade when you're ready to dominate your league
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {tiers.map((tier) => (
              <Card
                key={tier.name}
                className={tier.highlighted ? "border-primary shadow-lg" : ""}
              >
                <CardHeader>
                  <CardTitle className="text-2xl">{tier.name}</CardTitle>
                  <CardDescription>{tier.description}</CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{tier.price}</span>
                    <span className="text-muted-foreground"> / {tier.period}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <Check className="h-5 w-5 shrink-0 text-primary" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link href={tier.href} className="w-full">
                    <Button
                      className="w-full"
                      variant={tier.highlighted ? "default" : "outline"}
                      size="lg"
                    >
                      {tier.cta}
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* FAQ */}
          <div className="mx-auto mt-16 max-w-3xl">
            <h2 className="mb-8 text-center text-2xl font-bold">
              Frequently Asked Questions
            </h2>
            <div className="space-y-6">
              <div>
                <h3 className="mb-2 font-semibold">Can I change plans later?</h3>
                <p className="text-sm text-muted-foreground">
                  Yes! You can upgrade or downgrade at any time. Changes take effect immediately.
                </p>
              </div>
              <div>
                <h3 className="mb-2 font-semibold">What's BYOK (Bring Your Own Key)?</h3>
                <p className="text-sm text-muted-foreground">
                  Champion tier users can use their own OpenAI API key for unlimited AI queries at their own cost.
                </p>
              </div>
              <div>
                <h3 className="mb-2 font-semibold">Do you offer annual billing?</h3>
                <p className="text-sm text-muted-foreground">
                  Yes! Annual plans save 17% compared to monthly billing. Contact support for details.
                </p>
              </div>
              <div>
                <h3 className="mb-2 font-semibold">Which platforms do you support?</h3>
                <p className="text-sm text-muted-foreground">
                  We currently support ESPN and Sleeper fantasy football leagues.
                </p>
              </div>
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
