import { X, Play, Pause, Volume2, ThumbsUp, Meh, ThumbsDown, Tag, Clock, FileText, Bot, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";

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

interface CallDetailDrawerProps {
  call: Call | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const sentimentIcons = {
  positive: ThumbsUp,
  neutral: Meh,
  negative: ThumbsDown,
};

const sentimentLabels = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
};

const sentimentColors = {
  positive: "text-success bg-success/10",
  neutral: "text-muted-foreground bg-muted",
  negative: "text-destructive bg-destructive/10",
};

export function CallDetailDrawer({ call, open, onOpenChange }: CallDetailDrawerProps) {
  const [isPlaying, setIsPlaying] = useState(false);

  if (!call) return null;

  const SentimentIcon = sentimentIcons[call.sentiment];

  const transcript = `Agent: Hello, this is an automated call from Al Futtaim Motors. Am I speaking with ${call.customerName}?

Customer: Yes, speaking.

Agent: Great! I'm calling to let you know that your ${call.vehicleModel} is ready for pickup. Would you like to schedule a pickup time?

Customer: Yes, that would be great. What times are available?

Agent: We have availability tomorrow between 8 AM and 4 PM. What time works best for you?

Customer: How about 10 AM?

Agent: Perfect. I've scheduled your pickup for tomorrow at 10 AM. You'll receive a confirmation SMS shortly. Is there anything else I can help you with?

Customer: No, that's all. Thank you.

Agent: Thank you for choosing Al Futtaim Motors. Have a great day!`;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[480px] sm:max-w-[480px] overflow-y-auto">
        <SheetHeader className="pb-4">
          <SheetTitle className="text-left">Call Details</SheetTitle>
        </SheetHeader>

        {/* Customer Info */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">{call.customerName}</h3>
            <p className="text-sm text-muted-foreground">{call.phone}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-secondary/50 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Vehicle</p>
              <p className="text-sm font-medium text-foreground">{call.vehicleModel}</p>
              <p className="text-xs text-muted-foreground">{call.plate}</p>
            </div>
            <div className="bg-secondary/50 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Purpose</p>
              <p className="text-sm font-medium text-foreground">{call.purpose}</p>
            </div>
          </div>

          <Separator />

          {/* Audio Playback */}
          <div>
            <h4 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
              <Volume2 className="w-4 h-4" />
              Recording
            </h4>
            <div className="bg-secondary/50 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="icon"
                  className="h-10 w-10 rounded-full"
                  onClick={() => setIsPlaying(!isPlaying)}
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                </Button>
                <div className="flex-1">
                  <div className="h-2 bg-border rounded-full overflow-hidden">
                    <div className="h-full w-[35%] bg-primary rounded-full"></div>
                  </div>
                  <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                    <span>0:35</span>
                    <span>{call.duration}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Extracted Fields */}
          <div>
            <h4 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Extracted Information
            </h4>
            <div className="space-y-2">
              {call.bookedTime && (
                <div className="flex items-center justify-between bg-success/5 border border-success/20 rounded-lg px-3 py-2">
                  <span className="text-sm text-foreground">Pickup Scheduled</span>
                  <span className="text-sm font-medium text-success">{call.bookedTime}</span>
                </div>
              )}
              <div className="flex items-center justify-between bg-secondary/50 rounded-lg px-3 py-2">
                <span className="text-sm text-foreground">Confirmation</span>
                <span className="text-sm font-medium text-foreground">Yes</span>
              </div>
              <div className="flex items-center justify-between bg-secondary/50 rounded-lg px-3 py-2">
                <span className="text-sm text-foreground">Sentiment</span>
                <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full ${sentimentColors[call.sentiment]}`}>
                  <SentimentIcon className="w-3 h-3" />
                  <span className="text-xs font-medium">{sentimentLabels[call.sentiment]}</span>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Transcript */}
          <div>
            <h4 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Transcript
            </h4>
            <div className="bg-secondary/30 rounded-lg p-4 max-h-[300px] overflow-y-auto">
              <pre className="text-sm text-foreground whitespace-pre-wrap font-sans leading-relaxed">
                {transcript}
              </pre>
            </div>
          </div>

          <Separator />

          {/* Meta Info */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Bot className="w-4 h-4" />
              <span>Script v3.2</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="w-4 h-4" />
              <span>{call.timestamp}</span>
            </div>
          </div>

          {/* Tags */}
          <div>
            <h4 className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
              <Tag className="w-4 h-4" />
              Tags
            </h4>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs px-2 py-1 rounded-full bg-accent/20 text-accent">pickup-scheduled</span>
              <span className="text-xs px-2 py-1 rounded-full bg-secondary text-secondary-foreground">first-attempt</span>
              <span className="text-xs px-2 py-1 rounded-full bg-success/10 text-success">successful</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            <Button variant="outline" className="flex-1">Add Note</Button>
            <Button variant="outline" className="flex-1">Flag for Review</Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
