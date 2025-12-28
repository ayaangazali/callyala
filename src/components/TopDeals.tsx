import { Target, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TopDeals() {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">Top Deals</h2>
        <button className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
          View All
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex flex-col items-center justify-center py-6">
        <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
          <Target className="w-8 h-8 text-muted-foreground/40" />
        </div>
        <p className="text-foreground font-medium mb-1">No active deals</p>
        <p className="text-muted-foreground text-sm text-center mb-4">Start by creating your first deal</p>
        <Button size="sm">Create Deal</Button>
      </div>
    </div>
  );
}
