import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  FileImage, 
  Download, 
  Key,
  FileText,
  Image as ImageIcon,
  File,
  CheckCircle,
  Shield,
  Eye,
  Zap,
  Music,
  Video,
  RefreshCw
} from "lucide-react";

// API Service Integration
const API_BASE_URL = 'http://localhost:8000/api';

interface SupportedFormats {
  image: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
  video: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
  audio: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
  document: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
}

// Enhanced toast with better UX
const toast = {
  success: (message: string) => {
    console.log('✅ SUCCESS:', message);
    // You can replace this with a proper toast library later
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white p-3 rounded-lg shadow-lg z-50';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => document.body.removeChild(notification), 3000);
  },
  error: (message: string) => {
    console.error('❌ ERROR:', message);
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-500 text-white p-3 rounded-lg shadow-lg z-50';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => document.body.removeChild(notification), 5000);
  }
};

export default function General() {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState("embed");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [extractFile, setExtractFile] = useState<File | null>(null);
  const [contentType, setContentType] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [fileContent, setFileContent] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [operationResult, setOperationResult] = useState<any>(null);
  const [currentOperationId, setCurrentOperationId] = useState<string | null>(null);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats | null>(null);
  const [carrierType, setCarrierType] = useState("image");
  const [encryptionType, setEncryptionType] = useState("aes-256-gcm");
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [apiHealth, setApiHealth] = useState<any>(null);
  
  // Project Settings State
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [saveProject, setSaveProject] = useState(false);
  const [projectTags, setProjectTags] = useState("");
  const [savedProjects, setSavedProjects] = useState<any[]>([]);

  useEffect(() => {
    window.scrollTo(0, 0);
    
    const initializeComponent = async () => {
      try {
        // Check authentication
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          console.log("⚠️  No user authenticated, but allowing access for testing");
          // Temporarily allow access without authentication for testing
          // navigate("/auth");
          // return;
        }
        setCurrentUser(user);

        // Load API health and supported formats
        await loadApiData();
      } catch (error) {
        console.error("Initialization error:", error);
        toast.error("Failed to initialize application");
      }
    };

    initializeComponent();
  }, [navigate]);

  const loadApiData = async () => {
    try {
      console.log('🔍 Loading API data from:', API_BASE_URL);
      
      // Check API health
      console.log('📡 Testing API health...');
      const healthResponse = await fetch(`${API_BASE_URL}/health`);
      console.log('Health response status:', healthResponse.status);
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setApiHealth(healthData);
        console.log('✅ API Health loaded:', healthData);
      } else {
        console.log('❌ Health check failed with status:', healthResponse.status);
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }

      // Load supported formats
      console.log('📡 Loading supported formats...');
      const formatsResponse = await fetch(`${API_BASE_URL}/supported-formats`);
      console.log('Formats response status:', formatsResponse.status);
      
      if (formatsResponse.ok) {
        const formatsData = await formatsResponse.json();
        setSupportedFormats(formatsData);
        console.log('✅ Supported Formats loaded:', formatsData);
      } else {
        console.log('⚠️ Formats loading failed with status:', formatsResponse.status);
        // Don't throw error for formats - it's not critical
      }

      console.log('🎉 API data loading completed successfully');
      
    } catch (error) {
      console.error("❌ Failed to load API data:", error);
      console.error("Error details:", {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      toast.error("Backend API not available. Some features may not work.");
    }
  };

  const handleCarrierFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCarrierFile(file);
      
      // Auto-detect carrier type based on file extension
      const extension = file.name.split('.').pop()?.toLowerCase();
      let detectedType = carrierType; // default to current type
      
      if (extension) {
        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(extension)) {
          detectedType = "image";
          setCarrierType("image");
        } else if (['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'].includes(extension)) {
          detectedType = "video";
          setCarrierType("video");
        } else if (['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a'].includes(extension)) {
          detectedType = "audio";
          setCarrierType("audio");
        } else if (['pdf', 'docx', 'txt', 'rtf'].includes(extension)) {
          detectedType = "document";
          setCarrierType("document");
        }
      }
      
      // Validate file with detected type after a short delay to allow state update
      setTimeout(() => {
        if (supportedFormats) {
          validateFile(file, detectedType);
        }
      }, 100);
    }
  };

  const handleExtractFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setExtractFile(file);
      
      // Auto-detect file type for extraction
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (extension) {
        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(extension)) {
          setCarrierType("image");
        } else if (['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'].includes(extension)) {
          setCarrierType("video");
        } else if (['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a'].includes(extension)) {
          setCarrierType("audio");
        } else if (['pdf', 'docx', 'txt', 'rtf'].includes(extension)) {
          setCarrierType("document");
        }
      }
    }
  };

  const handleContentFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFileContent(e.target.files[0]);
    }
  };

  const generatePassword = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-password?length=16&include_symbols=true`);
      if (response.ok) {
        const data = await response.json();
        setPassword(data.password);
        toast.success(`Generated ${data.strength} password (${data.length} characters)`);
      } else {
        throw new Error('Failed to generate password');
      }
    } catch (error) {
      console.error('Password generation error:', error);
      // Fallback to local generation
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
      let result = '';
      for (let i = 0; i < 16; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      setPassword(result);
      toast.success('Generated strong password (local fallback)');
    }
  };

  const validateFile = (file: File, type: string) => {
    if (!supportedFormats) return true;

    const extension = file.name.split('.').pop()?.toLowerCase();
    const formats = supportedFormats[type as keyof SupportedFormats];
    
    if (!formats) {
      toast.error(`Unsupported file type: ${type}`);
      return false;
    }

    if (!formats.carrier_formats.includes(extension || '')) {
      toast.error(`Unsupported format. Supported: ${formats.carrier_formats.join(', ')}`);
      return false;
    }

    // Check file size limit (0 means no limit)
    if (formats.max_size_mb > 0) {
      const maxSizeBytes = formats.max_size_mb * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        toast.error(`File too large. Maximum size: ${formats.max_size_mb}MB`);
        return false;
      }
    }

    return true;
  };

  const formatFileSize = (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleEmbed = async () => {
    // Validation
    if (!carrierFile) {
      toast.error("Please select a carrier file");
      return;
    }

    if (contentType === "text" && !textContent.trim()) {
      toast.error("Please enter text content to hide");
      return;
    }

    if ((contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && !fileContent) {
      toast.error(`Please select a ${contentType} to hide`);
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }

    // Validate file format
    if (!validateFile(carrierFile, carrierType)) {
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setOperationResult(null);
    setCurrentOperationId(null);
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('carrier_file', carrierFile);
      formData.append('carrier_type', carrierType);
      formData.append('content_type', contentType);
      formData.append('password', password);
      formData.append('encryption_type', encryptionType);

      // Add project information if provided
      if (projectName.trim()) {
        formData.append('project_name', projectName.trim());
      }
      if (projectDescription.trim()) {
        formData.append('project_description', projectDescription.trim());
      }

      if (contentType === "text") {
        formData.append('text_content', textContent);
      } else if (contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") {
        formData.append('content_file', fileContent);
        // Set content_type to "file" for all file types for backend compatibility
        formData.set('content_type', 'file');
      }

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const response = await fetch(`${API_BASE_URL}/embed`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setCurrentOperationId(result.operation_id);
      toast.success("Embedding operation started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      toast.error(error.message || "Embedding operation failed");
      console.error("Embed error:", error);
    }
  };

  const handleExtract = async () => {
    // Validation
    if (!extractFile) {
      toast.error("Please select a file to extract from");
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter the password");
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setOperationResult(null);
    setCurrentOperationId(null);
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('stego_file', extractFile);
      formData.append('password', password);
      formData.append('output_format', 'auto');

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setCurrentOperationId(result.operation_id);
      toast.success("Extraction operation started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      toast.error(error.message || "Extraction operation failed");
      console.error("Extract error:", error);
    }
  };

  const pollOperationStatus = async (operationId: string) => {
    const maxAttempts = 300; // 5 minutes at 1-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/operations/${operationId}/status`);
        if (!response.ok) throw new Error('Failed to check status');
        
        const status = await response.json();
        
        if (status.progress !== undefined) {
          setProgress(status.progress);
        }

        if (status.status === "completed") {
          setIsProcessing(false);
          setOperationResult(status.result);
          toast.success("Operation completed successfully!");
          return;
        }

        if (status.status === "failed") {
          setIsProcessing(false);
          toast.error(status.error || "Operation failed");
          return;
        }

        attempts++;
        if (attempts < maxAttempts && (status.status === "processing" || status.status === "starting")) {
          setTimeout(poll, 1000);
        } else {
          setIsProcessing(false);
          if (attempts >= maxAttempts) {
            toast.error("Operation timed out");
          }
        }
      } catch (error) {
        setIsProcessing(false);
        toast.error("Failed to check operation status");
        console.error("Status poll error:", error);
      }
    };

    poll();
  };

  const downloadResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation result to download");
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/operations/${currentOperationId}/download`);
      
      if (!response.ok) {
        throw new Error(`Failed to download: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = operationResult?.filename || `result_${Date.now()}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("File downloaded successfully!");
    } catch (error: any) {
      toast.error(error.message || "Failed to download result");
      console.error("Download error:", error);
    }
  };

  const getContentIcon = () => {
    switch (contentType) {
      case "text": return <FileText className="h-4 w-4" />;
      case "image": return <ImageIcon className="h-4 w-4" />;
      case "audio": return <Music className="h-4 w-4" />;
      case "video": return <Video className="h-4 w-4" />;
      case "file": return <File className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-20">
        {/* Header Section */}
        <section className="py-8 bg-gradient-to-r from-primary/5 to-secondary/10">
          <div className="container">
            <div className="animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mr-4">
                    <FileImage className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h1 className="text-3xl md:text-4xl font-bold">General Protection</h1>
                    <p className="text-muted-foreground">
                      Advanced steganography for everyday data protection needs
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-4">
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Shield className="h-3 w-3" />
                  Secure Encryption
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Eye className="h-3 w-3" />
                  Invisible Embedding
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Zap className="h-3 w-3" />
                  Fast Processing
                </Badge>
                {/* API Status Indicator */}
                <Badge 
                  variant={apiHealth ? "default" : "destructive"} 
                  className="flex items-center gap-2"
                >
                  <div className={`h-2 w-2 rounded-full ${apiHealth ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                  API: {apiHealth ? 'Connected' : 'Disconnected'}
                </Badge>
              </div>
            </div>
          </div>
        </section>

        <section className="py-8">
          <div className="container">
            <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="embed">Embed Data</TabsTrigger>
                <TabsTrigger value="extract">Extract Data</TabsTrigger>
              </TabsList>
              
              <TabsContent value="embed" className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Input Section */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Upload className="h-5 w-5" />
                        Embed Configuration
                      </CardTitle>
                      <CardDescription>
                        Configure your carrier file and hidden content for secure embedding
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Carrier File Upload */}
                      <div className="space-y-2">
                        <Label htmlFor="carrier-file">Carrier File</Label>
                        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <input
                            id="carrier-file"
                            type="file"
                            accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                            onChange={handleCarrierFileChange}
                            className="hidden"
                          />
                          <label htmlFor="carrier-file" className="cursor-pointer">
                            <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                            <p className="text-sm text-muted-foreground">
                              {carrierFile ? carrierFile.name : "Click to upload carrier file"}
                            </p>
                          </label>
                        </div>
                      </div>

                      {/* Auto-detected Carrier Type Display */}
                      {carrierFile && (
                        <div className="space-y-2">
                          <Label>Detected Carrier Type</Label>
                          <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
                            {carrierType === "image" && <ImageIcon className="h-4 w-4" />}
                            {carrierType === "video" && <Video className="h-4 w-4" />}
                            {carrierType === "audio" && <Music className="h-4 w-4" />}
                            {carrierType === "document" && <FileText className="h-4 w-4" />}
                            <span className="capitalize font-medium">{carrierType}</span>
                            <span className="text-sm text-muted-foreground ml-auto">
                              Auto-detected from file extension
                            </span>
                          </div>
                        </div>
                      )}
                      {/* Content Type Selection */}
                      <div className="space-y-2">
                        <Label>Content Type to Hide</Label>
                        <Select value={contentType} onValueChange={setContentType}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                Text Message
                              </div>
                            </SelectItem>
                            <SelectItem value="file">
                              <div className="flex items-center gap-2">
                                <File className="h-4 w-4" />
                                Any File
                              </div>
                            </SelectItem>
                            <SelectItem value="image">
                              <div className="flex items-center gap-2">
                                <ImageIcon className="h-4 w-4" />
                                Image File
                              </div>
                            </SelectItem>
                            <SelectItem value="video">
                              <div className="flex items-center gap-2">
                                <Video className="h-4 w-4" />
                                Video File
                              </div>
                            </SelectItem>
                            <SelectItem value="audio">
                              <div className="flex items-center gap-2">
                                <Music className="h-4 w-4" />
                                Audio File
                              </div>
                            </SelectItem>
                            <SelectItem value="document">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                Document File
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      {/* Content Input */}
                      {contentType === "text" && (
                        <div className="space-y-2">
                          <Label htmlFor="text-content">Secret Message</Label>
                          <Textarea
                            id="text-content"
                            value={textContent}
                            onChange={(e) => setTextContent(e.target.value)}
                            placeholder="Enter your secret message here..."
                            rows={4}
                          />
                        </div>
                      )}

                      {(contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && (
                        <div className="space-y-2">
                          <Label htmlFor="content-file">
                            {contentType === "file" ? "File to Hide" :
                             contentType === "image" ? "Image to Hide" :
                             contentType === "video" ? "Video to Hide" :
                             contentType === "audio" ? "Audio to Hide" :
                             "Document to Hide"}
                          </Label>
                          <div className="border-2 border-dashed border-border rounded-lg p-4 text-center hover:border-primary/50 transition-colors">
                            <input
                              id="content-file"
                              type="file"
                              accept={
                                contentType === "image" ? "image/*" :
                                contentType === "video" ? "video/*" :
                                contentType === "audio" ? "audio/*" :
                                contentType === "document" ? ".pdf,.docx,.txt,.doc" :
                                "*/*"
                              }
                              onChange={handleContentFileChange}
                              className="hidden"
                            />
                            <label htmlFor="content-file" className="cursor-pointer">
                              {getContentIcon()}
                              <p className="text-sm text-muted-foreground mt-2">
                                {fileContent ? fileContent.name : `Click to upload ${contentType}`}
                              </p>
                            </label>
                          </div>
                        </div>
                      )}

                      {/* Project Settings */}
                      <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
                        <h4 className="text-sm font-semibold flex items-center gap-2">
                          <File className="h-4 w-4" />
                          Project Settings (Optional)
                        </h4>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-name">Project Name</Label>
                          <Input
                            id="project-name"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="e.g., Secret Mission Files"
                            className="text-sm"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-description">Project Description</Label>
                          <Textarea
                            id="project-description"
                            value={projectDescription}
                            onChange={(e) => setProjectDescription(e.target.value)}
                            placeholder="Brief description of this steganography project..."
                            rows={2}
                            className="text-sm"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-tags">Tags (comma-separated)</Label>
                          <Input
                            id="project-tags"
                            value={projectTags}
                            onChange={(e) => setProjectTags(e.target.value)}
                            placeholder="secret, mission, confidential"
                            className="text-sm"
                          />
                        </div>
                      </div>

                      {/* Password */}
                      <div className="space-y-2">
                        <Label htmlFor="password">Encryption Password</Label>
                        <div className="flex gap-2">
                          <Input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter strong password"
                            className="flex-1"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={generatePassword}
                            className="shrink-0"
                          >
                            <Key className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <Button 
                        onClick={handleEmbed} 
                        className="w-full"
                        disabled={!carrierFile || 
                          (contentType === "text" && !textContent.trim()) ||
                          ((contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && !fileContent) ||
                          isProcessing}
                      >
                        {isProcessing ? "Processing..." : "Embed Data"}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Preview/Progress Section */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="h-5 w-5" />
                        Preview & Progress
                      </CardTitle>
                      <CardDescription>
                        Monitor your embedding process and preview results
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {carrierFile && (
                        <div className="space-y-2">
                          <Label>Carrier File Preview</Label>
                          <div className="aspect-video rounded-lg overflow-hidden bg-muted flex items-center justify-center">
                            <FileImage className="h-16 w-16 text-muted-foreground" />
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {carrierFile.name} ({(carrierFile.size / 1024).toFixed(1)} KB)
                          </p>
                        </div>
                      )}

                      {isProcessing && (
                        <div className="space-y-2">
                          <Label>Processing Progress</Label>
                          <Progress value={progress} className="w-full" />
                          <p className="text-sm text-muted-foreground">
                            Embedding data... {progress}%
                          </p>
                        </div>
                      )}

                      {operationResult && !isProcessing && (
                        <div className="space-y-4">
                          <Alert>
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription>
                              Operation completed successfully! 
                              {operationResult.processing_time && 
                                ` Processed in ${operationResult.processing_time.toFixed(2)} seconds.`
                              }
                            </AlertDescription>
                          </Alert>
                          
                          <div className="space-y-2">
                            <Label>Operation Results</Label>
                            <div className="p-3 bg-muted rounded-lg space-y-2">
                              {operationResult.filename && (
                                <p className="text-sm"><strong>Output File:</strong> {operationResult.filename}</p>
                              )}
                              {operationResult.file_size && (
                                <p className="text-sm"><strong>File Size:</strong> {formatFileSize(operationResult.file_size)}</p>
                              )}
                              {operationResult.content_type && (
                                <p className="text-sm"><strong>Content Type:</strong> {operationResult.content_type}</p>
                              )}
                            </div>
                          </div>
                          
                          <Button 
                            onClick={downloadResult} 
                            className="w-full"
                            disabled={!currentOperationId}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download Result
                          </Button>
                        </div>
                      )}

                      {/* Project History */}
                      {projectName && (
                        <div className="space-y-2 pt-4 border-t">
                          <Label>Current Project</Label>
                          <div className="p-3 bg-muted rounded-lg space-y-1">
                            <p className="text-sm font-medium">{projectName}</p>
                            {projectDescription && (
                              <p className="text-xs text-muted-foreground">{projectDescription}</p>
                            )}
                            {projectTags && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {projectTags.split(',').map((tag, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {tag.trim()}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="extract" className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Extract Configuration */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Download className="h-5 w-5" />
                        Extract Configuration
                      </CardTitle>
                      <CardDescription>
                        Upload steganographic file and extract hidden content
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* File Upload */}
                      <div className="space-y-2">
                        <Label htmlFor="extract-file">Steganographic File</Label>
                        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <input
                            id="extract-file"
                            type="file"
                            accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                            onChange={handleExtractFileChange}
                            className="hidden"
                          />
                          <label htmlFor="extract-file" className="cursor-pointer">
                            <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                            <p className="text-sm text-muted-foreground">
                              {extractFile ? extractFile.name : "Click to upload file with hidden data"}
                            </p>
                          </label>
                        </div>
                      </div>

                      {/* Password */}
                      <div className="space-y-2">
                        <Label htmlFor="extract-password">Decryption Password</Label>
                        <Input
                          id="extract-password"
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Enter password to decrypt"
                        />
                      </div>

                      <Button 
                        onClick={handleExtract} 
                        className="w-full"
                        disabled={!extractFile || !password || isProcessing}
                      >
                        {isProcessing ? "Processing..." : "Extract Data"}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Extract Results */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="h-5 w-5" />
                        Extraction Results
                      </CardTitle>
                      <CardDescription>
                        View extracted content and download results
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {isProcessing && (
                        <div className="space-y-2">
                          <Label>Extraction Progress</Label>
                          <Progress value={progress} className="w-full" />
                          <p className="text-sm text-muted-foreground">
                            Extracting hidden data... {progress}%
                          </p>
                        </div>
                      )}

                      {operationResult && !isProcessing && (
                        <div className="space-y-4">
                          <Alert>
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription>
                              Extraction completed successfully!
                              {operationResult.processing_time && 
                                ` Processed in ${operationResult.processing_time.toFixed(2)} seconds.`
                              }
                            </AlertDescription>
                          </Alert>
                          
                          <div className="space-y-2">
                            <Label>Extracted Content</Label>
                            <div className="p-3 bg-muted rounded-lg space-y-2">
                              {operationResult.extracted_filename && (
                                <p className="text-sm"><strong>Extracted File:</strong> {operationResult.extracted_filename}</p>
                              )}
                              {operationResult.content_type && (
                                <p className="text-sm"><strong>Content Type:</strong> {operationResult.content_type}</p>
                              )}
                              {operationResult.file_size && (
                                <p className="text-sm"><strong>File Size:</strong> {formatFileSize(operationResult.file_size)}</p>
                              )}
                              {operationResult.text_content && (
                                <div className="space-y-1">
                                  <p className="text-sm font-medium">Text Content:</p>
                                  <div className="p-2 bg-background rounded border max-h-32 overflow-y-auto">
                                    <pre className="text-xs font-mono whitespace-pre-wrap">{operationResult.text_content}</pre>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <Button 
                            onClick={downloadResult} 
                            className="w-full"
                            disabled={!currentOperationId}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download Extracted Data
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}