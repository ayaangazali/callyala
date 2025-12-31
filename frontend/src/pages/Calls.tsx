import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Phone,
  Search,
  Filter,
  Download,
  Play,
  Pause,
  MoreHorizontal,
  ThumbsUp,
  ThumbsDown,
  Meh,
  Clock,
  PhoneIncoming,
  PhoneMissed,
  PhoneOff,
  Voicemail,
  Calendar,
  User,
  Car,
  FileText,
  X,
  ChevronDown,
  RefreshCw,
  Loader2,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";
import { useCalls } from "@/hooks/use-api";

interface Call {
  id: string;
  customerName: string;
  phone: string;
  vehicleModel: string;
  plate: string;
  campaign: string;
  outcome: "booked" | "callback" | "voicemail" | "no_answer" | "busy" | "not_interested" | "wrong_number";
  sentiment: "positive" | "neutral" | "negative";
  duration: string;
  timestamp: string;
  date: string;
  transcript?: string;
  summary?: string;
  recordingUrl?: string;
  nextAction?: string;
  bookedTime?: string;
}

const calls: Call[] = [
  {
    id: "call-001",
    customerName: "Ahmed Al-Mansour",
    phone: "+971 50 123 4567",
    vehicleModel: "Toyota Land Cruiser 2024",
    plate: "A 12345",
    campaign: "Service Ready Pickup",
    outcome: "booked",
    sentiment: "positive",
    duration: "1:42",
    timestamp: "10:32 AM",
    date: "Today",
    bookedTime: "Tomorrow 10:00 AM",
    transcript: "Agent: Good morning! This is Sarah from Dubai Motors. I'm calling to let you know your Toyota Land Cruiser is ready for pickup.\n\nCustomer: Oh excellent! I've been waiting for this.\n\nAgent: Great! When would be a convenient time for you to come in?\n\nCustomer: How about tomorrow morning around 10?\n\nAgent: Perfect! I've scheduled your pickup for tomorrow at 10 AM. Is there anything else you'd like to know about the service we performed?\n\nCustomer: No, that's all. Thank you for calling!\n\nAgent: You're welcome! We'll see you tomorrow. Have a great day!",
    summary: "Customer was pleased to hear their vehicle is ready. Pickup scheduled for tomorrow at 10 AM. Customer had no additional questions.",
    nextAction: "Done",
  },
  {
    id: "call-002",
    customerName: "Fatima Al-Hassan",
    phone: "+971 55 987 6543",
    vehicleModel: "Nissan Patrol 2023",
    plate: "B 54321",
    campaign: "Service Update",
    outcome: "voicemail",
    sentiment: "neutral",
    duration: "0:28",
    timestamp: "10:15 AM",
    date: "Today",
    summary: "Left voicemail regarding service completion. Will retry in 2 hours.",
    nextAction: "Retry",
  },
  {
    id: "call-003",
    customerName: "Khalid Ibrahim",
    phone: "+971 52 456 7890",
    vehicleModel: "Lexus LX 600",
    plate: "C 98765",
    campaign: "Service Ready Pickup",
    outcome: "no_answer",
    sentiment: "neutral",
    duration: "0:22",
    timestamp: "10:02 AM",
    date: "Today",
    summary: "No answer after 6 rings. Will retry.",
    nextAction: "Retry",
  },
  {
    id: "call-004",
    customerName: "Sarah Ahmed",
    phone: "+971 50 111 2222",
    vehicleModel: "BMW X5 2024",
    plate: "D 11111",
    campaign: "Service Ready Pickup",
    outcome: "callback",
    sentiment: "neutral",
    duration: "0:45",
    timestamp: "9:48 AM",
    date: "Today",
    transcript: "Agent: Hi, this is Sarah from Dubai Motors calling about your BMW X5.\n\nCustomer: Hi, I'm actually in a meeting right now. Can someone call me back in an hour?\n\nAgent: Of course! I'll have someone call you back at 10:45 AM. Is that okay?\n\nCustomer: Yes, perfect. Thank you.\n\nAgent: Great, speak to you then!",
    summary: "Customer requested callback due to being in meeting. Scheduled callback for 10:45 AM.",
    nextAction: "Human Call",
  },
  {
    id: "call-005",
    customerName: "Mohammed Al-Rashid",
    phone: "+971 55 333 4444",
    vehicleModel: "Mercedes GLE 450",
    plate: "E 22222",
    campaign: "Service Follow-up",
    outcome: "booked",
    sentiment: "positive",
    duration: "2:15",
    timestamp: "9:30 AM",
    date: "Today",
    bookedTime: "Today 3:00 PM",
    transcript: "Agent: Good morning Mr. Al-Rashid! This is Sarah from Dubai Motors following up on your Mercedes GLE service.\n\nCustomer: Yes, hello!\n\nAgent: I wanted to let you know everything is complete and your vehicle is ready. Would you like to schedule a pickup time?\n\nCustomer: Actually, can I come in this afternoon? Around 3?\n\nAgent: Absolutely! I'll book you in for 3 PM today. The total for the service comes to 1,850 AED. Will you be paying by card or cash?\n\nCustomer: Card is fine.\n\nAgent: Perfect! We'll have everything ready for you at 3. See you then!\n\nCustomer: Thank you so much!",
    summary: "Service follow-up successful. Customer booked same-day pickup at 3 PM. Payment will be by card. Total: 1,850 AED.",
    nextAction: "Done",
  },
  {
    id: "call-006",
    customerName: "Layla Hassan",
    phone: "+971 50 555 6666",
    vehicleModel: "Audi Q7 2023",
    plate: "F 33333",
    campaign: "Service Ready Pickup",
    outcome: "not_interested",
    sentiment: "negative",
    duration: "0:55",
    timestamp: "9:15 AM",
    date: "Today",
    transcript: "Agent: Hi, this is Sarah from Dubai Motors. Your Audi Q7 is ready for pickup.\n\nCustomer: I already told someone yesterday I can't come until next week.\n\nAgent: I apologize for the confusion. Would you like me to note that down?\n\nCustomer: Yes, please stop calling me about this.\n\nAgent: I understand. I've updated your file. We won't call again until next week. Sorry for any inconvenience.\n\nCustomer: Fine. Goodbye.",
    summary: "Customer frustrated about multiple calls. Requested no further contact until next week. Marked as do not call.",
    nextAction: "Do Not Call",
  },
];

const outcomeConfig = {
  booked: { label: "Booked", color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20", icon: Calendar },
  callback: { label: "Callback", color: "bg-blue-500/10 text-blue-600 border-blue-500/20", icon: Phone },
  voicemail: { label: "Voicemail", color: "bg-orange-500/10 text-orange-600 border-orange-500/20", icon: Voicemail },
  no_answer: { label: "No Answer", color: "bg-gray-500/10 text-gray-600 border-gray-500/20", icon: PhoneMissed },
  busy: { label: "Busy", color: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20", icon: PhoneOff },
  not_interested: { label: "Not Interested", color: "bg-red-500/10 text-red-600 border-red-500/20", icon: ThumbsDown },
  wrong_number: { label: "Wrong Number", color: "bg-purple-500/10 text-purple-600 border-purple-500/20", icon: X },
};

const sentimentConfig = {
  positive: { icon: ThumbsUp, color: "text-emerald-500" },
  neutral: { icon: Meh, color: "text-gray-400" },
  negative: { icon: ThumbsDown, color: "text-red-500" },
};

const Calls = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [outcomeFilter, setOutcomeFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const filteredCalls = calls.filter((call) => {
    const matchesSearch =
      call.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      call.phone.includes(searchQuery) ||
      call.vehicleModel.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesOutcome = outcomeFilter === "all" || call.outcome === outcomeFilter;
    const matchesSentiment = sentimentFilter === "all" || call.sentiment === sentimentFilter;
    return matchesSearch && matchesOutcome && matchesSentiment;
  });

  const stats = {
    total: calls.length,
    booked: calls.filter((c) => c.outcome === "booked").length,
    pending: calls.filter((c) => ["callback", "voicemail", "no_answer"].includes(c.outcome)).length,
    failed: calls.filter((c) => ["not_interested", "wrong_number", "busy"].includes(c.outcome)).length,
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar collapsed={sidebarCollapsed} onCollapse={setSidebarCollapsed} />

      <motion.main
        className="flex-1 p-6 overflow-auto"
        variants={blurIn}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Calls</h1>
            <p className="text-muted-foreground text-sm">
              View and manage all AI agent calls
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <motion.div
          className="grid grid-cols-4 gap-4 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {[
            { label: "Total Calls", value: stats.total, color: "text-foreground" },
            { label: "Booked", value: stats.booked, color: "text-emerald-500" },
            { label: "Pending", value: stats.pending, color: "text-orange-500" },
            { label: "Failed", value: stats.failed, color: "text-red-500" },
          ].map((stat) => (
            <motion.div key={stat.label} variants={staggerItem}>
              <Card className="border-border/50">
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className={`text-2xl font-semibold ${stat.color}`}>{stat.value}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, phone, or vehicle..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={outcomeFilter} onValueChange={setOutcomeFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Outcome" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Outcomes</SelectItem>
              <SelectItem value="booked">Booked</SelectItem>
              <SelectItem value="callback">Callback</SelectItem>
              <SelectItem value="voicemail">Voicemail</SelectItem>
              <SelectItem value="no_answer">No Answer</SelectItem>
              <SelectItem value="not_interested">Not Interested</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Sentiment" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sentiments</SelectItem>
              <SelectItem value="positive">Positive</SelectItem>
              <SelectItem value="neutral">Neutral</SelectItem>
              <SelectItem value="negative">Negative</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Calls Table */}
        <Card className="border-border/50">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Customer</TableHead>
                <TableHead>Vehicle</TableHead>
                <TableHead>Campaign</TableHead>
                <TableHead>Outcome</TableHead>
                <TableHead>Sentiment</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Time</TableHead>
                <TableHead className="w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <AnimatePresence>
                {filteredCalls.map((call, index) => {
                  const OutcomeIcon = outcomeConfig[call.outcome].icon;
                  const SentimentIcon = sentimentConfig[call.sentiment].icon;
                  return (
                    <motion.tr
                      key={call.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ delay: index * 0.05 }}
                      className="group cursor-pointer hover:bg-muted/50"
                      onClick={() => setSelectedCall(call)}
                    >
                      <TableCell>
                        <div>
                          <p className="font-medium">{call.customerName}</p>
                          <p className="text-xs text-muted-foreground">{call.phone}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm">{call.vehicleModel}</p>
                          <p className="text-xs text-muted-foreground">{call.plate}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{call.campaign}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={outcomeConfig[call.outcome].color}>
                          <OutcomeIcon className="w-3 h-3 mr-1" />
                          {outcomeConfig[call.outcome].label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <SentimentIcon className={`w-4 h-4 ${sentimentConfig[call.sentiment].color}`} />
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">{call.duration}</span>
                      </TableCell>
                      <TableCell>
                        <div className="text-right">
                          <p className="text-sm">{call.timestamp}</p>
                          <p className="text-xs text-muted-foreground">{call.date}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => setSelectedCall(call)}>
                              <FileText className="w-4 h-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Play className="w-4 h-4 mr-2" />
                              Play Recording
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Phone className="w-4 h-4 mr-2" />
                              Retry Call
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </motion.tr>
                  );
                })}
              </AnimatePresence>
            </TableBody>
          </Table>
        </Card>

        {/* Call Detail Sheet */}
        <Sheet open={!!selectedCall} onOpenChange={() => setSelectedCall(null)}>
          <SheetContent className="w-[500px] sm:w-[600px] sm:max-w-none">
            {selectedCall && (
              <>
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{selectedCall.customerName}</h3>
                      <p className="text-sm text-muted-foreground font-normal">{selectedCall.phone}</p>
                    </div>
                  </SheetTitle>
                </SheetHeader>

                <div className="mt-6 space-y-6">
                  {/* Quick Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-xs text-muted-foreground mb-1">Vehicle</p>
                      <div className="flex items-center gap-2">
                        <Car className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{selectedCall.vehicleModel}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{selectedCall.plate}</p>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-xs text-muted-foreground mb-1">Duration</p>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{selectedCall.duration}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{selectedCall.timestamp}</p>
                    </div>
                  </div>

                  {/* Outcome & Sentiment */}
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className={`${outcomeConfig[selectedCall.outcome].color} px-3 py-1`}>
                      {outcomeConfig[selectedCall.outcome].label}
                    </Badge>
                    {selectedCall.bookedTime && (
                      <span className="text-sm text-emerald-600">📅 {selectedCall.bookedTime}</span>
                    )}
                  </div>

                  {/* Audio Player */}
                  {selectedCall.recordingUrl !== undefined && (
                    <div className="p-4 rounded-lg border border-border bg-muted/30">
                      <div className="flex items-center gap-3">
                        <Button
                          size="icon"
                          variant="secondary"
                          onClick={() => setIsPlaying(!isPlaying)}
                        >
                          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </Button>
                        <div className="flex-1">
                          <Progress value={isPlaying ? 45 : 0} className="h-1" />
                          <div className="flex justify-between mt-1">
                            <span className="text-xs text-muted-foreground">0:45</span>
                            <span className="text-xs text-muted-foreground">{selectedCall.duration}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tabs */}
                  <Tabs defaultValue="transcript" className="w-full">
                    <TabsList className="w-full">
                      <TabsTrigger value="transcript" className="flex-1">Transcript</TabsTrigger>
                      <TabsTrigger value="summary" className="flex-1">Summary</TabsTrigger>
                    </TabsList>
                    <TabsContent value="transcript" className="mt-4">
                      <ScrollArea className="h-[300px] rounded-lg border border-border p-4 bg-muted/30">
                        {selectedCall.transcript ? (
                          <pre className="text-sm whitespace-pre-wrap font-sans leading-relaxed">
                            {selectedCall.transcript}
                          </pre>
                        ) : (
                          <p className="text-sm text-muted-foreground">No transcript available</p>
                        )}
                      </ScrollArea>
                    </TabsContent>
                    <TabsContent value="summary" className="mt-4">
                      <div className="rounded-lg border border-border p-4 bg-muted/30">
                        <p className="text-sm leading-relaxed">
                          {selectedCall.summary || "No summary available"}
                        </p>
                      </div>
                    </TabsContent>
                  </Tabs>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button className="flex-1" variant="outline">
                      <Phone className="w-4 h-4 mr-2" />
                      Retry Call
                    </Button>
                    <Button className="flex-1">
                      <User className="w-4 h-4 mr-2" />
                      Assign to Human
                    </Button>
                  </div>
                </div>
              </>
            )}
          </SheetContent>
        </Sheet>
      </motion.main>
    </div>
  );
};

export default Calls;
