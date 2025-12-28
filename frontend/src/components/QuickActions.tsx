import { Megaphone, ShieldCheck, Calendar, Phone, FileText, ArrowRight } from "lucide-react";

const actions = [
  { label: "Start Pickup Campaign", icon: Megaphone, highlight: true },
  { label: "Review Flagged Calls", icon: ShieldCheck, badge: "3" },
  { label: "View Tomorrow's Pickups", icon: Calendar },
  { label: "Manual Call Queue", icon: Phone },
  { label: "Update Scripts", icon: FileText },
];

export function QuickActions() {
  return (
    <div className="bg-quick-actions rounded-xl p-6">
      <h2 className="text-lg font-semibold text-primary mb-4">Quick Actions</h2>
      
      <div className="space-y-1">
        {actions.map((action) => (
          <button
            key={action.label}
            className={`w-full flex items-center justify-between py-2.5 px-2 rounded-lg text-primary hover:bg-primary/10 transition-colors ${
              action.highlight ? 'bg-primary/5' : ''
            }`}
          >
            <div className="flex items-center gap-3">
              <action.icon className="w-4 h-4" />
              <span className="text-sm font-medium">{action.label}</span>
              {action.badge && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-destructive text-destructive-foreground">
                  {action.badge}
                </span>
              )}
            </div>
            <ArrowRight className="w-4 h-4" />
          </button>
        ))}
      </div>
    </div>
  );
}
