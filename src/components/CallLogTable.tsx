import { useState } from "react";
import { Play, FileText, ThumbsUp, Meh, ThumbsDown, MoreHorizontal, Phone, RefreshCw, UserCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { CallDetailDrawer } from "./CallDetailDrawer";

interface Call {
  id: string;
  customerName: string;
  phone: string;
  vehicleModel: string;
  plate: string;
  purpose: string;
  outcome: string;
  bookedTime?: string;
  sentiment: "positive" | "neutral" | "negative";
  nextAction: string;
  duration: string;
  timestamp: string;
}

const calls: Call[] = [
  {
    id: "1",
    customerName: "Ahmed Al-Mansour",
    phone: "+971 50 123 4567",
    vehicleModel: "Toyota Land Cruiser",
    plate: "A 12345",
    purpose: "Ready for Pickup",
    outcome: "Booked",
    bookedTime: "Tomorrow 10:00 AM",
    sentiment: "positive",
    nextAction: "Done",
    duration: "1:42",
    timestamp: "10:32 AM",
  },
  {
    id: "2",
    customerName: "Fatima Al-Hassan",
    phone: "+971 55 987 6543",
    vehicleModel: "Nissan Patrol",
    plate: "B 54321",
    purpose: "Service Update",
    outcome: "Voicemail",
    sentiment: "neutral",
    nextAction: "Retry",
    duration: "0:28",
    timestamp: "10:15 AM",
  },
  {
    id: "3",
    customerName: "Khalid Ibrahim",
    phone: "+971 52 456 7890",
    vehicleModel: "Lexus LX",
    plate: "C 98765",
    purpose: "Ready for Pickup",
    outcome: "No Answer",
    sentiment: "neutral",
    nextAction: "Retry",
    duration: "0:22",
    timestamp: "10:02 AM",
  },
  {
    id: "4",
    customerName: "Sarah Ahmed",
    phone: "+971 50 111 2222",
    vehicleModel: "BMW X5",
    plate: "D 11111",
    purpose: "Ready for Pickup",
    outcome: "Callback",
    sentiment: "neutral",
    nextAction: "Human Call",
    duration: "0:45",
    timestamp: "9:48 AM",
  },
  {
    id: "5",
    customerName: "Mohammed Al-Rashid",
    phone: "+971 55 333 4444",
    vehicleModel: "Mercedes GLE",
    plate: "E 22222",
    purpose: "Service Follow-up",
    outcome: "Booked",
    bookedTime: "Today 3:00 PM",
    sentiment: "positive",
    nextAction: "Done",
    duration: "2:15",
    timestamp: "9:30 AM",
  },
];

const outcomeColors: Record<string, string> = {
  Booked: "bg-success/10 text-success",
  Voicemail: "bg-primary/10 text-primary",
  "No Answer": "bg-muted text-muted-foreground",
  Callback: "bg-accent/20 text-accent",
  "Opt-out": "bg-destructive/10 text-destructive",
};

const sentimentIcons = {
  positive: ThumbsUp,
  neutral: Meh,
  negative: ThumbsDown,
};

const sentimentColors = {
  positive: "text-success",
  neutral: "text-muted-foreground",
  negative: "text-destructive",
};

export function CallLogTable() {
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleRowClick = (call: Call) => {
    setSelectedCall(call);
    setDrawerOpen(true);
  };

  return (
    <>
      <div className="bg-card rounded-xl border border-border">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Recent Calls</h2>
          <Button variant="outline" size="sm">
            View All Calls
          </Button>
        </div>
        
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[180px]">Customer</TableHead>
              <TableHead className="w-[160px]">Vehicle</TableHead>
              <TableHead>Purpose</TableHead>
              <TableHead>Outcome</TableHead>
              <TableHead>Booked</TableHead>
              <TableHead className="text-center">Sentiment</TableHead>
              <TableHead>Next Action</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {calls.map((call) => {
              const SentimentIcon = sentimentIcons[call.sentiment];
              return (
                <TableRow 
                  key={call.id} 
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleRowClick(call)}
                >
                  <TableCell>
                    <div>
                      <p className="font-medium text-foreground">{call.customerName}</p>
                      <p className="text-xs text-muted-foreground">{call.phone}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="text-sm text-foreground">{call.vehicleModel}</p>
                      <p className="text-xs text-muted-foreground">{call.plate}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-foreground">{call.purpose}</TableCell>
                  <TableCell>
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${outcomeColors[call.outcome]}`}>
                      {call.outcome}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm text-foreground">
                    {call.bookedTime || "—"}
                  </TableCell>
                  <TableCell className="text-center">
                    <SentimentIcon className={`w-4 h-4 mx-auto ${sentimentColors[call.sentiment]}`} />
                  </TableCell>
                  <TableCell>
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                      call.nextAction === "Done" 
                        ? "bg-success/10 text-success" 
                        : call.nextAction === "Human Call"
                        ? "bg-destructive/10 text-destructive"
                        : "bg-primary/10 text-primary"
                    }`}>
                      {call.nextAction}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Play className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <FileText className="w-4 h-4" />
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Phone className="w-4 h-4 mr-2" />
                            Call Now
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Retry
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <UserCheck className="w-4 h-4 mr-2" />
                            Assign to Human
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <CallDetailDrawer 
        call={selectedCall} 
        open={drawerOpen} 
        onOpenChange={setDrawerOpen} 
      />
    </>
  );
}
