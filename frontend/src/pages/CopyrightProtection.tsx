import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import {
  Shield,
  Upload,
  Download,
  FileImage,
  FileVideo,
  FileAudio,
  FileText,
  Lock,
  Eye,
  CheckCircle,
  AlertTriangle,
  Info,
  X,
  Plus,
  Calendar,
  Settings,
  RefreshCw,
  EyeOff
} from "lucide-react";

// API Configuration
const API_BASE_URL = "/api";

// Helper function to format timestamp in user-friendly way
const formatTimestampForHumans = (date: Date): string => {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short'
  };
  return date.toLocaleDateString('en-US', options);
};

// Helper function to display timestamp (handles both old ISO and new user-friendly formats)
const displayTimestamp = (timestampStr: string): string => {
  // Check if it's already in ISO format (contains 'T' and ends with 'Z')
  if (timestampStr.includes('T') && (timestampStr.endsWith('Z') || timestampStr.includes('+') || timestampStr.includes('-'))) {
    // It's an ISO timestamp, convert to user-friendly format
    try {
      const date = new Date(timestampStr);
      return formatTimestampForHumans(date);
    } catch {
      // If parsing fails, return as-is
      return timestampStr;
    }
  } else {
    // It's already in user-friendly format, return as-is
    return timestampStr;
  }
};

// Types
interface FormatData {
  carrier_formats: string[];
  content_formats: string[];
  max_size_mb: number;
}

interface SupportedFormats {
  image: FormatData;
  audio: FormatData;
  video: FormatData;
  document?: FormatData;
}

interface OperationResult {
  success: boolean;
  message: string;
  filename?: string;
  output_filename?: string;
  processing_time?: number;
  extracted_filename?: string;
  content_type?: string;
  file_size?: number;
  text_content?: string;
  preview?: string;
  capacity_info?: {
    estimated_capacity: number;
    content_size: number;
    utilization_percentage: number;
  };
  batch_results?: Array<{
    carrier_file: string;
    output_file: string;
    success: boolean;
    message?: string;
    processing_time?: number;
  }>;
}

export default function CopyrightProtection() {
  const navigate = useNavigate();

  // State management
  const [selectedTab, setSelectedTab] = useState("embed");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [carrierFiles, setCarrierFiles] = useState<File[]>([]); // Multiple carrier files
  const [batchMode, setBatchMode] = useState(false); // Toggle between single and batch mode
  const [extractFile, setExtractFile] = useState<File | null>(null);

  // Copyright fields state
  const [authorName, setAuthorName] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [copyrightAlias, setCopyrightAlias] = useState("");

  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [operationResult, setOperationResult] = useState<OperationResult | null>(null);
  const [currentOperationId, setCurrentOperationId] = useState<string | null>(null);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats | null>(null);
  const [carrierType, setCarrierType] = useState("image");
  const [encryptionType] = useState("aes-256-gcm"); // Hidden from user, always use AES-256-GCM
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Project information fields
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
    
    // Check authentication and get user
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) {
        navigate("/auth");
      } else {
        setCurrentUser(user);
      }
    });

    // Fetch supported formats
    fetchSupportedFormats();
  }, [navigate]);

  const fetchSupportedFormats = async () => {
    try {
      console.log("📡 Fetching supported formats from:", `${API_BASE_URL}/supported-formats`);
      const response = await fetch(`${API_BASE_URL}/supported-formats`);
      console.log(`📡 Formats response status: ${response.status}`);
      console.log(`📡 Response headers:`, response.headers);
      
      if (response.ok) {
        const formats = await response.json();
        console.log("📋 Raw API response:", formats);
        console.log("📋 Setting supported formats state...");
        setSupportedFormats(formats);
        console.log("✅ Supported formats state updated");
        
        // Verify the state was set correctly
        setTimeout(() => {
          console.log("🔍 Verifying formats state after update...");
        }, 100);
      } else {
        console.log("❌ Failed to fetch formats:", response.status);
        console.log("❌ Response text:", await response.text());
      }
    } catch (error) {
      console.error("❌ Error fetching supported formats:", error);
    }
  };

  // Polling function for operation status
  const pollOperationStatus = async (operationId: string) => {
    const maxAttempts = 120; // 2 minutes with 1-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        attempts++;
        const response = await fetch(`${API_BASE_URL}/operations/${operationId}/status`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const status = await response.json();
        setProgress(status.progress);

        if (status.status === 'completed') {
          setIsProcessing(false);
          // Set success to true since status is 'completed'
          setOperationResult({
            ...status.result,
            success: true
          });
          toast.success("Operation completed successfully!");
        } else if (status.status === 'failed') {
          setIsProcessing(false);
          // Set success to false since status is 'failed'
          setOperationResult({
            success: false,
            message: status.error || "Operation failed"
          });
          toast.error(status.error || "Operation failed");
        } else if (attempts < maxAttempts) {
          setTimeout(poll, 1000);
        } else {
          setIsProcessing(false);
          toast.error("Operation timed out");
        }
      } catch (error) {
        console.error("Polling error:", error);
        if (attempts < maxAttempts) {
          setTimeout(poll, 1000);
        } else {
          setIsProcessing(false);
          toast.error("Failed to check operation status");
        }
      }
    };

    poll();
  };

  // File validation
  const validateFile = (file: File, type: string): boolean => {
    console.log(`🔍 Validating file: ${file.name} for type: ${type}`);
    console.log("📋 Supported formats available:", supportedFormats);
    
    if (!supportedFormats) {
      console.log("❌ No supported formats loaded yet");
      toast.error("Supported formats not loaded. Please wait a moment and try again.");
      return false;
    }

    const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
    console.log(`📄 File extension detected: ${fileExtension}`);
    
    const formatData = supportedFormats[type as keyof SupportedFormats];
    console.log(`📋 Format data for ${type}:`, formatData);
    
    // Handle the new format structure from API
    const formats = formatData?.carrier_formats || [];
    console.log(`✅ Available formats for ${type}:`, formats);
    
    if (!formats.includes(fileExtension)) {
      console.log(`❌ File extension ${fileExtension} not supported`);
      toast.error(`Unsupported ${type} format. Supported: ${formats.join(', ')}`);
      return false;
    }

    console.log("✅ File validation passed");
    return true;
  };

  // Handle embedding operation
  const handleEmbed = async () => {
    console.log("🔄 Embed button clicked - starting validation...");
    
    // Validation
    if (batchMode) {
      if (!carrierFiles || carrierFiles.length === 0) {
        console.log("❌ Validation failed: No carrier files selected for batch mode");
        toast.error("Please select at least one carrier file for batch processing");
        return;
      }
      console.log(`✅ Batch mode: ${carrierFiles.length} files selected`);
    } else {
      if (!carrierFile) {
        console.log("❌ Validation failed: No carrier file selected");
        toast.error("Please select a carrier file");
        return;
      }
      console.log(`✅ Single mode: File selected - ${carrierFile.name}`);
    }

    // Copyright validation
    if (!authorName.trim()) {
      console.log("❌ Validation failed: No author name");
      toast.error("Please enter the author name");
      return;
    }
    console.log(`✅ Author name: ${authorName}`);
    
    if (!copyrightAlias.trim()) {
      console.log("❌ Validation failed: No copyright alias");
      toast.error("Please enter the copyright alias");
      return;
    }
    console.log(`✅ Copyright alias: ${copyrightAlias}`);
    // Timestamp is optional - will be auto-generated if empty

    if (!password.trim()) {
      console.log("❌ Validation failed: No password");
      toast.error("Please enter a password");
      return;
    }
    console.log("✅ Password provided");

    // Validate file format(s)
    console.log(`🔍 Validating file formats for carrier type: ${carrierType}`);
    if (batchMode) {
      for (let i = 0; i < carrierFiles.length; i++) {
        if (!validateFile(carrierFiles[i], carrierType)) {
          console.log(`❌ File validation failed for: ${carrierFiles[i].name}`);
          toast.error(`Validation failed for file ${i + 1}: ${carrierFiles[i].name}`);
          return;
        }
      }
      console.log("✅ All batch files validated successfully");
    } else {
      if (!validateFile(carrierFile, carrierType)) {
        console.log(`❌ File validation failed for: ${carrierFile.name}`);
        return;
      }
      console.log("✅ Carrier file validated successfully");
    }

    console.log("🚀 Starting embed process...");
    setIsProcessing(true);
    setProgress(0);
    setOperationResult(null);
    setCurrentOperationId(null);
    
    try {
      const formData = new FormData();
      
      if (batchMode) {
        // Add all carrier files for batch processing
        carrierFiles.forEach((file, index) => {
          formData.append('carrier_files', file);
        });
      } else {
        // Single file processing
        formData.append('carrier_file', carrierFile);
        formData.append('carrier_type', carrierType);
      }
      
      formData.append('content_type', 'text'); // Always text for copyright
      formData.append('password', password);
      formData.append('encryption_type', encryptionType);

      // Add project information if provided
      if (projectName.trim()) {
        formData.append('project_name', projectName.trim());
      }
      if (projectDescription.trim()) {
        formData.append('project_description', projectDescription.trim());
      }

      // Create copyright JSON object with user-friendly timestamp
      const currentDate = new Date();
      const userFriendlyTimestamp = timestamp.trim() || formatTimestampForHumans(currentDate);
      
      const copyrightData = {
        author_name: authorName.trim(),
        copyright_alias: copyrightAlias.trim(),
        timestamp: userFriendlyTimestamp
      };
      formData.append('text_content', JSON.stringify(copyrightData));

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const endpoint = batchMode ? `${API_BASE_URL}/embed-batch` : `${API_BASE_URL}/embed`;
      console.log(`📡 Making API call to: ${endpoint}`);
      console.log("📦 FormData contents:");
      for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`  ${key}: File(${value.name}, ${value.size} bytes)`);
        } else {
          console.log(`  ${key}: ${value}`);
        }
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      console.log(`📡 API Response: ${response.status}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.log("❌ API Error:", errorData);
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log("✅ API Success:", result);
      setCurrentOperationId(result.operation_id);
      toast.success("Copyright embedding started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      
      // Clean up backend error messages for better UX
      let errorMessage = error.message || "Copyright embedding failed";
      
      // Filter out technical backend errors that confuse users
      if (errorMessage.includes("NoneType") || 
          errorMessage.includes("subscriptable") ||
          errorMessage.includes("steganography_operations") ||
          errorMessage.includes("PGRST205") ||
          errorMessage.includes("schema cache")) {
        errorMessage = "Operation may have completed but database logging failed. Please check your outputs folder for the result file.";
      }
      
      // Handle HTTP errors more gracefully
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file format or missing required information.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Service not available. Please ensure the backend is running.";
      }
      
      toast.error(errorMessage);
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
      const formData = new FormData();
      formData.append('stego_file', extractFile);  // Backend expects 'stego_file', not 'carrier_file'
      formData.append('password', password);
      formData.append('output_format', 'auto');

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

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
      toast.success("Copyright extraction started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      
      let errorMessage = error.message || "Copyright extraction failed";
      
      if (errorMessage.includes("NoneType") || 
          errorMessage.includes("subscriptable") ||
          errorMessage.includes("steganography_operations") ||
          errorMessage.includes("PGRST205") ||
          errorMessage.includes("schema cache")) {
        errorMessage = "Operation may have completed but database logging failed. Please check your outputs folder for the result file.";
      }
      
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file format or password incorrect.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Service not available. Please ensure the backend is running.";
      }
      
      toast.error(errorMessage);
      console.error("Extract error:", error);
    }
  };

  // Download result file
  const downloadResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation ID available for download");
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/operations/${currentOperationId}/download`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = operationResult?.filename || operationResult?.output_filename || 'copyright_result.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success("File downloaded successfully!");
    } catch (error) {
      console.error("Download error:", error);
      toast.error("Failed to download file");
    }
  };

  // Utility function to format file sizes
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Helper function to parse and validate copyright data
  const parseCopyrightData = (textContent: string) => {
    try {
      const data = JSON.parse(textContent);
      if (data.author_name && data.copyright_alias && data.timestamp) {
        return data;
      }
    } catch (e) {
      // Not valid JSON or missing required fields
    }
    return null;
  };

  // Generate secure password
  const generatePassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setPassword(password);
    toast.success("Password generated successfully!");
  };

  // Download copyright information as JSON file
  const downloadCopyrightInfo = (copyrightData: any) => {
    const dataStr = JSON.stringify(copyrightData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `copyright-info-${copyrightData.author_name?.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success("Copyright information downloaded!");
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
                <div className="flex items-center gap-3">
                  <Shield className="h-8 w-8 text-primary" />
                  <div>
                    <h1 className="text-3xl font-bold">Copyright Protection</h1>
                    <p className="text-muted-foreground">Secure your intellectual property with invisible copyright steganography</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Main Content */}
        <section className="py-8">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="embed" className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Embed Copyright
                  </TabsTrigger>
                  <TabsTrigger value="extract" className="flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    Extract Copyright
                  </TabsTrigger>
                  <TabsTrigger value="settings" className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    Project Settings
                  </TabsTrigger>
                </TabsList>

                {/* Embed Tab */}
                <TabsContent value="embed" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        Embed Copyright Information
                      </CardTitle>
                      <CardDescription>
                        Hide your copyright details invisibly within media files to protect your intellectual property.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Batch Mode Toggle */}
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="batch-mode"
                          checked={batchMode}
                          onCheckedChange={setBatchMode}
                        />
                        <Label htmlFor="batch-mode">
                          Batch Processing (Process multiple files at once)
                        </Label>
                      </div>

                      {/* Carrier File Selection */}
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="carrier-type">Carrier File Type</Label>
                          <Select value={carrierType} onValueChange={setCarrierType}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="image">
                                <div className="flex items-center gap-2">
                                  <FileImage className="h-4 w-4" />
                                  Image File
                                </div>
                              </SelectItem>
                              <SelectItem value="audio">
                                <div className="flex items-center gap-2">
                                  <FileAudio className="h-4 w-4" />
                                  Audio File
                                </div>
                              </SelectItem>
                              <SelectItem value="video">
                                <div className="flex items-center gap-2">
                                  <FileVideo className="h-4 w-4" />
                                  Video File
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
                          {supportedFormats && (
                            <p className="text-xs text-muted-foreground">
                              Supported formats: {supportedFormats[carrierType as keyof SupportedFormats]?.carrier_formats?.join(", ") || "Loading..."}
                            </p>
                          )}
                        </div>

                        {!batchMode ? (
                          <div className="space-y-2">
                            <Label htmlFor="carrier-file">Carrier File</Label>
                            <div className="flex items-center gap-2">
                              <Input
                                id="carrier-file"
                                type="file"
                                onChange={(e) => setCarrierFile(e.target.files?.[0] || null)}
                                accept={supportedFormats ? supportedFormats[carrierType as keyof SupportedFormats]?.carrier_formats?.map(ext => `.${ext}`).join(',') || '' : ''}
                              />
                            </div>
                            {carrierFile && (
                              <p className="text-sm text-muted-foreground">
                                Selected: {carrierFile.name} ({formatFileSize(carrierFile.size)})
                              </p>
                            )}
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Label htmlFor="carrier-files">Carrier Files (Multiple)</Label>
                            <div className="flex items-center gap-2">
                              <Input
                                id="carrier-files"
                                type="file"
                                multiple
                                onChange={(e) => setCarrierFiles(Array.from(e.target.files || []))}
                                accept={supportedFormats ? supportedFormats[carrierType as keyof SupportedFormats]?.carrier_formats?.map(ext => `.${ext}`).join(',') || '' : ''}
                              />
                            </div>
                            {carrierFiles.length > 0 && (
                              <div className="text-sm text-muted-foreground space-y-1">
                                <p>Selected {carrierFiles.length} files:</p>
                                {carrierFiles.slice(0, 3).map((file, index) => (
                                  <p key={index} className="ml-2">• {file.name} ({formatFileSize(file.size)})</p>
                                ))}
                                {carrierFiles.length > 3 && (
                                  <p className="ml-2">• ... and {carrierFiles.length - 3} more files</p>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Copyright Information Section */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Shield className="h-5 w-5 text-blue-600" />
                          <Label className="text-lg font-medium">Copyright Information</Label>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="author-name">Author Name *</Label>
                            <Input
                              id="author-name"
                              value={authorName}
                              onChange={(e) => setAuthorName(e.target.value)}
                              placeholder="Enter author's full name..."
                            />
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor="copyright-alias">Copyright Alias *</Label>
                            <Input
                              id="copyright-alias"
                              value={copyrightAlias}
                              onChange={(e) => setCopyrightAlias(e.target.value)}
                              placeholder="Enter copyright alias or company..."
                            />
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="timestamp">Timestamp</Label>
                          <div className="flex gap-2">
                            <Input
                              id="timestamp"
                              value={timestamp}
                              onChange={(e) => setTimestamp(e.target.value)}
                              placeholder="Enter custom timestamp or leave for auto-generated..."
                              className="flex-1"
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => setTimestamp(formatTimestampForHumans(new Date()))}
                              className="shrink-0"
                            >
                              <Calendar className="h-4 w-4 mr-2" />
                              Use Current Time
                            </Button>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Current time will be used if left empty. Format: ISO 8601 (e.g., {new Date().toISOString()})
                          </p>
                        </div>
                      </div>

                      <Separator />

                      {/* Password Settings */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2">
                          <Lock className="h-5 w-5 text-primary" />
                          <Label className="text-lg font-medium">Password Security</Label>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="password">Password *</Label>
                          <div className="flex gap-2">
                            <Input
                              id="password"
                              type={showPassword ? "text" : "password"}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Enter a strong password..."
                              className="flex-1"
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => setShowPassword(!showPassword)}
                              className="shrink-0"
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                            <Button
                              type="button"
                              variant="outline"
                              onClick={generatePassword}
                              className="shrink-0"
                            >
                              <RefreshCw className="h-4 w-4 mr-2" />
                              Generate
                            </Button>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Uses AES-256-GCM encryption for maximum security
                          </p>
                        </div>
                      </div>

                      <Button 
                        onClick={() => {
                          console.log("🎯 Embed button clicked!");
                          handleEmbed();
                        }} 
                        disabled={isProcessing} 
                        className="w-full"
                        size="lg"
                      >
                        {isProcessing ? (
                          <>Processing... ({progress}%)</>
                        ) : (
                          <>
                            <Shield className="h-4 w-4 mr-2" />
                            Embed Copyright Information
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Extract Tab */}
                <TabsContent value="extract" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="h-5 w-5" />
                        Extract Copyright Information
                      </CardTitle>
                      <CardDescription>
                        Extract and verify copyright information from protected media files.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="space-y-2">
                        <Label htmlFor="extract-file">File to Extract From</Label>
                        <Input
                          id="extract-file"
                          type="file"
                          onChange={(e) => setExtractFile(e.target.files?.[0] || null)}
                        />
                        {extractFile && (
                          <p className="text-sm text-muted-foreground">
                            Selected: {extractFile.name} ({formatFileSize(extractFile.size)})
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="extract-password">Password *</Label>
                        <div className="flex gap-2">
                          <Input
                            id="extract-password"
                            type={showPassword ? "text" : "password"}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter the password..."
                            className="flex-1"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => setShowPassword(!showPassword)}
                            className="shrink-0"
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Uses AES-256-GCM decryption
                        </p>
                      </div>

                      <Button 
                        onClick={handleExtract} 
                        disabled={isProcessing} 
                        className="w-full"
                        size="lg"
                      >
                        {isProcessing ? (
                          <>Processing... ({progress}%)</>
                        ) : (
                          <>
                            <Eye className="h-4 w-4 mr-2" />
                            Extract Copyright Information
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Project Settings Tab */}
                <TabsContent value="settings" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Settings className="h-5 w-5" />
                        Project Settings
                      </CardTitle>
                      <CardDescription>
                        Configure project information and metadata for your copyright operations.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="settings-project-name">Project Name</Label>
                          <Input
                            id="settings-project-name"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="Enter project name..."
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="settings-project-description">Project Description</Label>
                          <Textarea
                            id="settings-project-description"
                            value={projectDescription}
                            onChange={(e) => setProjectDescription(e.target.value)}
                            placeholder="Brief description of the project..."
                            rows={4}
                          />
                        </div>
                      </div>
                      
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          Project settings are optional and will be included in the operation metadata for better organization and tracking.
                        </AlertDescription>
                      </Alert>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>

              {/* Progress and Results */}
              {isProcessing && (
                <Card className="mt-6">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm font-medium">Processing...</Label>
                        <span className="text-sm text-muted-foreground">{progress}%</span>
                      </div>
                      <Progress value={progress} className="w-full" />
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Operation Result */}
              {operationResult && !isProcessing && (
                <Card className="mt-6">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <Alert className={operationResult.success ? "border-green-200 bg-green-50 dark:bg-green-950/30" : "border-red-200 bg-red-50 dark:bg-red-950/30"}>
                        <div className="flex items-center gap-2">
                          {operationResult.success ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-red-600" />
                          )}
                          <span className="font-medium">
                            {operationResult.success ? "Success" : "Failed"}
                          </span>
                        </div>
                        <AlertDescription className="mt-2">
                          {operationResult.message}
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
                          {(operationResult.text_content || operationResult.preview) && (() => {
                            const textData = operationResult.text_content || operationResult.preview;
                            const copyrightData = parseCopyrightData(textData);
                            
                            if (copyrightData) {
                              // Display copyright information prominently
                              return (
                                <div className="space-y-4">
                                  <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
                                    <div className="flex items-center justify-between mb-3">
                                      <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 flex items-center gap-2">
                                        <Shield className="h-5 w-5" />
                                        Copyright Information Verified
                                      </h3>
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => downloadCopyrightInfo(copyrightData)}
                                        className="text-green-700 border-green-300 hover:bg-green-100"
                                      >
                                        <Download className="h-4 w-4 mr-2" />
                                        Download JSON
                                      </Button>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                      <div className="space-y-1">
                                        <p className="font-medium text-green-700 dark:text-green-300">Author Name:</p>
                                        <p className="text-green-800 dark:text-green-200 font-mono bg-white dark:bg-green-900/20 p-2 rounded">
                                          {copyrightData.author_name}
                                        </p>
                                      </div>
                                      <div className="space-y-1">
                                        <p className="font-medium text-green-700 dark:text-green-300">Copyright Alias:</p>
                                        <p className="text-green-800 dark:text-green-200 font-mono bg-white dark:bg-green-900/20 p-2 rounded">
                                          {copyrightData.copyright_alias}
                                        </p>
                                      </div>
                                      <div className="space-y-1">
                                        <p className="font-medium text-green-700 dark:text-green-300">Timestamp:</p>
                                        <p className="text-green-800 dark:text-green-200 font-mono bg-white dark:bg-green-900/20 p-2 rounded">
                                          {displayTimestamp(copyrightData.timestamp)}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              );
                            } else {
                              // Display regular text content
                              return (
                                <div className="space-y-1">
                                  <p className="text-sm font-medium">Text Content:</p>
                                  <div className="p-2 bg-background rounded border max-h-32 overflow-y-auto">
                                    <pre className="text-xs font-mono whitespace-pre-wrap">{textData}</pre>
                                  </div>
                                </div>
                              );
                            }
                          })()}
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
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}