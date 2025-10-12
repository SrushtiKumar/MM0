import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Link } from "react-router-dom";
import { 
  Plus, 
  FileImage, 
  Shield, 
  Lock, 
  Calendar, 
  Download, 
  Eye, 
  Trash2, 
  Settings,
  FolderOpen,
  Activity,
  Clock,
  BarChart3
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import ProjectCreationDialog from "@/components/ProjectCreationDialog";

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [selectedTab, setSelectedTab] = useState("projects");
  const [projects, setProjects] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    window.scrollTo(0, 0);
    checkAuthAndFetchProjects();
  }, []);

  const checkAuthAndFetchProjects = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      navigate("/auth");
      return;
    }

    setUser(user);
    await fetchProjects(user.id);
  };

  const fetchProjects = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from("projects")
        .select("*")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setProjects(data || []);
    } catch (error) {
      console.error("Error fetching projects:", error);
      toast({
        title: "Error",
        description: "Failed to load projects.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      const { error } = await supabase
        .from("projects")
        .delete()
        .eq("id", projectId);

      if (error) throw error;

      setProjects(projects.filter(p => p.id !== projectId));
      toast({
        title: "Project Deleted",
        description: "Project has been deleted successfully.",
      });
    } catch (error) {
      console.error("Error deleting project:", error);
      toast({
        title: "Error",
        description: "Failed to delete project.",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "general":
        return <FileImage className="h-4 w-4" />;
      case "copyright":
        return <Shield className="h-4 w-4" />;
      case "forensic":
        return <Lock className="h-4 w-4" />;
      default:
        return <FileImage className="h-4 w-4" />;
    }
  };

  const getTypeBadgeColor = (type: string) => {
    switch (type) {
      case "general":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "copyright":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "forensic":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300";
    }
  };

  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.length,
    processedFiles: 0,
    dataProtected: "0 KB"
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-20">
        {/* Header Section */}
        <section className="py-8 bg-gradient-to-r from-primary/5 to-sea-light/10 dark:from-primary/10 dark:to-background">
          <div className="container">
            <div className="flex items-center justify-between">
              <div className="animate-fade-in">
                <h1 className="text-3xl md:text-4xl font-bold mb-2">Welcome back!</h1>
                <p className="text-muted-foreground">
                  Manage your steganography projects and protected data from your secure dashboard
                </p>
              </div>
              
              <div className="animate-fade-in [animation-delay:200ms]">
                <Button onClick={() => setShowCreateDialog(true)} size="lg" className="btn-primary">
                  <Plus className="mr-2 h-4 w-4" />
                  New Project
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Cards */}
        <section className="py-8">
          <div className="container">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="animate-fade-in">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Projects</p>
                      <p className="text-2xl font-bold">{stats.totalProjects}</p>
                    </div>
                    <FolderOpen className="h-8 w-8 text-primary" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="animate-fade-in [animation-delay:100ms]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Active Projects</p>
                      <p className="text-2xl font-bold text-green-600">{stats.activeProjects}</p>
                    </div>
                    <Activity className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="animate-fade-in [animation-delay:200ms]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Files Processed</p>
                      <p className="text-2xl font-bold text-blue-600">{stats.processedFiles}</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="animate-fade-in [animation-delay:300ms]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Data Protected</p>
                      <p className="text-2xl font-bold text-purple-600">{stats.dataProtected}</p>
                    </div>
                    <Shield className="h-8 w-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Projects List */}
        <section className="py-8">
          <div className="container">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">My Projects</h2>
            </div>
            
            {isLoading ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Loading projects...</p>
              </div>
            ) : projects.length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <FolderOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Projects Yet</h3>
                  <p className="text-muted-foreground mb-6">
                    Create your first project to start protecting your data
                  </p>
                  <Button onClick={() => setShowCreateDialog(true)} className="btn-primary">
                    <Plus className="mr-2 h-4 w-4" />
                    Create Project
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {projects.map((project, index) => (
                  <Card key={project.id} className={`animate-fade-in hover:shadow-lg transition-all duration-300`} style={{ animationDelay: `${index * 100}ms` }}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="flex items-center gap-2">
                            {getTypeIcon(project.project_type)}
                            {project.name}
                          </CardTitle>
                          <div className="flex items-center gap-2">
                            <Badge className={`text-xs ${getTypeBadgeColor(project.project_type)}`}>
                              {project.project_type}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleDeleteProject(project.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      {project.description && (
                        <p className="text-sm text-muted-foreground">{project.description}</p>
                      )}
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="font-medium text-muted-foreground mb-1">Created</p>
                          <p className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {formatDate(project.created_at)}
                          </p>
                        </div>
                        
                        <div>
                          <p className="font-medium text-muted-foreground mb-1">Last Updated</p>
                          <p className="flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            {formatDate(project.updated_at)}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-end pt-2 border-t border-border">
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/${project.project_type}`}>
                            Open Project
                          </Link>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
      
      <ProjectCreationDialog 
        open={showCreateDialog} 
        onOpenChange={setShowCreateDialog}
      />
      
      <Footer />
    </div>
  );
}
