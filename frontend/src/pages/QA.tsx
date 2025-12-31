import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Star,
  Play,
  Pause,
  Search,
  Filter,
  Download,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  SkipForward,
  Volume2,
  Clock,
  User,
  Phone,
  BarChart3,
  TrendingUp,
  Flag,
  Eye,
  Loader2,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Slider } from "@/components/ui/slider";
import { Progress } from "@/components/ui/progress";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";
import { useQACalls, useQAStats, useQATrends, useSubmitReview, useFlagCall } from "@/hooks/use-api";
import { useToast } from "@/hooks/use-toast";

interface CallForReview {
  id: string;
  customerName: string;
  phone: string;
  campaign: string;
  duration: string;
  outcome: "booked" | "callback" | "not-interested" | "no-answer";
  sentiment: "positive" | "neutral" | "negative";
  date: string;
  reviewed: boolean;
  flagged: boolean;
  scores?: {
    greeting: number;
    clarity: number;
    persuasion: number;
    objectionHandling: number;
    closing: number;
    overall: number;
  };
  feedback?: string;
}

const callsForReview: CallForReview[] = [
  {
    id: "qa-001",
    customerName: "Ahmed Al-Mansour",
    phone: "+971 50 123 4567",
    campaign: "Service Reminder Q1",
    duration: "4:32",
    outcome: "booked",
    sentiment: "positive",
    date: "Today, 10:30 AM",
    reviewed: false,
    flagged: true,
    scores: {
      greeting: 95,
      clarity: 88,
      persuasion: 92,
      objectionHandling: 85,
      closing: 90,
      overall: 90,
    },
  },
  {
    id: "qa-002",
    customerName: "Fatima Al-Hassan",
    phone: "+971 55 987 6543",
    campaign: "Appointment Confirmation",
    duration: "2:15",
    outcome: "callback",
    sentiment: "neutral",
    date: "Today, 09:45 AM",
    reviewed: false,
    flagged: false,
  },
  {
    id: "qa-003",
    customerName: "Mohammed Al-Rashid",
    phone: "+971 55 333 4444",
    campaign: "Service Reminder Q1",
    duration: "5:48",
    outcome: "not-interested",
    sentiment: "negative",
    date: "Today, 09:15 AM",
    reviewed: true,
    flagged: true,
    scores: {
      greeting: 75,
      clarity: 70,
      persuasion: 60,
      objectionHandling: 55,
      closing: 50,
      overall: 62,
    },
    feedback: "Customer was frustrated. AI could have handled objections better. Consider adding more empathy responses.",
  },
  {
    id: "qa-004",
    customerName: "Sarah Ahmed",
    phone: "+971 50 111 2222",
    campaign: "Winter Promotion",
    duration: "3:22",
    outcome: "booked",
    sentiment: "positive",
    date: "Yesterday, 4:30 PM",
    reviewed: true,
    flagged: false,
    scores: {
      greeting: 92,
      clarity: 95,
      persuasion: 88,
      objectionHandling: 90,
      closing: 94,
      overall: 92,
    },
    feedback: "Excellent call. Good example for training.",
  },
  {
    id: "qa-005",
    customerName: "Khalid Ibrahim",
    phone: "+971 52 456 7890",
    campaign: "Service Reminder Q1",
    duration: "1:45",
    outcome: "no-answer",
    sentiment: "neutral",
    date: "Yesterday, 3:15 PM",
    reviewed: false,
    flagged: false,
  },
];

const outcomeConfig = {
  booked: { label: "Booked", color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20", icon: CheckCircle },
  callback: { label: "Callback", color: "bg-amber-500/10 text-amber-600 border-amber-500/20", icon: Clock },
  "not-interested": { label: "Not Interested", color: "bg-red-500/10 text-red-600 border-red-500/20", icon: XCircle },
  "no-answer": { label: "No Answer", color: "bg-gray-500/10 text-gray-600 border-gray-500/20", icon: Phone },
};

const sentimentConfig = {
  positive: { label: "Positive", color: "text-emerald-500" },
  neutral: { label: "Neutral", color: "text-gray-500" },
  negative: { label: "Negative", color: "text-red-500" },
};

const QA = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("pending");
  const [selectedCall, setSelectedCall] = useState<CallForReview | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [scores, setScores] = useState({
    greeting: 80,
    clarity: 80,
    persuasion: 80,
    objectionHandling: 80,
    closing: 80,
  });
  const [feedback, setFeedback] = useState("");

  const filteredCalls = callsForReview.filter((call) => {
    const matchesSearch =
      call.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      call.campaign.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "pending" && !call.reviewed) ||
      (statusFilter === "reviewed" && call.reviewed) ||
      (statusFilter === "flagged" && call.flagged);
    return matchesSearch && matchesStatus;
  });

  const stats = {
    pendingReview: callsForReview.filter((c) => !c.reviewed).length,
    reviewed: callsForReview.filter((c) => c.reviewed).length,
    flagged: callsForReview.filter((c) => c.flagged).length,
    avgScore: Math.round(
      callsForReview
        .filter((c) => c.scores)
        .reduce((sum, c) => sum + (c.scores?.overall || 0), 0) /
        callsForReview.filter((c) => c.scores).length
    ),
  };

  const overallScore = Math.round(
    (scores.greeting + scores.clarity + scores.persuasion + scores.objectionHandling + scores.closing) / 5
  );

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
            <h1 className="text-2xl font-semibold text-foreground">QA / Review</h1>
            <p className="text-muted-foreground text-sm">
              Review and score AI voice agent call quality
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
            <Button variant="outline" size="sm">
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </Button>
          </div>
        </div>

        {/* Stats */}
        <motion.div
          className="grid grid-cols-4 gap-4 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {[
            { label: "Pending Review", value: stats.pendingReview, icon: Clock, color: "text-amber-500" },
            { label: "Reviewed", value: stats.reviewed, icon: CheckCircle, color: "text-emerald-500" },
            { label: "Flagged", value: stats.flagged, icon: Flag, color: "text-red-500" },
            { label: "Avg Score", value: `${stats.avgScore}%`, icon: Star, color: "text-primary" },
          ].map((stat) => (
            <motion.div key={stat.label} variants={staggerItem}>
              <Card className="border-border/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                      <p className={`text-2xl font-semibold ${stat.color}`}>{stat.value}</p>
                    </div>
                    <stat.icon className={`w-8 h-8 ${stat.color} opacity-30`} />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-3 gap-6">
          {/* Calls List */}
          <div className="col-span-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search calls..."
                  className="pl-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Calls</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="reviewed">Reviewed</SelectItem>
                  <SelectItem value="flagged">Flagged</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <ScrollArea className="h-[calc(100vh-300px)]">
              <div className="space-y-2">
                {filteredCalls.map((call) => {
                  const OutcomeIcon = outcomeConfig[call.outcome].icon;
                  return (
                    <motion.div key={call.id} variants={staggerItem}>
                      <Card
                        className={`cursor-pointer transition-all hover:border-primary/50 ${
                          selectedCall?.id === call.id ? "border-primary bg-primary/5" : "border-border/50"
                        }`}
                        onClick={() => setSelectedCall(call)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Avatar className="h-8 w-8">
                                <AvatarFallback className="text-xs">
                                  {call.customerName.split(" ").map((n) => n[0]).join("")}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <p className="font-medium text-sm">{call.customerName}</p>
                                <p className="text-xs text-muted-foreground">{call.date}</p>
                              </div>
                            </div>
                            {call.flagged && <Flag className="w-4 h-4 text-red-500" />}
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline" className={outcomeConfig[call.outcome].color}>
                              <OutcomeIcon className="w-3 h-3 mr-1" />
                              {outcomeConfig[call.outcome].label}
                            </Badge>
                            <Badge
                              variant="secondary"
                              className={`text-xs ${sentimentConfig[call.sentiment].color}`}
                            >
                              {sentimentConfig[call.sentiment].label}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span>{call.campaign}</span>
                            <span>{call.duration}</span>
                          </div>
                          {call.scores && (
                            <div className="mt-2 flex items-center gap-2">
                              <Progress value={call.scores.overall} className="h-1" />
                              <span className="text-xs font-medium">{call.scores.overall}%</span>
                            </div>
                          )}
                          {call.reviewed && (
                            <Badge variant="secondary" className="mt-2 text-xs bg-emerald-500/10 text-emerald-600">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Reviewed
                            </Badge>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </ScrollArea>
          </div>

          {/* Review Panel */}
          <div className="col-span-2">
            {selectedCall ? (
              <Card className="border-border/50 h-full">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-12 w-12">
                        <AvatarFallback className="text-lg">
                          {selectedCall.customerName.split(" ").map((n) => n[0]).join("")}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-lg">{selectedCall.customerName}</CardTitle>
                        <CardDescription>
                          {selectedCall.campaign} • {selectedCall.duration}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant={selectedCall.flagged ? "destructive" : "outline"}
                        size="sm"
                      >
                        <Flag className="w-4 h-4 mr-2" />
                        {selectedCall.flagged ? "Flagged" : "Flag"}
                      </Button>
                      <Button size="sm" variant="outline">
                        <SkipForward className="w-4 h-4 mr-2" />
                        Next
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Audio Player */}
                  <div className="p-4 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-4">
                      <Button
                        size="icon"
                        variant="outline"
                        className="h-12 w-12 rounded-full"
                        onClick={() => setIsPlaying(!isPlaying)}
                      >
                        {isPlaying ? (
                          <Pause className="w-5 h-5" />
                        ) : (
                          <Play className="w-5 h-5 ml-0.5" />
                        )}
                      </Button>
                      <div className="flex-1 space-y-2">
                        <Slider defaultValue={[35]} max={100} />
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>1:35</span>
                          <span>{selectedCall.duration}</span>
                        </div>
                      </div>
                      <Button size="icon" variant="ghost">
                        <Volume2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <Tabs defaultValue="scoring">
                    <TabsList>
                      <TabsTrigger value="scoring">
                        <Star className="w-4 h-4 mr-2" />
                        Scoring
                      </TabsTrigger>
                      <TabsTrigger value="transcript">
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Transcript
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="scoring" className="mt-4 space-y-6">
                      {/* Scoring Categories */}
                      <div className="space-y-4">
                        {[
                          { key: "greeting", label: "Greeting & Introduction" },
                          { key: "clarity", label: "Clarity & Communication" },
                          { key: "persuasion", label: "Persuasion & Value" },
                          { key: "objectionHandling", label: "Objection Handling" },
                          { key: "closing", label: "Closing & CTA" },
                        ].map((category) => (
                          <div key={category.key} className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Label>{category.label}</Label>
                              <span className="text-sm font-medium">
                                {scores[category.key as keyof typeof scores]}%
                              </span>
                            </div>
                            <Slider
                              value={[scores[category.key as keyof typeof scores]]}
                              onValueChange={([value]) =>
                                setScores((prev) => ({ ...prev, [category.key]: value }))
                              }
                              max={100}
                              step={5}
                            />
                          </div>
                        ))}
                      </div>

                      {/* Overall Score */}
                      <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Overall Score</span>
                          <span
                            className={`text-3xl font-bold ${
                              overallScore >= 80
                                ? "text-emerald-500"
                                : overallScore >= 60
                                ? "text-amber-500"
                                : "text-red-500"
                            }`}
                          >
                            {overallScore}%
                          </span>
                        </div>
                        <Progress value={overallScore} className="mt-2" />
                      </div>

                      {/* Feedback */}
                      <div className="space-y-2">
                        <Label>Feedback & Notes</Label>
                        <Textarea
                          placeholder="Add your feedback for this call..."
                          value={feedback}
                          onChange={(e) => setFeedback(e.target.value)}
                          className="min-h-[100px]"
                        />
                      </div>

                      {/* Quick Actions */}
                      <div className="flex items-center gap-2">
                        <Button variant="outline" className="flex-1">
                          <ThumbsDown className="w-4 h-4 mr-2" />
                          Needs Improvement
                        </Button>
                        <Button variant="outline" className="flex-1">
                          <ThumbsUp className="w-4 h-4 mr-2" />
                          Good Example
                        </Button>
                      </div>

                      {/* Submit */}
                      <Button className="w-full">
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Submit Review
                      </Button>
                    </TabsContent>

                    <TabsContent value="transcript" className="mt-4">
                      <ScrollArea className="h-[400px]">
                        <div className="space-y-4">
                          {[
                            { speaker: "AI", text: "Hello, this is Sarah from Al Ain Motors. Am I speaking with Mr. Ahmed?", time: "0:00" },
                            { speaker: "Customer", text: "Yes, this is Ahmed speaking.", time: "0:05" },
                            { speaker: "AI", text: "Great! I'm calling regarding your Toyota Land Cruiser. Our records show it's due for a routine service. Would you be available to bring it in this week?", time: "0:08" },
                            { speaker: "Customer", text: "Oh yes, I was planning to bring it in. What days do you have available?", time: "0:25" },
                            { speaker: "AI", text: "We have openings on Tuesday and Thursday morning. We also have a special 15% discount on all services this month. Which day works better for you?", time: "0:32" },
                            { speaker: "Customer", text: "Thursday morning sounds good. What time?", time: "0:50" },
                            { speaker: "AI", text: "How about 9 AM? That way you can use our complimentary shuttle service if needed.", time: "0:55" },
                            { speaker: "Customer", text: "Perfect, book me in for Thursday at 9.", time: "1:05" },
                            { speaker: "AI", text: "Excellent! I've scheduled your appointment for Thursday at 9 AM. You'll receive a confirmation SMS shortly. Is there anything else I can help you with?", time: "1:10" },
                            { speaker: "Customer", text: "No, that's all. Thank you!", time: "1:25" },
                            { speaker: "AI", text: "Thank you for choosing Al Ain Motors, Mr. Ahmed. We look forward to seeing you on Thursday. Have a great day!", time: "1:28" },
                          ].map((message, index) => (
                            <div
                              key={index}
                              className={`flex gap-3 ${
                                message.speaker === "AI" ? "" : "flex-row-reverse"
                              }`}
                            >
                              <Avatar className="h-8 w-8 shrink-0">
                                <AvatarFallback className="text-xs">
                                  {message.speaker === "AI" ? "AI" : "C"}
                                </AvatarFallback>
                              </Avatar>
                              <div
                                className={`max-w-[80%] p-3 rounded-lg ${
                                  message.speaker === "AI"
                                    ? "bg-primary/10"
                                    : "bg-muted/50"
                                }`}
                              >
                                <p className="text-sm">{message.text}</p>
                                <span className="text-xs text-muted-foreground mt-1 block">
                                  {message.time}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            ) : (
              <div className="h-full flex items-center justify-center border border-dashed border-border/50 rounded-lg">
                <div className="text-center text-muted-foreground">
                  <Eye className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="font-medium">Select a call to review</p>
                  <p className="text-sm">Choose from the list to start scoring</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.main>
    </div>
  );
};

export default QA;
