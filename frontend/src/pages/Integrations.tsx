import { useState } from "react";
import { motion } from "framer-motion";
import {
  Plug,
  Check,
  X,
  RefreshCw,
  ExternalLink,
  Key,
  Database,
  Mic,
  Bot,
  FileSpreadsheet,
  Settings,
  AlertCircle,
  CheckCircle,
  Loader2,
  Copy,
  Eye,
  EyeOff,
  TestTube,
  Link,
  Unlink,
  Zap,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
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
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  status: "connected" | "disconnected" | "error";
  category: "ai" | "voice" | "data" | "communication";
  lastSync?: string;
  config?: Record<string, string>;
}

const integrations: Integration[] = [
  {
    id: "elevenlabs",
    name: "ElevenLabs",
    description: "AI voice synthesis for natural-sounding calls",
    icon: Mic,
    status: "connected",
    category: "voice",
    lastSync: "2 mins ago",
    config: {
      apiKey: "sk-el-****************************",
      voiceId: "rachel_default",
      model: "eleven_turbo_v2",
    },
  },
  {
    id: "claude",
    name: "Claude AI",
    description: "Anthropic's AI for intelligent conversations",
    icon: Bot,
    status: "connected",
    category: "ai",
    lastSync: "Just now",
    config: {
      apiKey: "sk-ant-****************************",
      model: "claude-3-sonnet",
      maxTokens: "4096",
    },
  },
  {
    id: "google-sheets",
    name: "Google Sheets",
    description: "Import leads and export call data",
    icon: FileSpreadsheet,
    status: "connected",
    category: "data",
    lastSync: "5 mins ago",
    config: {
      serviceAccount: "voiceops@project.iam.gserviceaccount.com",
      defaultSheet: "Leads Database 2024",
    },
  },
  {
    id: "openai",
    name: "OpenAI GPT",
    description: "Alternative AI model for conversations",
    icon: Zap,
    status: "disconnected",
    category: "ai",
  },
  {
    id: "twilio",
    name: "Twilio",
    description: "Alternative voice infrastructure",
    icon: Mic,
    status: "disconnected",
    category: "voice",
  },
  {
    id: "crm",
    name: "CRM System",
    description: "Sync customer data with your CRM",
    icon: Database,
    status: "error",
    category: "data",
    lastSync: "Failed 1 hour ago",
  },
];

const statusConfig = {
  connected: {
    label: "Connected",
    color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
    icon: CheckCircle,
  },
  disconnected: {
    label: "Disconnected",
    color: "bg-gray-500/10 text-gray-600 border-gray-500/20",
    icon: X,
  },
  error: {
    label: "Error",
    color: "bg-red-500/10 text-red-600 border-red-500/20",
    icon: AlertCircle,
  },
};

const Integrations = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    // Simulate API test
    setTimeout(() => {
      setIsTesting(false);
      setTestResult("success");
    }, 2000);
  };

  const connectedCount = integrations.filter((i) => i.status === "connected").length;
  const errorCount = integrations.filter((i) => i.status === "error").length;

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
            <h1 className="text-2xl font-semibold text-foreground">Integrations</h1>
            <p className="text-muted-foreground text-sm">
              Manage your connected services and API keys
            </p>
          </div>
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync All
          </Button>
        </div>

        {/* Stats */}
        <motion.div
          className="grid grid-cols-4 gap-4 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {[
            { label: "Connected", value: connectedCount, icon: CheckCircle, color: "text-emerald-500" },
            { label: "Disconnected", value: integrations.length - connectedCount - errorCount, icon: Unlink, color: "text-gray-500" },
            { label: "Errors", value: errorCount, icon: AlertCircle, color: "text-red-500" },
            { label: "Total", value: integrations.length, icon: Plug, color: "text-primary" },
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

        <Tabs defaultValue="all">
          <TabsList className="mb-6">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="ai">AI Models</TabsTrigger>
            <TabsTrigger value="voice">Voice</TabsTrigger>
            <TabsTrigger value="data">Data</TabsTrigger>
          </TabsList>

          {["all", "ai", "voice", "data"].map((category) => (
            <TabsContent key={category} value={category}>
              <motion.div
                className="grid grid-cols-2 gap-4"
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
              >
                {integrations
                  .filter((i) => category === "all" || i.category === category)
                  .map((integration) => {
                    const StatusIcon = statusConfig[integration.status].icon;
                    return (
                      <motion.div key={integration.id} variants={staggerItem}>
                        <Card className="border-border/50 hover:border-primary/30 transition-colors">
                          <CardHeader className="pb-3">
                            <div className="flex items-start justify-between">
                              <div className="flex items-center gap-3">
                                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                                  <integration.icon className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                  <CardTitle className="text-base">{integration.name}</CardTitle>
                                  <CardDescription className="text-sm">
                                    {integration.description}
                                  </CardDescription>
                                </div>
                              </div>
                              <Badge variant="outline" className={statusConfig[integration.status].color}>
                                <StatusIcon className="w-3 h-3 mr-1" />
                                {statusConfig[integration.status].label}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent className="pb-3">
                            {integration.lastSync && (
                              <p className="text-xs text-muted-foreground">
                                Last sync: {integration.lastSync}
                              </p>
                            )}
                          </CardContent>
                          <CardFooter className="border-t pt-3">
                            <div className="flex items-center justify-between w-full">
                              <div className="flex items-center gap-2">
                                {integration.status === "connected" ? (
                                  <>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => setSelectedIntegration(integration)}
                                    >
                                      <Settings className="w-4 h-4 mr-2" />
                                      Configure
                                    </Button>
                                    <Button variant="ghost" size="sm">
                                      <Unlink className="w-4 h-4 mr-2" />
                                      Disconnect
                                    </Button>
                                  </>
                                ) : (
                                  <Dialog>
                                    <DialogTrigger asChild>
                                      <Button size="sm">
                                        <Link className="w-4 h-4 mr-2" />
                                        Connect
                                      </Button>
                                    </DialogTrigger>
                                    <DialogContent>
                                      <DialogHeader>
                                        <DialogTitle>Connect {integration.name}</DialogTitle>
                                        <DialogDescription>
                                          Enter your API credentials to connect
                                        </DialogDescription>
                                      </DialogHeader>
                                      <div className="space-y-4 py-4">
                                        <div className="space-y-2">
                                          <Label>API Key</Label>
                                          <div className="relative">
                                            <Input
                                              type={showApiKey ? "text" : "password"}
                                              placeholder="Enter your API key"
                                            />
                                            <Button
                                              variant="ghost"
                                              size="icon"
                                              className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                                              onClick={() => setShowApiKey(!showApiKey)}
                                            >
                                              {showApiKey ? (
                                                <EyeOff className="w-4 h-4" />
                                              ) : (
                                                <Eye className="w-4 h-4" />
                                              )}
                                            </Button>
                                          </div>
                                        </div>
                                      </div>
                                      <DialogFooter>
                                        <Button variant="outline">Cancel</Button>
                                        <Button>Connect</Button>
                                      </DialogFooter>
                                    </DialogContent>
                                  </Dialog>
                                )}
                              </div>
                              <Button variant="ghost" size="icon" asChild>
                                <a href="#" target="_blank">
                                  <ExternalLink className="w-4 h-4" />
                                </a>
                              </Button>
                            </div>
                          </CardFooter>
                        </Card>
                      </motion.div>
                    );
                  })}
              </motion.div>
            </TabsContent>
          ))}
        </Tabs>

        {/* Configuration Dialog */}
        <Dialog
          open={!!selectedIntegration}
          onOpenChange={() => setSelectedIntegration(null)}
        >
          <DialogContent className="sm:max-w-[500px]">
            {selectedIntegration && (
              <>
                <DialogHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <selectedIntegration.icon className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <DialogTitle>{selectedIntegration.name} Settings</DialogTitle>
                      <DialogDescription>Configure your integration settings</DialogDescription>
                    </div>
                  </div>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  {selectedIntegration.config &&
                    Object.entries(selectedIntegration.config).map(([key, value]) => (
                      <div key={key} className="space-y-2">
                        <Label className="capitalize">{key.replace(/([A-Z])/g, " $1").trim()}</Label>
                        <div className="relative">
                          <Input
                            type={key.includes("Key") || key.includes("key") ? (showApiKey ? "text" : "password") : "text"}
                            defaultValue={value}
                          />
                          {(key.includes("Key") || key.includes("key")) && (
                            <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => setShowApiKey(!showApiKey)}
                              >
                                {showApiKey ? (
                                  <EyeOff className="w-4 h-4" />
                                ) : (
                                  <Eye className="w-4 h-4" />
                                )}
                              </Button>
                              <Button variant="ghost" size="icon" className="h-7 w-7">
                                <Copy className="w-4 h-4" />
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}

                  {/* Test Connection */}
                  <div className="pt-4 border-t">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleTestConnection}
                      disabled={isTesting}
                    >
                      {isTesting ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <TestTube className="w-4 h-4 mr-2" />
                      )}
                      Test Connection
                    </Button>
                    {testResult === "success" && (
                      <div className="flex items-center gap-2 mt-2 text-sm text-emerald-600">
                        <CheckCircle className="w-4 h-4" />
                        Connection successful!
                      </div>
                    )}
                    {testResult === "error" && (
                      <div className="flex items-center gap-2 mt-2 text-sm text-red-600">
                        <AlertCircle className="w-4 h-4" />
                        Connection failed. Check your credentials.
                      </div>
                    )}
                  </div>

                  {/* Additional Settings */}
                  <div className="space-y-3 pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Auto-sync</Label>
                        <p className="text-xs text-muted-foreground">
                          Automatically sync data every hour
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Error notifications</Label>
                        <p className="text-xs text-muted-foreground">
                          Get notified when sync fails
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setSelectedIntegration(null)}>
                    Cancel
                  </Button>
                  <Button onClick={() => setSelectedIntegration(null)}>Save Changes</Button>
                </DialogFooter>
              </>
            )}
          </DialogContent>
        </Dialog>
      </motion.main>
    </div>
  );
};

export default Integrations;
