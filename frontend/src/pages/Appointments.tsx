import { useState } from "react";
import { motion } from "framer-motion";
import {
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  User,
  Car,
  Phone,
  Mail,
  MoreHorizontal,
  Plus,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  Filter,
} from "lucide-react";
import { format, addDays, startOfWeek, addWeeks, isSameDay, isToday } from "date-fns";
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
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";
import { cn } from "@/lib/utils";

interface Appointment {
  id: string;
  customerName: string;
  phone: string;
  email?: string;
  vehicleModel: string;
  plate: string;
  type: "pickup" | "service" | "consultation" | "test_drive";
  status: "confirmed" | "pending" | "completed" | "cancelled" | "no_show";
  date: Date;
  time: string;
  duration: number; // minutes
  notes?: string;
  bookedBy: "ai" | "human";
  campaign?: string;
}

const appointments: Appointment[] = [
  {
    id: "apt-001",
    customerName: "Ahmed Al-Mansour",
    phone: "+971 50 123 4567",
    email: "ahmed@email.com",
    vehicleModel: "Toyota Land Cruiser 2024",
    plate: "A 12345",
    type: "pickup",
    status: "confirmed",
    date: new Date(),
    time: "10:00 AM",
    duration: 30,
    notes: "Customer prefers morning appointments",
    bookedBy: "ai",
    campaign: "January Service Pickup",
  },
  {
    id: "apt-002",
    customerName: "Fatima Al-Hassan",
    phone: "+971 55 987 6543",
    vehicleModel: "Nissan Patrol 2023",
    plate: "B 54321",
    type: "service",
    status: "pending",
    date: new Date(),
    time: "2:00 PM",
    duration: 60,
    bookedBy: "human",
  },
  {
    id: "apt-003",
    customerName: "Mohammed Al-Rashid",
    phone: "+971 55 333 4444",
    vehicleModel: "Mercedes GLE 450",
    plate: "E 22222",
    type: "pickup",
    status: "confirmed",
    date: new Date(),
    time: "3:00 PM",
    duration: 30,
    bookedBy: "ai",
    campaign: "Service Follow-up",
  },
  {
    id: "apt-004",
    customerName: "Sarah Ahmed",
    phone: "+971 50 111 2222",
    vehicleModel: "BMW X5 2024",
    plate: "D 11111",
    type: "consultation",
    status: "confirmed",
    date: addDays(new Date(), 1),
    time: "11:00 AM",
    duration: 45,
    bookedBy: "ai",
  },
  {
    id: "apt-005",
    customerName: "Khalid Ibrahim",
    phone: "+971 52 456 7890",
    vehicleModel: "Lexus LX 600",
    plate: "C 98765",
    type: "test_drive",
    status: "pending",
    date: addDays(new Date(), 1),
    time: "4:00 PM",
    duration: 60,
    bookedBy: "human",
  },
  {
    id: "apt-006",
    customerName: "Layla Hassan",
    phone: "+971 50 555 6666",
    vehicleModel: "Audi Q7 2023",
    plate: "F 33333",
    type: "pickup",
    status: "cancelled",
    date: addDays(new Date(), -1),
    time: "9:00 AM",
    duration: 30,
    bookedBy: "ai",
    notes: "Customer rescheduled to next week",
  },
];

const typeConfig = {
  pickup: { label: "Pickup", color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20" },
  service: { label: "Service", color: "bg-blue-500/10 text-blue-600 border-blue-500/20" },
  consultation: { label: "Consultation", color: "bg-purple-500/10 text-purple-600 border-purple-500/20" },
  test_drive: { label: "Test Drive", color: "bg-orange-500/10 text-orange-600 border-orange-500/20" },
};

const statusConfig = {
  confirmed: { label: "Confirmed", color: "bg-emerald-500", icon: CheckCircle },
  pending: { label: "Pending", color: "bg-yellow-500", icon: AlertCircle },
  completed: { label: "Completed", color: "bg-blue-500", icon: CheckCircle },
  cancelled: { label: "Cancelled", color: "bg-red-500", icon: XCircle },
  no_show: { label: "No Show", color: "bg-gray-500", icon: XCircle },
};

const Appointments = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentWeek, setCurrentWeek] = useState(startOfWeek(new Date(), { weekStartsOn: 0 }));
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [view, setView] = useState<"week" | "list">("week");
  const [searchQuery, setSearchQuery] = useState("");

  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(currentWeek, i));

  const getAppointmentsForDate = (date: Date) => {
    return appointments.filter((apt) => isSameDay(apt.date, date));
  };

  const filteredAppointments = appointments.filter((apt) =>
    apt.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    apt.vehicleModel.toLowerCase().includes(searchQuery.toLowerCase()) ||
    apt.phone.includes(searchQuery)
  );

  const todayAppointments = appointments.filter((apt) => isToday(apt.date));
  const stats = {
    today: todayAppointments.length,
    confirmed: todayAppointments.filter((a) => a.status === "confirmed").length,
    pending: todayAppointments.filter((a) => a.status === "pending").length,
    aiBooked: appointments.filter((a) => a.bookedBy === "ai").length,
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
            <h1 className="text-2xl font-semibold text-foreground">Appointments</h1>
            <p className="text-muted-foreground text-sm">
              Manage scheduled pickups, services, and consultations
            </p>
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                New Appointment
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Schedule Appointment</DialogTitle>
                <DialogDescription>
                  Create a new appointment for a customer
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Customer Name</Label>
                    <Input placeholder="Full name" />
                  </div>
                  <div className="space-y-2">
                    <Label>Phone</Label>
                    <Input placeholder="+971 50 XXX XXXX" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Vehicle</Label>
                    <Input placeholder="Model" />
                  </div>
                  <div className="space-y-2">
                    <Label>Plate</Label>
                    <Input placeholder="Plate number" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Date</Label>
                    <Input type="date" />
                  </div>
                  <div className="space-y-2">
                    <Label>Time</Label>
                    <Input type="time" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pickup">Pickup</SelectItem>
                      <SelectItem value="service">Service</SelectItem>
                      <SelectItem value="consultation">Consultation</SelectItem>
                      <SelectItem value="test_drive">Test Drive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Textarea placeholder="Additional notes..." />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Schedule</Button>
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
            { label: "Today's Appointments", value: stats.today, icon: CalendarIcon },
            { label: "Confirmed", value: stats.confirmed, icon: CheckCircle, color: "text-emerald-500" },
            { label: "Pending", value: stats.pending, icon: AlertCircle, color: "text-yellow-500" },
            { label: "AI Booked", value: stats.aiBooked, icon: User, color: "text-primary" },
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

        {/* View Toggle & Filters */}
        <div className="flex items-center justify-between mb-4">
          <Tabs value={view} onValueChange={(v) => setView(v as "week" | "list")}>
            <TabsList>
              <TabsTrigger value="week">Week View</TabsTrigger>
              <TabsTrigger value="list">List View</TabsTrigger>
            </TabsList>
          </Tabs>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search..."
                className="pl-9 w-64"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Week View */}
        {view === "week" && (
          <Card className="border-border/50">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setCurrentWeek(addWeeks(currentWeek, -1))}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <CardTitle className="text-lg">
                    {format(currentWeek, "MMMM yyyy")}
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setCurrentWeek(addWeeks(currentWeek, 1))}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentWeek(startOfWeek(new Date(), { weekStartsOn: 0 }))}
                >
                  Today
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-2">
                {weekDays.map((day) => {
                  const dayAppointments = getAppointmentsForDate(day);
                  const isSelected = isSameDay(day, selectedDate);
                  const dayIsToday = isToday(day);

                  return (
                    <div
                      key={day.toISOString()}
                      className={cn(
                        "min-h-[120px] p-2 rounded-lg border cursor-pointer transition-all",
                        isSelected
                          ? "border-primary bg-primary/5"
                          : "border-border/50 hover:border-border",
                        dayIsToday && !isSelected && "bg-muted/50"
                      )}
                      onClick={() => setSelectedDate(day)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-muted-foreground">
                          {format(day, "EEE")}
                        </span>
                        <span
                          className={cn(
                            "text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full",
                            dayIsToday && "bg-primary text-primary-foreground"
                          )}
                        >
                          {format(day, "d")}
                        </span>
                      </div>
                      <div className="space-y-1">
                        {dayAppointments.slice(0, 3).map((apt) => (
                          <div
                            key={apt.id}
                            className={cn(
                              "text-xs p-1 rounded truncate",
                              typeConfig[apt.type].color
                            )}
                          >
                            {apt.time} - {apt.customerName.split(" ")[0]}
                          </div>
                        ))}
                        {dayAppointments.length > 3 && (
                          <div className="text-xs text-muted-foreground text-center">
                            +{dayAppointments.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Selected Day Details */}
              <div className="mt-4 pt-4 border-t border-border/50">
                <h3 className="font-medium mb-3">
                  {format(selectedDate, "EEEE, MMMM d")}
                  {isToday(selectedDate) && (
                    <Badge variant="secondary" className="ml-2">Today</Badge>
                  )}
                </h3>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-2">
                    {getAppointmentsForDate(selectedDate).length > 0 ? (
                      getAppointmentsForDate(selectedDate).map((apt) => (
                        <div
                          key={apt.id}
                          className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className={cn("w-1 h-10 rounded-full", statusConfig[apt.status].color)} />
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{apt.customerName}</span>
                                <Badge variant="outline" className={typeConfig[apt.type].color}>
                                  {typeConfig[apt.type].label}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                                <span className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  {apt.time}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Car className="w-3 h-3" />
                                  {apt.vehicleModel}
                                </span>
                              </div>
                            </div>
                          </div>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>View Details</DropdownMenuItem>
                              <DropdownMenuItem>Edit</DropdownMenuItem>
                              <DropdownMenuItem>Reschedule</DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem className="text-destructive">Cancel</DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No appointments scheduled
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </CardContent>
          </Card>
        )}

        {/* List View */}
        {view === "list" && (
          <div className="space-y-3">
            {filteredAppointments.map((apt) => {
              const StatusIcon = statusConfig[apt.status].icon;
              return (
                <Card key={apt.id} className="border-border/50 hover:shadow-md transition-all">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={cn("w-1 h-16 rounded-full", statusConfig[apt.status].color)} />
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{apt.customerName}</span>
                            <Badge variant="outline" className={typeConfig[apt.type].color}>
                              {typeConfig[apt.type].label}
                            </Badge>
                            {apt.bookedBy === "ai" && (
                              <Badge variant="secondary" className="text-xs">AI Booked</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <CalendarIcon className="w-4 h-4" />
                              {format(apt.date, "MMM d, yyyy")}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {apt.time}
                            </span>
                            <span className="flex items-center gap-1">
                              <Car className="w-4 h-4" />
                              {apt.vehicleModel}
                            </span>
                            <span className="flex items-center gap-1">
                              <Phone className="w-4 h-4" />
                              {apt.phone}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="flex items-center gap-1">
                          <StatusIcon className="w-3 h-3" />
                          {statusConfig[apt.status].label}
                        </Badge>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Reschedule</DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive">Cancel</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </motion.main>
    </div>
  );
};

export default Appointments;
