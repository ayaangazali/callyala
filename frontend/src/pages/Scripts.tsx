import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Plus,
  Search,
  Edit,
  Copy,
  Trash2,
  MoreHorizontal,
  Play,
  Pause,
  Sparkles,
  MessageSquare,
  Mic,
  Volume2,
  Clock,
  Save,
  RefreshCw,
  Wand2,
  ChevronDown,
  Check,
  Code,
  Settings2,
  Zap,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";

interface Script {
  id: string;
  name: string;
  type: "service-reminder" | "appointment-confirm" | "follow-up" | "promotion" | "custom";
  language: "en" | "ar" | "mixed";
  prompt: string;
  variables: string[];
  voiceSettings: {
    voice: string;
    speed: number;
    pitch: number;
  };
  usageCount: number;
  lastUsed: string;
  status: "active" | "draft" | "archived";
}

const scripts: Script[] = [
  {
    id: "script-001",
    name: "Service Reminder - Standard",
    type: "service-reminder",
    language: "en",
    prompt: `You are a professional service advisor at a car dealership. Call the customer to remind them about their upcoming service appointment.

Customer Name: {customer_name}
Vehicle: {vehicle_make} {vehicle_model}
Service Due: {service_type}
Last Service: {last_service_date}

Key points:
- Be polite and professional
- Confirm their availability
- Mention any current promotions
- Offer to schedule if not already scheduled`,
    variables: ["customer_name", "vehicle_make", "vehicle_model", "service_type", "last_service_date"],
    voiceSettings: { voice: "Rachel", speed: 1.0, pitch: 1.0 },
    usageCount: 245,
    lastUsed: "Today",
    status: "active",
  },
  {
    id: "script-002",
    name: "Appointment Confirmation",
    type: "appointment-confirm",
    language: "en",
    prompt: `You are calling to confirm an upcoming service appointment.

Customer: {customer_name}
Appointment: {appointment_date} at {appointment_time}
Service: {service_type}
Location: {dealership_location}

Instructions:
- Confirm the appointment details
- Ask if they need any changes
- Remind them to bring their keys and any documents
- Provide estimated duration`,
    variables: ["customer_name", "appointment_date", "appointment_time", "service_type", "dealership_location"],
    voiceSettings: { voice: "Marcus", speed: 1.1, pitch: 1.0 },
    usageCount: 189,
    lastUsed: "Today",
    status: "active",
  },
  {
    id: "script-003",
    name: "Arabic Service Reminder",
    type: "service-reminder",
    language: "ar",
    prompt: `أنت مستشار خدمة محترف في وكالة سيارات. اتصل بالعميل لتذكيره بموعد الصيانة القادم.

اسم العميل: {customer_name}
السيارة: {vehicle_make} {vehicle_model}
نوع الخدمة: {service_type}

التعليمات:
- كن مهذباً ومحترفاً
- تأكد من توفر العميل
- اذكر أي عروض ترويجية حالية`,
    variables: ["customer_name", "vehicle_make", "vehicle_model", "service_type"],
    voiceSettings: { voice: "Fatima", speed: 0.95, pitch: 1.0 },
    usageCount: 78,
    lastUsed: "Yesterday",
    status: "active",
  },
  {
    id: "script-004",
    name: "Follow-Up - Post Service",
    type: "follow-up",
    language: "en",
    prompt: `You are calling to follow up after a recent service visit.

Customer: {customer_name}
Service Completed: {service_date}
Services Performed: {services_list}

Objectives:
- Ask about their satisfaction with the service
- Inquire if everything is working properly
- Address any concerns they might have
- Thank them for their business`,
    variables: ["customer_name", "service_date", "services_list"],
    voiceSettings: { voice: "Rachel", speed: 1.0, pitch: 1.0 },
    usageCount: 156,
    lastUsed: "2 days ago",
    status: "active",
  },
  {
    id: "script-005",
    name: "Seasonal Promotion",
    type: "promotion",
    language: "mixed",
    prompt: `Call customers about the current seasonal promotion.

Customer: {customer_name}
Promotion: {promotion_name}
Discount: {discount_percentage}%
Valid Until: {expiry_date}

Approach:
- Greet warmly in their preferred language
- Present the promotion benefits
- Create urgency with expiry date
- Offer to schedule an appointment`,
    variables: ["customer_name", "promotion_name", "discount_percentage", "expiry_date"],
    voiceSettings: { voice: "Marcus", speed: 1.0, pitch: 1.0 },
    usageCount: 45,
    lastUsed: "3 days ago",
    status: "draft",
  },
];

const typeConfig = {
  "service-reminder": { label: "Service Reminder", color: "bg-blue-500/10 text-blue-600 border-blue-500/20", icon: Clock },
  "appointment-confirm": { label: "Appointment", color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20", icon: Check },
  "follow-up": { label: "Follow-Up", color: "bg-purple-500/10 text-purple-600 border-purple-500/20", icon: MessageSquare },
  "promotion": { label: "Promotion", color: "bg-amber-500/10 text-amber-600 border-amber-500/20", icon: Zap },
  "custom": { label: "Custom", color: "bg-gray-500/10 text-gray-600 border-gray-500/20", icon: Code },
};

const voiceOptions = ["Rachel", "Marcus", "Fatima", "Ahmad", "Sarah", "James"];

const Scripts = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [selectedScript, setSelectedScript] = useState<Script | null>(null);
  const [editedPrompt, setEditedPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const filteredScripts = scripts.filter((script) => {
    const matchesSearch = script.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === "all" || script.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const handleGenerateWithAI = async () => {
    setIsGenerating(true);
    // Simulate AI generation
    setTimeout(() => {
      setEditedPrompt((prev) => prev + "\n\n[AI Enhanced] Added emotional intelligence cues and personalization markers for better customer engagement.");
      setIsGenerating(false);
    }, 2000);
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
            <h1 className="text-2xl font-semibold text-foreground">Scripts & Prompts</h1>
            <p className="text-muted-foreground text-sm">
              Manage AI voice agent scripts powered by Claude
            </p>
          </div>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Create Script
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Create New Script</DialogTitle>
                <DialogDescription>
                  Create a new AI voice script from scratch or use a template
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>Script Name</Label>
                  <Input placeholder="e.g., Service Reminder - VIP" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Type</Label>
                    <Select defaultValue="service-reminder">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(typeConfig).map(([key, config]) => (
                          <SelectItem key={key} value={key}>
                            {config.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Language</Label>
                    <Select defaultValue="en">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="ar">Arabic</SelectItem>
                        <SelectItem value="mixed">Mixed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Prompt</Label>
                    <Button variant="ghost" size="sm" className="h-7 text-xs">
                      <Sparkles className="w-3 h-3 mr-1" />
                      Generate with AI
                    </Button>
                  </div>
                  <Textarea
                    placeholder="Write your AI voice agent prompt here..."
                    className="min-h-[200px] font-mono text-sm"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={() => setShowCreateDialog(false)}>
                  Create Script
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats */}
        <motion.div
          className="grid grid-cols-4 gap-4 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {[
            { label: "Total Scripts", value: scripts.length, icon: FileText },
            { label: "Active Scripts", value: scripts.filter((s) => s.status === "active").length, icon: Check, color: "text-emerald-500" },
            { label: "Total Uses", value: scripts.reduce((sum, s) => sum + s.usageCount, 0), icon: Play },
            { label: "Languages", value: "3", icon: MessageSquare },
          ].map((stat) => (
            <motion.div key={stat.label} variants={staggerItem}>
              <Card className="border-border/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                      <p className={`text-2xl font-semibold ${stat.color || "text-foreground"}`}>
                        {stat.value}
                      </p>
                    </div>
                    <stat.icon className="w-8 h-8 text-muted-foreground/30" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-3 gap-6">
          {/* Scripts List */}
          <div className="col-span-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search scripts..."
                  className="pl-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-36">
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {Object.entries(typeConfig).map(([key, config]) => (
                    <SelectItem key={key} value={key}>
                      {config.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <ScrollArea className="h-[calc(100vh-300px)]">
              <div className="space-y-2">
                {filteredScripts.map((script) => {
                  const TypeIcon = typeConfig[script.type].icon;
                  return (
                    <motion.div key={script.id} variants={staggerItem}>
                      <Card
                        className={`cursor-pointer transition-all hover:border-primary/50 ${
                          selectedScript?.id === script.id ? "border-primary bg-primary/5" : "border-border/50"
                        }`}
                        onClick={() => {
                          setSelectedScript(script);
                          setEditedPrompt(script.prompt);
                        }}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <TypeIcon className="w-4 h-4 text-muted-foreground" />
                              <span className="font-medium text-sm">{script.name}</span>
                            </div>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                                <Button variant="ghost" size="icon" className="h-7 w-7">
                                  <MoreHorizontal className="w-4 h-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem>
                                  <Copy className="w-4 h-4 mr-2" />
                                  Duplicate
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <Edit className="w-4 h-4 mr-2" />
                                  Edit
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="text-destructive">
                                  <Trash2 className="w-4 h-4 mr-2" />
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline" className={typeConfig[script.type].color}>
                              {typeConfig[script.type].label}
                            </Badge>
                            <Badge variant="secondary" className="text-xs">
                              {script.language.toUpperCase()}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span>{script.usageCount} uses</span>
                            <span>Last: {script.lastUsed}</span>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </ScrollArea>
          </div>

          {/* Script Editor */}
          <div className="col-span-2">
            {selectedScript ? (
              <Card className="border-border/50 h-full">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{selectedScript.name}</CardTitle>
                      <CardDescription>
                        {selectedScript.variables.length} variables • Voice: {selectedScript.voiceSettings.voice}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Play className="w-4 h-4 mr-2" />
                        Test
                      </Button>
                      <Button size="sm">
                        <Save className="w-4 h-4 mr-2" />
                        Save
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <Tabs defaultValue="prompt">
                    <TabsList>
                      <TabsTrigger value="prompt">
                        <FileText className="w-4 h-4 mr-2" />
                        Prompt
                      </TabsTrigger>
                      <TabsTrigger value="voice">
                        <Mic className="w-4 h-4 mr-2" />
                        Voice Settings
                      </TabsTrigger>
                      <TabsTrigger value="variables">
                        <Code className="w-4 h-4 mr-2" />
                        Variables
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="prompt" className="mt-4">
                      <div className="space-y-4">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={handleGenerateWithAI}
                            disabled={isGenerating}
                          >
                            {isGenerating ? (
                              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <Wand2 className="w-4 h-4 mr-2" />
                            )}
                            Enhance with Claude
                          </Button>
                          <Button variant="outline" size="sm">
                            <Sparkles className="w-4 h-4 mr-2" />
                            Regenerate
                          </Button>
                        </div>
                        <Textarea
                          value={editedPrompt}
                          onChange={(e) => setEditedPrompt(e.target.value)}
                          className="min-h-[400px] font-mono text-sm"
                        />
                        <div className="text-xs text-muted-foreground">
                          Tip: Use {"{variable_name}"} syntax to insert dynamic content
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="voice" className="mt-4">
                      <div className="space-y-6">
                        <div className="space-y-3">
                          <Label>Voice</Label>
                          <Select defaultValue={selectedScript.voiceSettings.voice}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {voiceOptions.map((voice) => (
                                <SelectItem key={voice} value={voice}>
                                  {voice}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <Label>Speed</Label>
                            <span className="text-sm text-muted-foreground">
                              {selectedScript.voiceSettings.speed}x
                            </span>
                          </div>
                          <Slider
                            defaultValue={[selectedScript.voiceSettings.speed]}
                            min={0.5}
                            max={2}
                            step={0.1}
                          />
                        </div>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <Label>Pitch</Label>
                            <span className="text-sm text-muted-foreground">
                              {selectedScript.voiceSettings.pitch}x
                            </span>
                          </div>
                          <Slider
                            defaultValue={[selectedScript.voiceSettings.pitch]}
                            min={0.5}
                            max={2}
                            step={0.1}
                          />
                        </div>
                        <div className="pt-4 border-t">
                          <Button variant="outline" className="w-full">
                            <Volume2 className="w-4 h-4 mr-2" />
                            Preview Voice
                          </Button>
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="variables" className="mt-4">
                      <div className="space-y-4">
                        <p className="text-sm text-muted-foreground">
                          Variables are automatically extracted from your prompt. They will be replaced with actual data when making calls.
                        </p>
                        <div className="space-y-2">
                          {selectedScript.variables.map((variable) => (
                            <div
                              key={variable}
                              className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                            >
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="font-mono">
                                  {"{" + variable + "}"}
                                </Badge>
                              </div>
                              <Input
                                placeholder="Test value"
                                className="w-48 h-8 text-sm"
                              />
                            </div>
                          ))}
                        </div>
                        <Button variant="outline" size="sm">
                          <Plus className="w-4 h-4 mr-2" />
                          Add Variable
                        </Button>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            ) : (
              <div className="h-full flex items-center justify-center border border-dashed border-border/50 rounded-lg">
                <div className="text-center text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="font-medium">Select a script to edit</p>
                  <p className="text-sm">Choose from the list or create a new one</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.main>
    </div>
  );
};

export default Scripts;
