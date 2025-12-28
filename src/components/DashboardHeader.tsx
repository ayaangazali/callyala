import { Plus, Upload, Play, Square, Download, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function DashboardHeader() {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Overview</h1>
        <p className="text-muted-foreground mt-1">Monitor your voice agent performance and call outcomes.</p>
      </div>
      
      <div className="flex items-center gap-3">
        {/* Date Range Selector */}
        <Select defaultValue="today">
          <SelectTrigger className="w-[140px]">
            <Calendar className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Select range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Today</SelectItem>
            <SelectItem value="yesterday">Yesterday</SelectItem>
            <SelectItem value="week">This Week</SelectItem>
            <SelectItem value="month">This Month</SelectItem>
          </SelectContent>
        </Select>

        {/* Branch Selector */}
        <Select defaultValue="dubai">
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Select branch" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="dubai">Dubai Branch</SelectItem>
            <SelectItem value="abudhabi">Abu Dhabi Branch</SelectItem>
            <SelectItem value="sharjah">Sharjah Branch</SelectItem>
            <SelectItem value="all">All Branches</SelectItem>
          </SelectContent>
        </Select>

        <div className="h-6 w-px bg-border mx-1"></div>

        <Button variant="outline" className="gap-2">
          <Upload className="w-4 h-4" />
          Upload List
        </Button>
        <Button variant="outline" className="gap-2">
          <Download className="w-4 h-4" />
          Export
        </Button>
        <Button variant="secondary" className="gap-2">
          <Plus className="w-4 h-4" />
          New Campaign
        </Button>
        <Button className="gap-2">
          <Play className="w-4 h-4" />
          Start Calling
        </Button>
      </div>
    </div>
  );
}
