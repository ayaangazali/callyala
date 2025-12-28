import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";

interface VoiceStatsCardProps {
  title: string;
  value: string;
  change?: string;
  changeLabel?: string;
  icon: LucideIcon;
  positive?: boolean;
  trend?: "up" | "down" | "neutral";
}

export function VoiceStatsCard({ 
  title, 
  value, 
  change, 
  changeLabel, 
  icon: Icon,
  positive = true,
  trend = "up"
}: VoiceStatsCardProps) {
  return (
    <div className="bg-card rounded-xl border border-border p-4 flex-1 min-w-[150px]">
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{title}</p>
        <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center">
          <Icon className="w-4 h-4 text-muted-foreground" />
        </div>
      </div>
      <p className="text-2xl font-bold text-foreground mb-1">{value}</p>
      {change && (
        <div className="flex items-center gap-1">
          {trend === "up" && <TrendingUp className={`w-3 h-3 ${positive ? 'text-success' : 'text-destructive'}`} />}
          {trend === "down" && <TrendingDown className={`w-3 h-3 ${positive ? 'text-success' : 'text-destructive'}`} />}
          <span className={`text-xs ${positive ? 'text-success' : 'text-destructive'}`}>
            {change}
          </span>
          {changeLabel && <span className="text-xs text-muted-foreground">{changeLabel}</span>}
        </div>
      )}
    </div>
  );
}
