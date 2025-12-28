import { FileText, ArrowRight } from "lucide-react";

export function RecentActivities() {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-foreground">Recent Activities</h2>
        <button className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
          View All
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex flex-col items-center justify-center py-12">
        <div className="w-16 h-16 rounded-lg bg-secondary flex items-center justify-center mb-4">
          <FileText className="w-8 h-8 text-muted-foreground/50" />
        </div>
        <p className="text-foreground font-medium mb-1">No recent activities</p>
        <p className="text-muted-foreground text-sm">Start logging your interactions with contacts</p>
      </div>
    </div>
  );
}
