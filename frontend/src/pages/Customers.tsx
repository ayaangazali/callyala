import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Car,
  User,
  Search,
  Plus,
  MoreHorizontal,
  Phone,
  Mail,
  MapPin,
  Calendar,
  FileText,
  Edit,
  Trash2,
  Eye,
  Filter,
  Download,
  Upload,
  ChevronRight,
  History,
  DollarSign,
  Wrench,
  Tag,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";

interface Customer {
  id: string;
  name: string;
  phone: string;
  email?: string;
  address?: string;
  totalCalls: number;
  totalAppointments: number;
  lastContact: string;
  status: "active" | "inactive" | "vip";
  vehicles: Vehicle[];
  notes?: string;
}

interface Vehicle {
  id: string;
  make: string;
  model: string;
  year: number;
  plate: string;
  vin?: string;
  color?: string;
  lastService?: string;
  totalServices: number;
  totalSpent: number;
}

const customers: Customer[] = [
  {
    id: "cust-001",
    name: "Ahmed Al-Mansour",
    phone: "+971 50 123 4567",
    email: "ahmed@email.com",
    address: "Dubai Marina, Tower 5, Apt 1201",
    totalCalls: 12,
    totalAppointments: 8,
    lastContact: "Today",
    status: "vip",
    vehicles: [
      {
        id: "veh-001",
        make: "Toyota",
        model: "Land Cruiser",
        year: 2024,
        plate: "A 12345",
        color: "Pearl White",
        lastService: "2024-01-15",
        totalServices: 5,
        totalSpent: 12500,
      },
      {
        id: "veh-002",
        make: "Lexus",
        model: "LX 600",
        year: 2023,
        plate: "A 67890",
        color: "Black",
        lastService: "2023-12-20",
        totalServices: 3,
        totalSpent: 8200,
      },
    ],
    notes: "VIP customer, prefers morning appointments. Owns two vehicles.",
  },
  {
    id: "cust-002",
    name: "Fatima Al-Hassan",
    phone: "+971 55 987 6543",
    email: "fatima@email.com",
    totalCalls: 5,
    totalAppointments: 3,
    lastContact: "Yesterday",
    status: "active",
    vehicles: [
      {
        id: "veh-003",
        make: "Nissan",
        model: "Patrol",
        year: 2023,
        plate: "B 54321",
        color: "Silver",
        lastService: "2024-01-10",
        totalServices: 2,
        totalSpent: 4500,
      },
    ],
  },
  {
    id: "cust-003",
    name: "Mohammed Al-Rashid",
    phone: "+971 55 333 4444",
    email: "mohammed@email.com",
    address: "JBR, Building 8",
    totalCalls: 8,
    totalAppointments: 6,
    lastContact: "2 days ago",
    status: "active",
    vehicles: [
      {
        id: "veh-004",
        make: "Mercedes",
        model: "GLE 450",
        year: 2024,
        plate: "E 22222",
        color: "Obsidian Black",
        lastService: "2024-01-18",
        totalServices: 4,
        totalSpent: 15800,
      },
    ],
  },
  {
    id: "cust-004",
    name: "Sarah Ahmed",
    phone: "+971 50 111 2222",
    totalCalls: 3,
    totalAppointments: 2,
    lastContact: "1 week ago",
    status: "inactive",
    vehicles: [
      {
        id: "veh-005",
        make: "BMW",
        model: "X5",
        year: 2024,
        plate: "D 11111",
        color: "Alpine White",
        totalServices: 1,
        totalSpent: 2800,
      },
    ],
  },
  {
    id: "cust-005",
    name: "Khalid Ibrahim",
    phone: "+971 52 456 7890",
    email: "khalid@email.com",
    totalCalls: 6,
    totalAppointments: 4,
    lastContact: "3 days ago",
    status: "vip",
    vehicles: [
      {
        id: "veh-006",
        make: "Lexus",
        model: "LX 600",
        year: 2024,
        plate: "C 98765",
        color: "Sonic Titanium",
        lastService: "2024-01-12",
        totalServices: 3,
        totalSpent: 9500,
      },
    ],
  },
];

const statusConfig = {
  active: { label: "Active", color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20" },
  inactive: { label: "Inactive", color: "bg-gray-500/10 text-gray-600 border-gray-500/20" },
  vip: { label: "VIP", color: "bg-amber-500/10 text-amber-600 border-amber-500/20" },
};

const Customers = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [view, setView] = useState<"customers" | "vehicles">("customers");
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  const filteredCustomers = customers.filter((customer) => {
    const matchesSearch =
      customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      customer.phone.includes(searchQuery) ||
      customer.vehicles.some((v) =>
        `${v.make} ${v.model}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
        v.plate.toLowerCase().includes(searchQuery.toLowerCase())
      );
    const matchesStatus = statusFilter === "all" || customer.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const allVehicles = customers.flatMap((c) =>
    c.vehicles.map((v) => ({ ...v, customerName: c.name, customerId: c.id }))
  );

  const stats = {
    totalCustomers: customers.length,
    vipCustomers: customers.filter((c) => c.status === "vip").length,
    totalVehicles: allVehicles.length,
    totalRevenue: allVehicles.reduce((sum, v) => sum + v.totalSpent, 0),
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
            <h1 className="text-2xl font-semibold text-foreground">Customers & Vehicles</h1>
            <p className="text-muted-foreground text-sm">
              Manage your customer database and vehicle inventory
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Upload className="w-4 h-4 mr-2" />
              Import
            </Button>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Dialog>
              <DialogTrigger asChild>
                <Button className="bg-primary hover:bg-primary/90">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Customer
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle>Add New Customer</DialogTitle>
                  <DialogDescription>
                    Enter customer details and their vehicle information
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Full Name</Label>
                      <Input placeholder="Customer name" />
                    </div>
                    <div className="space-y-2">
                      <Label>Phone</Label>
                      <Input placeholder="+971 50 XXX XXXX" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input type="email" placeholder="email@example.com" />
                  </div>
                  <div className="space-y-2">
                    <Label>Address</Label>
                    <Textarea placeholder="Full address" />
                  </div>
                  <div className="border-t pt-4">
                    <Label className="text-base">Vehicle Details</Label>
                    <div className="grid grid-cols-2 gap-4 mt-3">
                      <div className="space-y-2">
                        <Label>Make</Label>
                        <Input placeholder="Toyota" />
                      </div>
                      <div className="space-y-2">
                        <Label>Model</Label>
                        <Input placeholder="Land Cruiser" />
                      </div>
                      <div className="space-y-2">
                        <Label>Year</Label>
                        <Input type="number" placeholder="2024" />
                      </div>
                      <div className="space-y-2">
                        <Label>Plate</Label>
                        <Input placeholder="A 12345" />
                      </div>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button>Add Customer</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
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
            { label: "Total Customers", value: stats.totalCustomers, icon: User },
            { label: "VIP Customers", value: stats.vipCustomers, icon: Tag, color: "text-amber-500" },
            { label: "Total Vehicles", value: stats.totalVehicles, icon: Car },
            { label: "Total Revenue", value: `${(stats.totalRevenue / 1000).toFixed(1)}K AED`, icon: DollarSign, color: "text-emerald-500" },
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
          <Tabs value={view} onValueChange={(v) => setView(v as "customers" | "vehicles")}>
            <TabsList>
              <TabsTrigger value="customers">
                <User className="w-4 h-4 mr-2" />
                Customers
              </TabsTrigger>
              <TabsTrigger value="vehicles">
                <Car className="w-4 h-4 mr-2" />
                Vehicles
              </TabsTrigger>
            </TabsList>
          </Tabs>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search customers or vehicles..."
                className="pl-9 w-80"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="vip">VIP</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Customers Table */}
        {view === "customers" && (
          <Card className="border-border/50">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Customer</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Vehicles</TableHead>
                  <TableHead>Activity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-10"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCustomers.map((customer) => (
                  <TableRow
                    key={customer.id}
                    className="group cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelectedCustomer(customer)}
                  >
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-9 w-9">
                          <AvatarFallback className="bg-primary/10 text-primary text-sm">
                            {customer.name.split(" ").map((n) => n[0]).join("")}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{customer.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {customer.vehicles.length} vehicle{customer.vehicles.length !== 1 ? "s" : ""}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <p className="text-sm flex items-center gap-1">
                          <Phone className="w-3 h-3 text-muted-foreground" />
                          {customer.phone}
                        </p>
                        {customer.email && (
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            {customer.email}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {customer.vehicles.slice(0, 2).map((v) => (
                          <Badge key={v.id} variant="secondary" className="text-xs">
                            {v.make} {v.model}
                          </Badge>
                        ))}
                        {customer.vehicles.length > 2 && (
                          <Badge variant="secondary" className="text-xs">
                            +{customer.vehicles.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <p>{customer.totalCalls} calls</p>
                        <p className="text-xs text-muted-foreground">
                          Last: {customer.lastContact}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={statusConfig[customer.status].color}>
                        {statusConfig[customer.status].label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => setSelectedCustomer(customer)}>
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Phone className="w-4 h-4 mr-2" />
                            Call Customer
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
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        )}

        {/* Vehicles Table */}
        {view === "vehicles" && (
          <Card className="border-border/50">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Vehicle</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead>Plate</TableHead>
                  <TableHead>Last Service</TableHead>
                  <TableHead>Total Spent</TableHead>
                  <TableHead className="w-10"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allVehicles.map((vehicle) => (
                  <TableRow key={vehicle.id} className="group hover:bg-muted/50">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                          <Car className="w-5 h-5 text-muted-foreground" />
                        </div>
                        <div>
                          <p className="font-medium">
                            {vehicle.year} {vehicle.make} {vehicle.model}
                          </p>
                          {vehicle.color && (
                            <p className="text-xs text-muted-foreground">{vehicle.color}</p>
                          )}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{vehicle.customerName}</span>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{vehicle.plate}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {vehicle.lastService || "Never"}
                        <p className="text-xs text-muted-foreground">
                          {vehicle.totalServices} service{vehicle.totalServices !== 1 ? "s" : ""}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium text-emerald-600">
                        {vehicle.totalSpent.toLocaleString()} AED
                      </span>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Eye className="w-4 h-4 mr-2" />
                            View History
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Wrench className="w-4 h-4 mr-2" />
                            Schedule Service
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Edit className="w-4 h-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        )}

        {/* Customer Detail Sheet */}
        <Sheet open={!!selectedCustomer} onOpenChange={() => setSelectedCustomer(null)}>
          <SheetContent className="w-[500px] sm:w-[600px] sm:max-w-none">
            {selectedCustomer && (
              <>
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className="bg-primary/10 text-primary text-lg">
                        {selectedCustomer.name.split(" ").map((n) => n[0]).join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold">{selectedCustomer.name}</h3>
                      <Badge variant="outline" className={statusConfig[selectedCustomer.status].color}>
                        {statusConfig[selectedCustomer.status].label}
                      </Badge>
                    </div>
                  </SheetTitle>
                </SheetHeader>

                <div className="mt-6 space-y-6">
                  {/* Contact Info */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-medium text-muted-foreground">Contact Information</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-3 text-sm">
                        <Phone className="w-4 h-4 text-muted-foreground" />
                        {selectedCustomer.phone}
                      </div>
                      {selectedCustomer.email && (
                        <div className="flex items-center gap-3 text-sm">
                          <Mail className="w-4 h-4 text-muted-foreground" />
                          {selectedCustomer.email}
                        </div>
                      )}
                      {selectedCustomer.address && (
                        <div className="flex items-center gap-3 text-sm">
                          <MapPin className="w-4 h-4 text-muted-foreground" />
                          {selectedCustomer.address}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 rounded-lg bg-muted/50 text-center">
                      <p className="text-2xl font-semibold">{selectedCustomer.totalCalls}</p>
                      <p className="text-xs text-muted-foreground">Total Calls</p>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50 text-center">
                      <p className="text-2xl font-semibold">{selectedCustomer.totalAppointments}</p>
                      <p className="text-xs text-muted-foreground">Appointments</p>
                    </div>
                    <div className="p-3 rounded-lg bg-emerald-500/10 text-center">
                      <p className="text-2xl font-semibold text-emerald-600">
                        {selectedCustomer.vehicles.reduce((sum, v) => sum + v.totalSpent, 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground">Total AED</p>
                    </div>
                  </div>

                  {/* Vehicles */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-medium text-muted-foreground">Vehicles</h4>
                    <div className="space-y-2">
                      {selectedCustomer.vehicles.map((vehicle) => (
                        <div
                          key={vehicle.id}
                          className="p-3 rounded-lg border border-border/50 bg-muted/30"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <Car className="w-5 h-5 text-muted-foreground" />
                              <div>
                                <p className="font-medium">
                                  {vehicle.year} {vehicle.make} {vehicle.model}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {vehicle.plate} • {vehicle.color}
                                </p>
                              </div>
                            </div>
                            <Badge variant="secondary">
                              {vehicle.totalServices} services
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Notes */}
                  {selectedCustomer.notes && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-muted-foreground">Notes</h4>
                      <p className="text-sm p-3 rounded-lg bg-muted/50">
                        {selectedCustomer.notes}
                      </p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button className="flex-1" variant="outline">
                      <Phone className="w-4 h-4 mr-2" />
                      Call
                    </Button>
                    <Button className="flex-1" variant="outline">
                      <Calendar className="w-4 h-4 mr-2" />
                      Schedule
                    </Button>
                    <Button className="flex-1">
                      <Edit className="w-4 h-4 mr-2" />
                      Edit
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

export default Customers;
