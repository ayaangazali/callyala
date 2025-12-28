import { LucideIcon, TrendingUp } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string;
  change: string;
  changeLabel: string;
  icon: LucideIcon;
  positive?: boolean;
  showChart?: boolean;
}

export function StatsCard({ 
  title, 
  value, 
  change, 
  changeLabel, 
  icon: Icon,
  positive = true,
  showChart = false
}: StatsCardProps) {
  return (
    <div className="bg-card rounded-xl border border-border p-5 flex-1 min-w-[180px]">
      <div className="flex items-start justify-between mb-3">
        <p className="text-sm text-muted-foreground">{title}</p>
        <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
          <Icon className="w-5 h-5 text-muted-foreground" />
        </div>
      </div>
      <p className="text-3xl font-semibold text-foreground mb-2">{value}</p>
      <div className="flex items-center gap-1.5">
        {showChart ? (
          <>
            <TrendingUp className="w-4 h-4 text-success" />
            <span className="text-success text-sm">{change}</span>
          </>
        ) : (
          <>
            <span className={`text-sm ${positive ? 'text-success' : 'text-destructive'}`}>
              ↗ {change}
            </span>
            <span className="text-muted-foreground text-sm">{changeLabel}</span>
          </>
        )}
      </div>
    </div>
  );
}
