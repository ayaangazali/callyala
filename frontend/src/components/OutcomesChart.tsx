import { memo } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

// Move static data outside component to prevent recreation
const outcomeData = [
  { name: "Booked", value: 23, color: "hsl(142, 71%, 45%)" },
  { name: "No Answer", value: 34, color: "hsl(220, 9%, 46%)" },
  { name: "Voicemail", value: 18, color: "hsl(24, 95%, 53%)" },
  { name: "Busy", value: 12, color: "hsl(168, 76%, 26%)" },
  { name: "Wrong Number", value: 5, color: "hsl(0, 84%, 60%)" },
  { name: "Opt-out", value: 3, color: "hsl(220, 13%, 18%)" },
];

// Memoize tooltip and legend styles
const tooltipStyle = {
  backgroundColor: 'hsl(0 0% 100%)',
  border: '1px solid hsl(220 13% 91%)',
  borderRadius: '8px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
};

const tooltipFormatter = (value: number) => [`${value} calls`, ''];
const legendFormatter = (value: string) => <span className="text-sm text-foreground">{value}</span>;

export const OutcomesChart = memo(function OutcomesChart() {
  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-md hover:shadow-lg transition-shadow duration-300">
      <h2 className="text-lg font-semibold text-foreground mb-6">Outcomes Breakdown</h2>
      
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={outcomeData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
            >
              {outcomeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={tooltipStyle}
              formatter={tooltipFormatter}
            />
            <Legend 
              layout="vertical" 
              align="right" 
              verticalAlign="middle"
              iconType="circle"
              iconSize={8}
              formatter={legendFormatter}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Total Calls Today</span>
          <span className="font-semibold text-foreground">95</span>
        </div>
      </div>
    </div>
  );
});
