import { useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Key,
  Building,
  Phone,
  Mail,
  MapPin,
  Clock,
  Save,
  Moon,
  Sun,
  Monitor,
  Trash2,
  Download,
  Upload,
  HelpCircle,
  MessageSquare,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { blurIn, staggerContainer, staggerItem } from "@/lib/motion";

const Settings = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState("system");
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;

  const toggleLanguage = () => {
    const newLang = currentLanguage === 'en' ? 'ar' : 'en';
    i18n.changeLanguage(newLang);
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
            <h1 className="text-2xl font-semibold text-foreground">{t('settings.title')}</h1>
            <p className="text-muted-foreground text-sm">
              {t('settings.subtitle')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <LanguageSwitcher size="lg" />
            <Button>
              <Save className="w-4 h-4 mr-2" />
              {t('common.saveAllChanges')}
            </Button>
          </div>
        </div>

        <Tabs defaultValue="account" className="space-y-6">
          <TabsList className="bg-muted/50">
            <TabsTrigger value="account">
              <User className="w-4 h-4 mr-2" />
              Account
            </TabsTrigger>
            <TabsTrigger value="organization">
              <Building className="w-4 h-4 mr-2" />
              Organization
            </TabsTrigger>
            <TabsTrigger value="notifications">
              <Bell className="w-4 h-4 mr-2" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="appearance">
              <Palette className="w-4 h-4 mr-2" />
              Appearance
            </TabsTrigger>
            <TabsTrigger value="security">
              <Shield className="w-4 h-4 mr-2" />
              Security
            </TabsTrigger>
          </TabsList>

          {/* Account Settings */}
          <TabsContent value="account">
            <motion.div
              className="space-y-6"
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                      Update your personal information and profile picture
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Profile Photo */}
                    <div className="flex items-center gap-6">
                      <Avatar className="h-20 w-20">
                        <AvatarImage src="/placeholder.svg" />
                        <AvatarFallback className="text-xl">AG</AvatarFallback>
                      </Avatar>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Upload className="w-4 h-4 mr-2" />
                            Upload Photo
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="w-4 h-4 mr-2" />
                            Remove
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          JPG, PNG or GIF. Max size 2MB.
                        </p>
                      </div>
                    </div>

                    <Separator />

                    {/* Personal Info */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>First Name</Label>
                        <Input defaultValue="Ayaan" />
                      </div>
                      <div className="space-y-2">
                        <Label>Last Name</Label>
                        <Input defaultValue="Gazali" />
                      </div>
                      <div className="space-y-2">
                        <Label>Email</Label>
                        <Input type="email" defaultValue="ayaan@dealership.ae" />
                      </div>
                      <div className="space-y-2">
                        <Label>Phone</Label>
                        <Input type="tel" defaultValue="+971 50 123 4567" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Role</Label>
                      <Input defaultValue="Operations Manager" readOnly className="bg-muted/50" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Regional Settings</CardTitle>
                    <CardDescription>
                      Configure your timezone and language preferences
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Timezone</Label>
                        <Select defaultValue="gst">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="gst">Gulf Standard Time (GST)</SelectItem>
                            <SelectItem value="ast">Arabia Standard Time (AST)</SelectItem>
                            <SelectItem value="utc">UTC</SelectItem>
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
                            <SelectItem value="ar">العربية (Arabic)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Date Format</Label>
                        <Select defaultValue="dmy">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="dmy">DD/MM/YYYY</SelectItem>
                            <SelectItem value="mdy">MM/DD/YYYY</SelectItem>
                            <SelectItem value="ymd">YYYY-MM-DD</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Currency</Label>
                        <Select defaultValue="aed">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="aed">AED (درهم)</SelectItem>
                            <SelectItem value="usd">USD ($)</SelectItem>
                            <SelectItem value="eur">EUR (€)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          </TabsContent>

          {/* Organization Settings */}
          <TabsContent value="organization">
            <motion.div
              className="space-y-6"
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Organization Details</CardTitle>
                    <CardDescription>
                      Information about your dealership
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Dealership Name</Label>
                      <Input defaultValue="Al Ain Motors" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Phone</Label>
                        <Input defaultValue="+971 2 123 4567" />
                      </div>
                      <div className="space-y-2">
                        <Label>Email</Label>
                        <Input defaultValue="info@alainmotors.ae" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>Address</Label>
                      <Textarea defaultValue="Sheikh Zayed Road, Al Ain, UAE" />
                    </div>
                    <div className="space-y-2">
                      <Label>Website</Label>
                      <Input defaultValue="https://alainmotors.ae" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Business Hours</CardTitle>
                    <CardDescription>
                      Set your operating hours for AI calling
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {[
                      { day: "Sunday - Thursday", start: "08:00", end: "18:00", active: true },
                      { day: "Friday", start: "08:00", end: "12:00", active: true },
                      { day: "Saturday", start: "10:00", end: "16:00", active: false },
                    ].map((schedule) => (
                      <div key={schedule.day} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                        <div className="flex items-center gap-3">
                          <Switch defaultChecked={schedule.active} />
                          <span className="font-medium">{schedule.day}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Input className="w-24" defaultValue={schedule.start} type="time" />
                          <span className="text-muted-foreground">to</span>
                          <Input className="w-24" defaultValue={schedule.end} type="time" />
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          </TabsContent>

          {/* Notifications Settings */}
          <TabsContent value="notifications">
            <motion.div
              className="space-y-6"
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Notification Preferences</CardTitle>
                    <CardDescription>
                      Choose what notifications you want to receive
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {[
                      {
                        title: "Campaign Completed",
                        description: "Get notified when a calling campaign finishes",
                        email: true,
                        push: true,
                      },
                      {
                        title: "Appointment Booked",
                        description: "Notification for each new appointment from AI calls",
                        email: true,
                        push: true,
                      },
                      {
                        title: "Call Flagged for Review",
                        description: "When a call needs manual review or has issues",
                        email: true,
                        push: false,
                      },
                      {
                        title: "Daily Summary",
                        description: "Daily report of all calling activities",
                        email: true,
                        push: false,
                      },
                      {
                        title: "Weekly Report",
                        description: "Weekly analytics and performance report",
                        email: true,
                        push: false,
                      },
                      {
                        title: "Integration Errors",
                        description: "Alerts when integrations fail or need attention",
                        email: true,
                        push: true,
                      },
                    ].map((notification) => (
                      <div key={notification.title} className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <p className="font-medium">{notification.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {notification.description}
                          </p>
                        </div>
                        <div className="flex items-center gap-6">
                          <div className="flex items-center gap-2">
                            <Label className="text-xs text-muted-foreground">Email</Label>
                            <Switch defaultChecked={notification.email} />
                          </div>
                          <div className="flex items-center gap-2">
                            <Label className="text-xs text-muted-foreground">Push</Label>
                            <Switch defaultChecked={notification.push} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          </TabsContent>

          {/* Appearance Settings */}
          <TabsContent value="appearance">
            <motion.div
              className="space-y-6"
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Theme</CardTitle>
                    <CardDescription>
                      Select your preferred color theme
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <RadioGroup
                      value={theme}
                      onValueChange={setTheme}
                      className="grid grid-cols-3 gap-4"
                    >
                      {[
                        { value: "light", label: "Light", icon: Sun },
                        { value: "dark", label: "Dark", icon: Moon },
                        { value: "system", label: "System", icon: Monitor },
                      ].map((option) => (
                        <div key={option.value}>
                          <RadioGroupItem
                            value={option.value}
                            id={option.value}
                            className="peer sr-only"
                          />
                          <Label
                            htmlFor={option.value}
                            className="flex flex-col items-center justify-between rounded-lg border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                          >
                            <option.icon className="mb-3 h-6 w-6" />
                            {option.label}
                          </Label>
                        </div>
                      ))}
                    </RadioGroup>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Dashboard Layout</CardTitle>
                    <CardDescription>
                      Customize your dashboard appearance
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Compact Mode</Label>
                        <p className="text-sm text-muted-foreground">
                          Show more content with reduced spacing
                        </p>
                      </div>
                      <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Show Animations</Label>
                        <p className="text-sm text-muted-foreground">
                          Enable smooth transitions and animations
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Sidebar Collapsed by Default</Label>
                        <p className="text-sm text-muted-foreground">
                          Start with collapsed sidebar
                        </p>
                      </div>
                      <Switch />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security">
            <motion.div
              className="space-y-6"
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Password</CardTitle>
                    <CardDescription>
                      Change your password
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Current Password</Label>
                      <Input type="password" />
                    </div>
                    <div className="space-y-2">
                      <Label>New Password</Label>
                      <Input type="password" />
                    </div>
                    <div className="space-y-2">
                      <Label>Confirm New Password</Label>
                      <Input type="password" />
                    </div>
                    <Button>Update Password</Button>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Two-Factor Authentication</CardTitle>
                    <CardDescription>
                      Add an extra layer of security to your account
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <p className="font-medium">Enable 2FA</p>
                        <p className="text-sm text-muted-foreground">
                          Use an authenticator app to generate codes
                        </p>
                      </div>
                      <Button variant="outline">Enable</Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={staggerItem}>
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>API Keys</CardTitle>
                    <CardDescription>
                      Manage your API keys for external integrations
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div>
                        <p className="font-medium">Production Key</p>
                        <p className="text-sm text-muted-foreground font-mono">
                          sk-prod-****************************
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">Active</Badge>
                        <Button variant="ghost" size="sm">Regenerate</Button>
                      </div>
                    </div>
                    <Button variant="outline">
                      <Key className="w-4 h-4 mr-2" />
                      Create New API Key
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={staggerItem}>
                <Card className="border-destructive/50">
                  <CardHeader>
                    <CardTitle className="text-destructive">Danger Zone</CardTitle>
                    <CardDescription>
                      Irreversible actions for your account
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Export All Data</p>
                        <p className="text-sm text-muted-foreground">
                          Download all your data as a JSON file
                        </p>
                      </div>
                      <Button variant="outline">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                      </Button>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Delete Account</p>
                        <p className="text-sm text-muted-foreground">
                          Permanently delete your account and all data
                        </p>
                      </div>
                      <Button variant="destructive">Delete Account</Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          </TabsContent>
        </Tabs>
      </motion.main>
    </div>
  );
};

export default Settings;
