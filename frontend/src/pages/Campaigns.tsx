import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Megaphone,
  Plus,
  Search,
  MoreHorizontal,
  Play,
  Pause,
  Edit,
  Trash2,
  Copy,
  BarChart3,
  Users,
  Phone,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronRight,
  FileSpreadsheet,
  Settings,
  Zap,
  Loader2,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
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
import { Switch } from "@/components/ui/switch";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";
import { useCampaigns, useCreateCampaign, useStartCampaign, usePauseCampaign, useDeleteCampaign } from "@/hooks/use-api";
import { useToast } from "@/hooks/use-toast";

interface Campaign {
  id: string;
  name: string;
  description: string;
  status: "draft" | "active" | "paused" | "completed";
  sheetId?: string;
  sheetName?: string;
  totalLeads: number;
  callsMade: number;
  booked: number;
  failed: number;
  successRate: number;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  script?: string;
  callsPerHour: number;
  retryAttempts: number;
}

const campaigns: Campaign[] = [
  {
    id: "camp-001",
    name: "January Service Pickup",
    description: "Notify customers their vehicles are ready for pickup",
    status: "active",
    sheetId: "1abc...",
    sheetName: "Service Ready - Jan 2024",
    totalLeads: 250,
    callsMade: 127,
    booked: 89,
    failed: 12,
    successRate: 70,
    createdAt: "2024-01-10",
    startedAt: "2024-01-15",
    callsPerHour: 30,
    retryAttempts: 2,
  },
  {
    id: "camp-002",
    name: "Service Due Reminder",
    description: "Remind customers about upcoming service appointments",
    status: "paused",
    sheetId: "2def...",
    sheetName: "Service Due - Week 3",
    totalLeads: 180,
    callsMade: 95,
    booked: 45,
    failed: 20,
    successRate: 47,
    createdAt: "2024-01-08",
    startedAt: "2024-01-12",
    callsPerHour: 25,
    retryAttempts: 3,
  },
  {
    id: "camp-003",
    name: "New Year Promotion",
    description: "Offer exclusive new year deals on service packages",
    status: "completed",
    sheetId: "3ghi...",
    sheetName: "Promo Leads 2024",
    totalLeads: 500,
    callsMade: 500,
    booked: 156,
    failed: 89,
    successRate: 31,
    createdAt: "2024-01-01",
    startedAt: "2024-01-02",
    completedAt: "2024-01-10",
    callsPerHour: 40,
    retryAttempts: 2,
  },
  {
    id: "camp-004",
    name: "VIP Customer Outreach",
    description: "Personal calls to high-value customers",
    status: "draft",
    totalLeads: 50,
    callsMade: 0,
    booked: 0,
    failed: 0,
    successRate: 0,
    createdAt: "2024-01-14",
    callsPerHour: 10,
    retryAttempts: 1,
  },
];

const statusConfig = {
  draft: { label: "Draft", color: "bg-gray-500/10 text-gray-600 border-gray-500/20", icon: Edit },
  active: { label: "Active", color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20", icon: Play },
  paused: { label: "Paused", color: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20", icon: Pause },
  completed: { label: "Completed", color: "bg-blue-500/10 text-blue-600 border-blue-500/20", icon: CheckCircle },
};

const Campaigns = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    name: "",
    description: "",
    sheetUrl: "",
    callsPerHour: 30,
    retryAttempts: 2,
    useAI: true,
  });

  const filteredCampaigns = campaigns.filter((campaign) => {
    const matchesSearch =
      campaign.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      campaign.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || campaign.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: campaigns.length,
    active: campaigns.filter((c) => c.status === "active").length,
    totalLeads: campaigns.reduce((sum, c) => sum + c.totalLeads, 0),
    totalBooked: campaigns.reduce((sum, c) => sum + c.booked, 0),
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
            <h1 className="text-2xl font-semibold text-foreground">Campaigns</h1>
            <p className="text-muted-foreground text-sm">
              Create and manage your calling campaigns
            </p>
          </div>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                New Campaign
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Create New Campaign</DialogTitle>
                <DialogDescription>
                  Set up a new AI calling campaign from your Google Sheet
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Campaign Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., January Service Pickup"
                    value={newCampaign.name}
                    onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Brief description of the campaign purpose..."
                    value={newCampaign.description}
                    onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sheet">Google Sheet URL</Label>
                  <Input
                    id="sheet"
                    placeholder="https://docs.google.com/spreadsheets/d/..."
                    value={newCampaign.sheetUrl}
                    onChange={(e) => setNewCampaign({ ...newCampaign, sheetUrl: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground">
                    Sheet must have columns: Name, Phone, Vehicle, Plate
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="callsPerHour">Calls per Hour</Label>
                    <Input
                      id="callsPerHour"
                      type="number"
                      value={newCampaign.callsPerHour}
                      onChange={(e) => setNewCampaign({ ...newCampaign, callsPerHour: parseInt(e.target.value) })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="retryAttempts">Retry Attempts</Label>
                    <Input
                      id="retryAttempts"
                      type="number"
                      value={newCampaign.retryAttempts}
                      onChange={(e) => setNewCampaign({ ...newCampaign, retryAttempts: parseInt(e.target.value) })}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-primary" />
                    <div>
                      <p className="text-sm font-medium">AI-Powered Calls</p>
                      <p className="text-xs text-muted-foreground">Use Claude + ElevenLabs</p>
                    </div>
                  </div>
                  <Switch
                    checked={newCampaign.useAI}
                    onCheckedChange={(checked) => setNewCampaign({ ...newCampaign, useAI: checked })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={() => setIsCreateOpen(false)}>
                  Create Campaign
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats Cards */}
        <motion.div
          className="grid grid-cols-4 gap-4 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {[
            { label: "Total Campaigns", value: stats.total, icon: Megaphone },
            { label: "Active", value: stats.active, icon: Play, color: "text-emerald-500" },
            { label: "Total Leads", value: stats.totalLeads.toLocaleString(), icon: Users },
            { label: "Total Booked", value: stats.totalBooked, icon: Calendar, color: "text-emerald-500" },
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

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search campaigns..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="paused">Paused</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Campaigns Grid */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-4"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          <AnimatePresence>
            {filteredCampaigns.map((campaign) => {
              const StatusIcon = statusConfig[campaign.status].icon;
              const progress = campaign.totalLeads > 0 
                ? (campaign.callsMade / campaign.totalLeads) * 100 
                : 0;

              return (
                <motion.div
                  key={campaign.id}
                  variants={staggerItem}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                >
                  <Card className="border-border/50 hover:border-border hover:shadow-md transition-all group">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <CardTitle className="text-lg">{campaign.name}</CardTitle>
                            <Badge variant="outline" className={statusConfig[campaign.status].color}>
                              <StatusIcon className="w-3 h-3 mr-1" />
                              {statusConfig[campaign.status].label}
                            </Badge>
                          </div>
                          <CardDescription>{campaign.description}</CardDescription>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            {campaign.status === "draft" && (
                              <DropdownMenuItem>
                                <Play className="w-4 h-4 mr-2" />
                                Start Campaign
                              </DropdownMenuItem>
                            )}
                            {campaign.status === "active" && (
                              <DropdownMenuItem>
                                <Pause className="w-4 h-4 mr-2" />
                                Pause Campaign
                              </DropdownMenuItem>
                            )}
                            {campaign.status === "paused" && (
                              <DropdownMenuItem>
                                <Play className="w-4 h-4 mr-2" />
                                Resume Campaign
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuItem>
                              <Edit className="w-4 h-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Copy className="w-4 h-4 mr-2" />
                              Duplicate
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <BarChart3 className="w-4 h-4 mr-2" />
                              View Analytics
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive">
                              <Trash2 className="w-4 h-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Progress */}
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="font-medium">{campaign.callsMade} / {campaign.totalLeads} calls</span>
                        </div>
                        <Progress value={progress} className="h-2" />
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-4 gap-2">
                        <div className="text-center p-2 rounded-lg bg-muted/50">
                          <p className="text-lg font-semibold">{campaign.totalLeads}</p>
                          <p className="text-xs text-muted-foreground">Leads</p>
                        </div>
                        <div className="text-center p-2 rounded-lg bg-emerald-500/10">
                          <p className="text-lg font-semibold text-emerald-600">{campaign.booked}</p>
                          <p className="text-xs text-muted-foreground">Booked</p>
                        </div>
                        <div className="text-center p-2 rounded-lg bg-red-500/10">
                          <p className="text-lg font-semibold text-red-600">{campaign.failed}</p>
                          <p className="text-xs text-muted-foreground">Failed</p>
                        </div>
                        <div className="text-center p-2 rounded-lg bg-blue-500/10">
                          <p className="text-lg font-semibold text-blue-600">{campaign.successRate}%</p>
                          <p className="text-xs text-muted-foreground">Success</p>
                        </div>
                      </div>

                      {/* Sheet Info */}
                      {campaign.sheetName && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <FileSpreadsheet className="w-4 h-4" />
                          <span className="truncate">{campaign.sheetName}</span>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center justify-between pt-2 border-t border-border/50">
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {campaign.callsPerHour}/hr
                          </span>
                          <span className="flex items-center gap-1">
                            <Phone className="w-3 h-3" />
                            {campaign.retryAttempts} retries
                          </span>
                        </div>
                        <Button variant="ghost" size="sm" className="text-primary">
                          View Details
                          <ChevronRight className="w-4 h-4 ml-1" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>
      </motion.main>
    </div>
  );
};

export default Campaigns;
