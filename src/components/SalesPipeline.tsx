import { PieChart } from "lucide-react";

export function SalesPipeline() {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <h2 className="text-xl font-semibold text-foreground mb-8">Sales Pipeline by Stage</h2>
      
      <div className="flex flex-col items-center justify-center py-12">
        <div className="w-20 h-20 rounded-full bg-secondary flex items-center justify-center mb-4">
          <PieChart className="w-10 h-10 text-muted-foreground/50" />
        </div>
        <p className="text-foreground font-medium mb-1">No pipeline data available</p>
        <p className="text-muted-foreground text-sm">Create some deals to see your pipeline</p>
      </div>
    </div>
  );
}
