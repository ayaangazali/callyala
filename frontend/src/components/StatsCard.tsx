import { memo } from "react";
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string;
  change: string;
  changeLabel: string;
  icon: LucideIcon;
  positive?: boolean;
  trend?: "up" | "down" | "neutral";
  showChart?: boolean;
}

export const StatsCard = memo(function StatsCard({ 
  title, 
  value, 
  change, 
  changeLabel, 
  icon: Icon,
  positive = true,
  trend = "up",
  showChart = false
}: StatsCardProps) {
  // Determine trend icon based on trend prop
  const TrendIcon = trend === "up" ? TrendingUp : TrendingDown;
  
  return (
    <div className="bg-card rounded-xl border border-border p-5 flex-1 min-w-[180px] shadow-md hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5">
      <div className="flex items-start justify-between mb-3">
        <p className="text-sm text-muted-foreground font-medium">{title}</p>
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center group-hover:from-primary/20 group-hover:to-primary/10 transition-colors">
          <Icon className="w-5 h-5 text-primary" />
        </div>
      </div>
      <p className="text-3xl font-semibold text-foreground mb-2 tracking-tight">{value}</p>
      <div className="flex items-center gap-1.5">
        {showChart ? (
          <>
            <TrendIcon className={`w-4 h-4 ${positive ? 'text-success' : 'text-destructive'}`} />
            <span className={`${positive ? 'text-success' : 'text-destructive'} text-sm`}>{change}</span>
          </>
        ) : (
          <>
            <TrendIcon className={`w-3.5 h-3.5 ${positive ? 'text-success' : 'text-destructive'}`} />
            <span className={`text-sm ${positive ? 'text-success' : 'text-destructive'}`}>
              {change}
            </span>
            <span className="text-muted-foreground text-sm">{changeLabel}</span>
          </>
        )}
      </div>
    </div>
  );
});
