import { motion } from "framer-motion";
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { useCountUp } from "@/hooks/use-motion";
import { cardHover, iconHover } from "@/lib/motion";
import { cn } from "@/lib/utils";

interface VoiceStatsCardProps {
  title: string;
  value: string;
  change?: string;
  changeLabel?: string;
  icon: LucideIcon;
  positive?: boolean;
  trend?: "up" | "down" | "neutral";
  index?: number;
}

export function VoiceStatsCard({ 
  title, 
  value, 
  change, 
  changeLabel, 
  icon: Icon,
  positive = true,
  trend = "up",
  index = 0
}: VoiceStatsCardProps) {
  // Extract numeric value for animation
  const numericValue = parseFloat(value.replace(/[^0-9.]/g, '')) || 0;
  const animatedValue = useCountUp(numericValue, 800, 0);
  
  // Format the animated value back
  const displayValue = value.includes('$') 
    ? `$${animatedValue}` 
    : value.includes('%') 
    ? `${animatedValue}%`
    : value.includes(':')
    ? value // Don't animate time values
    : animatedValue.toString();

  return (
    <motion.div
      className="bg-card rounded-xl border border-border p-4 flex-1 min-w-[140px] card-hover relative overflow-hidden group"
      initial={{ opacity: 0, y: 20, filter: "blur(4px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ 
        delay: index * 0.05,
        duration: 0.3,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      whileHover="hover"
      variants={cardHover}
    >
      {/* Subtle gradient overlay on hover */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
      />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-2">
          <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wide">{title}</p>
          <motion.div 
            className="w-8 h-8 rounded-lg bg-secondary/80 flex items-center justify-center"
            variants={iconHover}
          >
            <Icon className="w-4 h-4 text-muted-foreground" />
          </motion.div>
        </div>
        
        <motion.p 
          className="text-2xl font-bold text-foreground mb-1 tabular-nums"
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 + 0.2 }}
        >
          {displayValue}
        </motion.p>
        
        {change && (
          <motion.div 
            className="flex items-center gap-1"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 + 0.3 }}
          >
            {trend === "up" && (
              <TrendingUp className={cn(
                "w-3 h-3",
                positive ? "text-success" : "text-destructive"
              )} />
            )}
            {trend === "down" && (
              <TrendingDown className={cn(
                "w-3 h-3",
                positive ? "text-success" : "text-destructive"
              )} />
            )}
            <span className={cn(
              "text-xs font-medium",
              positive ? "text-success" : "text-destructive"
            )}>
              {change}
            </span>
            {changeLabel && (
              <span className="text-xs text-muted-foreground">{changeLabel}</span>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
