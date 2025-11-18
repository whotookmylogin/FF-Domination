import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Trophy, TrendingUp, Users, Bell } from "lucide-react";

const stats = [
  {
    title: "Active Leagues",
    value: "3",
    icon: Trophy,
    description: "+1 from last season",
  },
  {
    title: "Win Rate",
    value: "67%",
    icon: TrendingUp,
    description: "+12% from last year",
  },
  {
    title: "Trades Completed",
    value: "8",
    icon: Users,
    description: "This season",
  },
  {
    title: "AI Queries Used",
    value: "24/100",
    icon: Bell,
    description: "This month",
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's your fantasy football overview.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Action Items */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Actions</CardTitle>
          <CardDescription>
            Top priorities for this week
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <p className="font-medium">Review Waiver Wire</p>
              <p className="text-sm text-muted-foreground">
                3 high-value players available
              </p>
            </div>
            <div className="text-sm text-muted-foreground">Priority: High</div>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <p className="font-medium">Consider Trade Opportunity</p>
              <p className="text-sm text-muted-foreground">
                AI found 2 favorable trades
              </p>
            </div>
            <div className="text-sm text-muted-foreground">Priority: Medium</div>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <p className="font-medium">Set Your Lineup</p>
              <p className="text-sm text-muted-foreground">
                Week 12 deadline in 2 days
              </p>
            </div>
            <div className="text-sm text-muted-foreground">Priority: Medium</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
