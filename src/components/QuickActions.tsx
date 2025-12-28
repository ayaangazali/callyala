import { Users, Target, Building2, ArrowRight } from "lucide-react";

const actions = [
  { label: "Add New Contact", icon: Users },
  { label: "Create Deal", icon: Target },
  { label: "Add Company", icon: Building2 },
];

export function QuickActions() {
  return (
    <div className="bg-quick-actions rounded-xl p-6">
      <h2 className="text-lg font-semibold text-primary mb-4">Quick Actions</h2>
      
      <div className="space-y-2">
        {actions.map((action) => (
          <button
            key={action.label}
            className="w-full flex items-center justify-between py-2.5 text-primary hover:opacity-80 transition-opacity"
          >
            <div className="flex items-center gap-3">
              <action.icon className="w-4 h-4" />
              <span className="text-sm font-medium">{action.label}</span>
            </div>
            <ArrowRight className="w-4 h-4" />
          </button>
        ))}
      </div>
    </div>
  );
}
