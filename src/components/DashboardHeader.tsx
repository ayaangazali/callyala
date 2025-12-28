import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export function DashboardHeader() {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Welcome back! Here's what's happening with your sales.</p>
      </div>
      
      <div className="flex items-center gap-3">
        <Button variant="secondary" className="gap-2">
          GitHub Connection
        </Button>
        <Button variant="outline" className="gap-2">
          <Plus className="w-4 h-4" />
          Log Activity
        </Button>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          Add Contact
        </Button>
      </div>
    </div>
  );
}
