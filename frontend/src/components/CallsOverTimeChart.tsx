import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const callsData = [
  { time: "8AM", calls: 12, answered: 8 },
  { time: "9AM", calls: 18, answered: 14 },
  { time: "10AM", calls: 22, answered: 16 },
  { time: "11AM", calls: 15, answered: 11 },
  { time: "12PM", calls: 8, answered: 5 },
  { time: "1PM", calls: 10, answered: 7 },
  { time: "2PM", calls: 19, answered: 14 },
  { time: "3PM", calls: 16, answered: 12 },
  { time: "4PM", calls: 7, answered: 5 },
];

export function CallsOverTimeChart() {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">Calls Over Time</h2>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-primary/30"></div>
            <span className="text-muted-foreground">Total Calls</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-success"></div>
            <span className="text-muted-foreground">Answered</span>
          </div>
        </div>
      </div>
      
      <div className="h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={callsData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(24, 95%, 53%)" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="hsl(24, 95%, 53%)" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorAnswered" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 13% 91%)" vertical={false} />
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: 'hsl(220 9% 46%)' }}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: 'hsl(220 9% 46%)' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(0 0% 100%)', 
                border: '1px solid hsl(220 13% 91%)',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="calls" 
              stroke="hsl(24, 95%, 53%)" 
              fillOpacity={1} 
              fill="url(#colorCalls)" 
              strokeWidth={2}
            />
            <Area 
              type="monotone" 
              dataKey="answered" 
              stroke="hsl(142, 71%, 45%)" 
              fillOpacity={1} 
              fill="url(#colorAnswered)" 
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
