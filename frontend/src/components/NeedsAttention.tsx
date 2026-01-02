import { memo } from "react";
import { AlertTriangle, PhoneCall, Frown, Clock, AlertCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

// Move static data outside component to prevent recreation on every render
const attentionItems = [
  {
    id: 1,
    type: "retry",
    icon: AlertTriangle,
    title: "3rd failed attempt",
    description: "Mohammed Al-Rashid - Toyota Camry",
    action: "Retry Now",
    priority: "high",
  },
  {
    id: 2,
    type: "callback",
    icon: PhoneCall,
    title: "Callback requested",
    description: "Sarah Ahmed - requested 2PM callback",
    action: "Schedule",
    priority: "high",
  },
  {
    id: 3,
    type: "sentiment",
    icon: Frown,
    title: "Negative sentiment detected",
    description: "Khalid Ibrahim - complaint about wait time",
    action: "Review",
    priority: "medium",
  },
  {
    id: 4,
    type: "missing",
    icon: Clock,
    title: "Pickup booked - time missing",
    description: "Fatima Hassan - Nissan Patrol",
    action: "Complete",
    priority: "medium",
  },
  {
    id: 5,
    type: "mismatch",
    icon: AlertCircle,
    title: "Plate/job mismatch",
    description: "Job #4521 - plate doesn't match record",
    action: "Verify",
    priority: "low",
  },
];

const priorityColors = {
  high: "text-destructive bg-destructive/10",
  medium: "text-primary bg-primary/10",
  low: "text-muted-foreground bg-muted",
};

export const NeedsAttention = memo(function NeedsAttention() {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Needs Attention</h2>
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-destructive/10 text-destructive">
            {attentionItems.length}
          </span>
        </div>
        <button className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
          View All
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
      
      <div className="space-y-3">
        {attentionItems.map((item) => (
          <div
            key={item.id}
            className="flex items-center gap-3 p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
          >
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${priorityColors[item.priority]}`}>
              <item.icon className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground">{item.title}</p>
              <p className="text-xs text-muted-foreground truncate">{item.description}</p>
            </div>
            <Button size="sm" variant="outline" className="shrink-0 h-7 text-xs">
              {item.action}
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
});
