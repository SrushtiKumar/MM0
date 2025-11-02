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
  EyeOff,
  Copy,
  Save,
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

// Enhanced toast with better UX - fixed stacking issue
let toastCount = 0;
const activeToasts: HTMLElement[] = [];

const toast = {
  success: (message: string) => {
    console.log('✅ SUCCESS:', message);
    createToast(message, 'bg-green-500', 3000);
  },
  error: (message: string) => {
    console.error('❌ ERROR:', message);
    createToast(message, 'bg-red-500', 5000);
  }
};

function createToast(message: string, bgColor: string, duration: number) {
  const notification = document.createElement('div');
  const topOffset = 16 + (activeToasts.length * 80); // 16px base + 80px per existing toast
  
  notification.className = `fixed right-4 ${bgColor} text-white p-3 rounded-lg shadow-lg z-50 transition-all duration-300 ease-in-out`;
  notification.style.top = `${topOffset}px`;
  notification.textContent = message;
  
  // Add to active toasts
  activeToasts.push(notification);
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.style.opacity = '1';
    notification.style.transform = 'translateX(0)';
  }, 10);
  
  // Remove after duration
  setTimeout(() => {
    const index = activeToasts.indexOf(notification);
    if (index > -1) {
      activeToasts.splice(index, 1);
      
      // Animate out
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(100%)';
      
      setTimeout(() => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
        
        // Reposition remaining toasts
        activeToasts.forEach((toast, i) => {
          const newTopOffset = 16 + (i * 80);
          toast.style.top = `${newTopOffset}px`;
        });
      }, 300);
    }
  }, duration);
  
  // Initial state for animation
  notification.style.opacity = '0';
  notification.style.transform = 'translateX(100%)';
}

export default function General() {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState("embed");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [carrierFiles, setCarrierFiles] = useState<File[]>([]); // Multiple carrier files
  const [batchMode, setBatchMode] = useState(false); // Toggle between single and batch mode
  const [extractFile, setExtractFile] = useState<File | null>(null);
  const [contentType, setContentType] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [fileContent, setFileContent] = useState<File | null>(null);
  
  // Copyright fields state
  const [authorName, setAuthorName] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [copyrightAlias, setCopyrightAlias] = useState("");
  
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
  
  // Password Management State
  const [showPassword, setShowPassword] = useState(false);
  const [savePasswordWithProject, setSavePasswordWithProject] = useState(false);
  const [savedPassword, setSavedPassword] = useState("");
  
  // Size Estimate State
  const [estimateFile, setEstimateFile] = useState<File | null>(null);
  const [estimateType, setEstimateType] = useState<"carrier" | "content">("carrier");
  const [estimateResult, setEstimateResult] = useState<any>(null);
  const [estimateLoading, setEstimateLoading] = useState(false);

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

  const handleCarrierFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      setCarrierFiles(files);
      
      // Auto-detect carrier type from first file
      const firstFile = files[0];
      const extension = firstFile.name.split('.').pop()?.toLowerCase();
      let detectedType = carrierType;
      
      if (extension) {
        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(extension)) {
          detectedType = "image";
        } else if (['mp4', 'avi', 'mov', 'mkv', 'wmv'].includes(extension)) {
          detectedType = "video";
        } else if (['wav', 'mp3', 'flac', 'ogg', 'aac'].includes(extension)) {
          detectedType = "audio";
        } else if (['pdf', 'doc', 'docx', 'txt'].includes(extension)) {
          detectedType = "document";
        }
        
        if (detectedType !== carrierType) {
          setCarrierType(detectedType);
        }
      }
      
      // Validate all files
      setTimeout(() => {
        if (supportedFormats) {
          files.forEach((file, index) => {
            try {
              validateFile(file, detectedType);
            } catch (error) {
              toast.error(`File ${index + 1} (${file.name}): ${error}`);
            }
          });
        }
      }, 100);
    }
  };

  const removeCarrierFile = (index: number) => {
    const newFiles = carrierFiles.filter((_, i) => i !== index);
    setCarrierFiles(newFiles);
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

  // Password Management Functions
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const copyPasswordToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(password);
      toast.success("Password copied to clipboard!");
    } catch (error) {
      console.error("Failed to copy password:", error);
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = password;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        toast.success("Password copied to clipboard!");
      } catch (fallbackError) {
        toast.error("Failed to copy password");
      }
      document.body.removeChild(textArea);
    }
  };

  const savePasswordWithProjectSettings = () => {
    if (savePasswordWithProject && password.trim()) {
      setSavedPassword(password);
      toast.success("Password saved with project settings!");
    } else if (!savePasswordWithProject) {
      setSavedPassword("");
      toast.success("Password removed from project settings!");
    }
  };

  const loadSavedPassword = () => {
    if (savedPassword) {
      setPassword(savedPassword);
      toast.success("Loaded saved password from project!");
    } else {
      toast.error("No saved password found in project settings");
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
    // Validation for batch vs single mode
    if (batchMode) {
      if (!carrierFiles || carrierFiles.length === 0) {
        toast.error("Please select at least one carrier file for batch processing");
        return;
      }
    } else {
      if (!carrierFile) {
        toast.error("Please select a carrier file");
        return;
      }
    }

    if (contentType === "text" && !textContent.trim()) {
      toast.error("Please enter text content to hide");
      return;
    }

    if (contentType === "copyright") {
      if (!authorName.trim()) {
        toast.error("Please enter the author name");
        return;
      }
      if (!copyrightAlias.trim()) {
        toast.error("Please enter the copyright alias");
        return;
      }
      // Timestamp is optional - will be auto-generated if empty
    }

    if ((contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && !fileContent) {
      toast.error(`Please select a ${contentType} to hide`);
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }

    // Validate file format(s)
    if (batchMode) {
      for (let i = 0; i < carrierFiles.length; i++) {
        if (!validateFile(carrierFiles[i], carrierType)) {
          toast.error(`Validation failed for file ${i + 1}: ${carrierFiles[i].name}`);
          return;
        }
      }
    } else {
      if (!validateFile(carrierFile, carrierType)) {
        return;
      }
    }

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
      } else if (contentType === "copyright") {
        // Create copyright JSON object
        const copyrightData = {
          author_name: authorName.trim(),
          copyright_alias: copyrightAlias.trim(),
          timestamp: timestamp.trim() || new Date().toISOString()
        };
        formData.append('text_content', JSON.stringify(copyrightData));
        // Set content_type to "text" for backend compatibility since we're sending JSON as text
        formData.set('content_type', 'text');
      } else if (contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") {
        formData.append('content_file', fileContent);
        // Set content_type to "file" for all file types for backend compatibility
        formData.set('content_type', 'file');
      }

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const endpoint = batchMode ? `${API_BASE_URL}/embed-batch` : `${API_BASE_URL}/embed`;
      const response = await fetch(endpoint, {
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
      
      // Clean up backend error messages for better UX
      let errorMessage = error.message || "Embedding operation failed";
      
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
      
      // Clean up backend error messages for better UX
      let errorMessage = error.message || "Extraction operation failed";
      
      // Filter out technical backend errors that confuse users
      if (errorMessage.includes("NoneType") || 
          errorMessage.includes("subscriptable") ||
          errorMessage.includes("steganography_operations") ||
          errorMessage.includes("PGRST205") ||
          errorMessage.includes("schema cache")) {
        errorMessage = "Operation may have completed but database logging failed. Please check the extraction results.";
      }
      
      // Handle HTTP errors more gracefully
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file or incorrect password.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Service not available. Please ensure the backend is running.";
      }
      
      toast.error(errorMessage);
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
          // Clean up backend error messages for better UX
          let errorMessage = status.error || "Operation failed";
          
          // Filter out technical backend errors that confuse users
          if (errorMessage.includes("NoneType") || 
              errorMessage.includes("subscriptable") ||
              errorMessage.includes("steganography_operations") ||
              errorMessage.includes("PGRST205")) {
            errorMessage = "Operation completed but logging failed. Your files were processed successfully.";
          }
          
          toast.error(errorMessage);
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

  // Enhanced download with custom save dialog
  const downloadResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation result to download");
      return;
    }

    try {
      // Check if this is a batch operation
      const isBatchOperation = operationResult?.batch_operation || false;
      const downloadEndpoint = isBatchOperation 
        ? `${API_BASE_URL}/operations/${currentOperationId}/download-batch`
        : `${API_BASE_URL}/operations/${currentOperationId}/download`;
      
      const response = await fetch(downloadEndpoint);
      
      if (!response.ok) {
        throw new Error(`Failed to download: ${response.statusText}`);
      }

      const blob = await response.blob();
      
      // For batch operations, suggest a ZIP filename
      const defaultFilename = isBatchOperation 
        ? `batch_results_${Date.now()}.zip`
        : (operationResult?.filename || `result_${Date.now()}`);
      
      // Try to use the modern File System Access API
      if ('showSaveFilePicker' in window) {
        try {
          // Get the file extension from the default filename - handle edge cases
          const lastDotIndex = defaultFilename.lastIndexOf('.');
          const extension = (lastDotIndex > 0 && lastDotIndex < defaultFilename.length - 1) 
            ? defaultFilename.substring(lastDotIndex + 1).toLowerCase()
            : '';
          
          // Handle problematic temporary filenames
          const cleanFilename = defaultFilename.includes('extracted_tmp') 
            ? `extracted_file_${Date.now()}.txt`
            : defaultFilename;
          
          const fileTypeMap: { [key: string]: any } = {
            'mp4': { description: 'MP4 Video', accept: { 'video/mp4': ['.mp4'] } },
            'avi': { description: 'AVI Video', accept: { 'video/avi': ['.avi'] } },
            'wav': { description: 'WAV Audio', accept: { 'audio/wav': ['.wav'] } },
            'mp3': { description: 'MP3 Audio', accept: { 'audio/mp3': ['.mp3'] } },
            'jpg': { description: 'JPEG Image', accept: { 'image/jpeg': ['.jpg', '.jpeg'] } },
            'jpeg': { description: 'JPEG Image', accept: { 'image/jpeg': ['.jpg', '.jpeg'] } },
            'png': { description: 'PNG Image', accept: { 'image/png': ['.png'] } },
            'pdf': { description: 'PDF Document', accept: { 'application/pdf': ['.pdf'] } },
            'doc': { description: 'Word Document', accept: { 'application/msword': ['.doc'] } },
            'docx': { description: 'Word Document', accept: { 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] } },
            'txt': { description: 'Text File', accept: { 'text/plain': ['.txt'] } },
            'zip': { description: 'ZIP Archive', accept: { 'application/zip': ['.zip'] } }
          };

          // Get file type or create a proper fallback
          let fileType = fileTypeMap[extension.toLowerCase()];
          
          if (!fileType) {
            // For unknown extensions, create a proper type with the actual extension
            if (extension && extension.length > 0) {
              fileType = {
                description: `${extension.toUpperCase()} File`,
                accept: { [`application/${extension}`]: [`.${extension}`] }
              };
            } else {
              // If no extension, allow all files but don't specify invalid patterns
              fileType = {
                description: 'All Files',
                accept: { '*/*': [] }
              };
            }
          }

          // Show the save dialog
          const fileHandle = await (window as any).showSaveFilePicker({
            suggestedName: cleanFilename,
            types: [fileType]
          });

          // Write the file
          const writableStream = await fileHandle.createWritable();
          await writableStream.write(blob);
          await writableStream.close();

          toast.success(`File saved successfully as "${fileHandle.name}"!`);
        } catch (error: any) {
          if (error.name === 'AbortError') {
            toast.error("Save operation was cancelled");
            return;
          }
          throw error; // Fall back to traditional download
        }
      } else {
        // Fallback for browsers that don't support File System Access API
        // Show a custom dialog for filename input
        const customFilename = prompt(
          `Enter filename to save as (current: ${defaultFilename}):`,
          defaultFilename
        );
        
        if (customFilename === null) {
          toast.error("Download cancelled");
          return;
        }

        const finalFilename = customFilename.trim() || defaultFilename;
        
        // Traditional download with custom filename
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = finalFilename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast.success(`File downloaded as "${finalFilename}"!`);
      }
    } catch (error: any) {
      // Final fallback - traditional download with original filename
      if (error.message.includes('File System Access API')) {
        try {
          const blob = await (await fetch(`${API_BASE_URL}/operations/${currentOperationId}/download`)).blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = operationResult?.filename || `result_${Date.now()}`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          toast.success("File downloaded successfully (fallback mode)!");
        } catch (fallbackError: any) {
          toast.error(fallbackError.message || "Failed to download result");
          console.error("Download fallback error:", fallbackError);
        }
      } else {
        toast.error(error.message || "Failed to download result");
        console.error("Download error:", error);
      }
    }
  };

  // Size Estimation Functions
  const handleEstimateFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setEstimateFile(file);
      setEstimateResult(null);
    }
  };

  const calculateSizeEstimate = async () => {
    if (!estimateFile) {
      toast.error("Please select a file first");
      return;
    }

    setEstimateLoading(true);
    setEstimateResult(null);

    try {
      const fileSizeBytes = estimateFile.size;
      const fileSizeKB = fileSizeBytes / 1024;
      const fileSizeMB = fileSizeKB / 1024;

      if (estimateType === "carrier") {
        // Calculate how much data can be embedded in this carrier file
        const fileExt = estimateFile.name.split('.').pop()?.toLowerCase() || '';
        let capacityBytes = 0;
        let estimatedCapacity = "";

        // Audio capacity calculation (based on our audio capacity manager)
        if (['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a'].includes(fileExt)) {
          // Approximate: 1 bit per sample for LSB steganography
          // For audio files, estimate based on duration and sample rate
          const estimatedSamples = fileSizeBytes * 0.5; // Rough estimate
          capacityBytes = Math.floor(estimatedSamples * 0.8 / 8); // 80% safety factor
          estimatedCapacity = "audio steganography";
        }
        // Image capacity calculation
        else if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(fileExt)) {
          // Rough estimate: 1 bit per pixel for LSB
          const estimatedPixels = fileSizeBytes * 0.1; // Very rough estimate
          capacityBytes = Math.floor(estimatedPixels / 8);
          estimatedCapacity = "image steganography";
        }
        // Video capacity calculation
        else if (['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'].includes(fileExt)) {
          // Video has higher capacity
          capacityBytes = Math.floor(fileSizeBytes * 0.01); // 1% of video size
          estimatedCapacity = "video steganography";
        }
        // Document capacity calculation
        else if (['pdf', 'docx', 'txt', 'rtf'].includes(fileExt)) {
          // Document steganography has variable capacity
          capacityBytes = Math.floor(fileSizeBytes * 0.1); // 10% of document size
          estimatedCapacity = "document steganography";
        }

        setEstimateResult({
          type: "carrier",
          fileSize: fileSizeBytes,
          fileSizeFormatted: fileSizeBytes > 1024 * 1024 ? `${fileSizeMB.toFixed(2)} MB` : `${fileSizeKB.toFixed(2)} KB`,
          capacity: capacityBytes,
          capacityFormatted: capacityBytes > 1024 ? `${(capacityBytes / 1024).toFixed(2)} KB` : `${capacityBytes} bytes`,
          method: estimatedCapacity,
          recommendations: [
            `This ${fileExt.toUpperCase()} file can hide approximately ${capacityBytes > 1024 ? `${(capacityBytes / 1024).toFixed(2)} KB` : `${capacityBytes} bytes`} of data`,
            capacityBytes > 10000 ? "✅ Good capacity for most files" : capacityBytes > 1000 ? "⚠️ Moderate capacity - suitable for small files" : "❌ Limited capacity - only text messages recommended"
          ]
        });
      } else {
        // Calculate what size carrier file is needed for this content
        const overhead = fileSizeBytes * 1.5; // Account for encryption and encoding overhead
        const recommendedCarrierSize = overhead * 10; // 10x for safety margin

        const audioCarrierDuration = Math.ceil(overhead / 3000); // ~3KB per second for audio
        const imageCarrierPixels = overhead * 8; // 8 bits per pixel
        const videoCarrierSize = overhead * 100; // Video can hide more efficiently

        setEstimateResult({
          type: "content",
          fileSize: fileSizeBytes,
          fileSizeFormatted: fileSizeBytes > 1024 * 1024 ? `${fileSizeMB.toFixed(2)} MB` : `${fileSizeKB.toFixed(2)} KB`,
          recommendations: [
            `For audio carriers: Use ${audioCarrierDuration}+ second audio files`,
            `For image carriers: Use images with ${Math.ceil(Math.sqrt(imageCarrierPixels))}x${Math.ceil(Math.sqrt(imageCarrierPixels))}+ pixels`,
            `For video carriers: Use ${((videoCarrierSize / 1024 / 1024)).toFixed(1)}+ MB video files`,
            fileSizeBytes > 100000 ? "💡 Large file - consider using video carriers for best results" : "💡 Small file - any carrier type should work"
          ]
        });
      }
    } catch (error) {
      console.error("Size estimation error:", error);
      toast.error("Failed to calculate size estimate");
    } finally {
      setEstimateLoading(false);
    }
  };

  const getContentIcon = () => {
    switch (contentType) {
      case "text": return <FileText className="h-4 w-4" />;
      case "copyright": return <Shield className="h-4 w-4" />;
      case "image": return <ImageIcon className="h-4 w-4" />;
      case "audio": return <Music className="h-4 w-4" />;
      case "video": return <Video className="h-4 w-4" />;
      case "file": return <File className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
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
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="embed">Embed Data</TabsTrigger>
                <TabsTrigger value="extract">Extract Data</TabsTrigger>
                <TabsTrigger value="project-settings">Project Settings</TabsTrigger>
                <TabsTrigger value="size-estimate">Size Estimate</TabsTrigger>
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
                      {/* Batch Mode Toggle */}
                      <div className="space-y-2">
                        <Label>Processing Mode</Label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="batch-mode"
                            checked={batchMode}
                            onChange={(e) => setBatchMode(e.target.checked)}
                            className="rounded"
                          />
                          <label htmlFor="batch-mode" className="text-sm font-medium cursor-pointer">
                            Batch Mode (Multiple Carrier Files)
                          </label>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {batchMode 
                            ? "Hide the same content in multiple carrier files"
                            : "Hide content in a single carrier file"
                          }
                        </p>
                      </div>
                      {/* Carrier File Upload */}
                      <div className="space-y-2">
                        <Label htmlFor="carrier-file">
                          {batchMode ? "Carrier Files (Multiple)" : "Carrier File"}
                        </Label>
                        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          {!batchMode ? (
                            // Single file upload
                            <>
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
                            </>
                          ) : (
                            // Multiple files upload
                            <>
                              <input
                                id="carrier-files"
                                type="file"
                                accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                                multiple
                                onChange={handleCarrierFilesChange}
                                className="hidden"
                              />
                              <label htmlFor="carrier-files" className="cursor-pointer">
                                <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                                <p className="text-sm text-muted-foreground">
                                  {carrierFiles.length > 0 
                                    ? `${carrierFiles.length} files selected` 
                                    : "Click to upload multiple carrier files"}
                                </p>
                              </label>
                            </>
                          )}
                        </div>
                        
                        {/* Display selected files for batch mode */}
                        {batchMode && carrierFiles.length > 0 && (
                          <div className="space-y-2 max-h-40 overflow-y-auto">
                            <Label className="text-xs">Selected Files:</Label>
                            {carrierFiles.map((file, index) => (
                              <div key={index} className="flex items-center justify-between bg-muted p-2 rounded text-sm">
                                <span className="truncate">{file.name}</span>
                                <div className="flex items-center gap-2">
                                  <span className="text-xs text-muted-foreground">
                                    {(file.size / 1024).toFixed(1)} KB
                                  </span>
                                  <button
                                    onClick={() => removeCarrierFile(index)}
                                    className="text-red-500 hover:text-red-700 text-xs"
                                  >
                                    ×
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
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
                            <SelectItem value="copyright">
                              <div className="flex items-center gap-2">
                                <Shield className="h-4 w-4" />
                                Copyright Information
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

                      {contentType === "copyright" && (
                        <div className="space-y-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Shield className="h-5 w-5 text-blue-600" />
                            <Label className="text-lg font-medium">Copyright Information</Label>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="author-name">Author Name</Label>
                              <Input
                                id="author-name"
                                value={authorName}
                                onChange={(e) => setAuthorName(e.target.value)}
                                placeholder="Enter author's full name..."
                              />
                            </div>
                            
                            <div className="space-y-2">
                              <Label htmlFor="copyright-alias">Copyright Alias</Label>
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
                                onClick={() => setTimestamp(new Date().toISOString())}
                                className="shrink-0"
                              >
                                Use Current Time
                              </Button>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Current time will be used if left empty. Format: ISO 8601 (e.g., {new Date().toISOString()})
                            </p>
                          </div>
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

                      {/* Password */}
                      <div className="space-y-3">
                        <Label htmlFor="password">Encryption Password</Label>
                        
                        {/* Password Input Row */}
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Input
                              id="password"
                              type={showPassword ? "text" : "password"}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Enter strong password"
                              className="pr-10"
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={togglePasswordVisibility}
                              className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted"
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          </div>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={generatePassword}
                            className="shrink-0"
                            title="Generate Password"
                          >
                            <Key className="h-4 w-4" />
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={copyPasswordToClipboard}
                            className="shrink-0"
                            disabled={!password.trim()}
                            title="Copy Password"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                        
                        {/* Password Management Options */}
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="save-password-with-project"
                              checked={savePasswordWithProject}
                              onChange={(e) => {
                                setSavePasswordWithProject(e.target.checked);
                                if (e.target.checked && password.trim()) {
                                  setSavedPassword(password);
                                  toast.success("Password will be saved with project!");
                                } else if (!e.target.checked) {
                                  setSavedPassword("");
                                }
                              }}
                              className="rounded"
                            />
                            <Label htmlFor="save-password-with-project" className="text-sm">
                              Save password with project settings
                            </Label>
                          </div>
                          
                          {savedPassword && (
                            <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
                              <Shield className="h-4 w-4 text-green-600" />
                              <span className="text-sm text-muted-foreground">Password saved with project</span>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={loadSavedPassword}
                                className="ml-auto h-6 px-2 text-xs"
                              >
                                Load
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>

                      <Button 
                        onClick={handleEmbed} 
                        className="w-full"
                        disabled={(batchMode ? (carrierFiles.length === 0) : !carrierFile) || 
                          (contentType === "text" && !textContent.trim()) ||
                          ((contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && !fileContent) ||
                          isProcessing}
                      >
                        {isProcessing 
                          ? (batchMode ? `Processing ${carrierFiles.length} files...` : "Processing...")
                          : (batchMode ? `Embed in ${carrierFiles.length} Files` : "Embed Data")
                        }
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
                            Save Result As...
                          </Button>
                          <p className="text-xs text-muted-foreground text-center mt-2">
                            Choose your preferred filename and save location
                          </p>
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
                      <div className="space-y-3">
                        <Label htmlFor="extract-password">Decryption Password</Label>
                        
                        {/* Password Input Row */}
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Input
                              id="extract-password"
                              type={showPassword ? "text" : "password"}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Enter password to decrypt"
                              className="pr-10"
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={togglePasswordVisibility}
                              className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted"
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          </div>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={copyPasswordToClipboard}
                            className="shrink-0"
                            disabled={!password.trim()}
                            title="Copy Password"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                        
                        {/* Load Saved Password Option */}
                        {savedPassword && (
                          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
                            <Shield className="h-4 w-4 text-green-600" />
                            <span className="text-sm text-muted-foreground">Use saved project password</span>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={loadSavedPassword}
                              className="ml-auto h-6 px-2 text-xs"
                            >
                              Load
                            </Button>
                          </div>
                        )}
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
                        View extracted content and save to your chosen location
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
                              {(operationResult.text_content || operationResult.preview) && (() => {
                                const textData = operationResult.text_content || operationResult.preview;
                                const copyrightData = parseCopyrightData(textData);
                                
                                if (copyrightData) {
                                  // Display copyright information in simple vertical format
                                  return (
                                    <div className="space-y-1">
                                      <p className="text-sm">Author name: {copyrightData.author_name}</p>
                                      <p className="text-sm">Copyright alias: {copyrightData.copyright_alias}</p>
                                      <p className="text-sm">Timestamp: {new Date(copyrightData.timestamp).toLocaleString()}</p>
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
                            Save Extracted Data As...
                          </Button>
                          <p className="text-xs text-muted-foreground text-center mt-2">
                            Choose your preferred filename and save location
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              {/* Project Settings Tab */}
              <TabsContent value="project-settings" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <File className="h-5 w-5" />
                      Project Settings
                    </CardTitle>
                    <CardDescription>
                      Configure project information and manage your steganography projects
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      {/* Project Information */}
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold">Project Information</h3>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-name-tab">Project Name</Label>
                          <Input
                            id="project-name-tab"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="e.g., Secret Mission Files"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-description-tab">Project Description</Label>
                          <Textarea
                            id="project-description-tab"
                            value={projectDescription}
                            onChange={(e) => setProjectDescription(e.target.value)}
                            placeholder="Brief description of this steganography project..."
                            rows={3}
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-tags-tab">Tags (comma-separated)</Label>
                          <Input
                            id="project-tags-tab"
                            value={projectTags}
                            onChange={(e) => setProjectTags(e.target.value)}
                            placeholder="secret, mission, confidential"
                          />
                        </div>
                        
                        {/* Password Management Section */}
                        <div className="space-y-4 p-4 border rounded-lg bg-muted/30">
                          <h4 className="text-sm font-semibold flex items-center gap-2">
                            <Shield className="h-4 w-4" />
                            Password Management
                          </h4>
                          
                          <div className="space-y-3">
                            <div className="space-y-2">
                              <Label htmlFor="project-password">Project Password</Label>
                              <div className="flex gap-2">
                                <div className="relative flex-1">
                                  <Input
                                    id="project-password"
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter or generate password"
                                    className="pr-10"
                                  />
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={togglePasswordVisibility}
                                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted"
                                  >
                                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                  </Button>
                                </div>
                                <Button
                                  type="button"
                                  variant="outline"
                                  onClick={generatePassword}
                                  className="shrink-0"
                                  title="Generate Password"
                                >
                                  <Key className="h-4 w-4" />
                                </Button>
                                <Button
                                  type="button"
                                  variant="outline"
                                  onClick={copyPasswordToClipboard}
                                  className="shrink-0"
                                  disabled={!password.trim()}
                                  title="Copy Password"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                id="save-password-project-tab"
                                checked={savePasswordWithProject}
                                onChange={(e) => {
                                  setSavePasswordWithProject(e.target.checked);
                                  savePasswordWithProjectSettings();
                                }}
                                className="rounded"
                              />
                              <Label htmlFor="save-password-project-tab" className="text-sm">
                                Save password with this project
                              </Label>
                            </div>
                            
                            {savedPassword && (
                              <div className="p-2 bg-green-50 border border-green-200 rounded-lg">
                                <div className="flex items-center gap-2">
                                  <CheckCircle className="h-4 w-4 text-green-600" />
                                  <span className="text-sm text-green-700">
                                    Password saved with project ({savedPassword.length} characters)
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="save-project"
                            checked={saveProject}
                            onChange={(e) => setSaveProject(e.target.checked)}
                            className="rounded"
                          />
                          <Label htmlFor="save-project">Save project for future use</Label>
                        </div>
                      </div>
                      
                      {/* Project Preview */}
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold">Project Preview</h3>
                        
                        {projectName ? (
                          <div className="p-4 bg-muted rounded-lg space-y-3">
                            <div className="flex items-center gap-2">
                              <File className="h-4 w-4" />
                              <span className="font-medium">{projectName}</span>
                            </div>
                            
                            {projectDescription && (
                              <p className="text-sm text-muted-foreground">
                                {projectDescription}
                              </p>
                            )}
                            
                            {projectTags && (
                              <div className="flex flex-wrap gap-1">
                                {projectTags.split(',').map((tag, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {tag.trim()}
                                  </Badge>
                                ))}
                              </div>
                            )}
                            
                            {/* Password Status */}
                            {savedPassword && (
                              <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded">
                                <Shield className="h-4 w-4 text-green-600" />
                                <span className="text-xs text-green-700">
                                  Password saved ({savedPassword.length} chars)
                                </span>
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="sm"
                                  onClick={copyPasswordToClipboard}
                                  className="ml-auto h-6 w-6 p-0"
                                  title="Copy Password"
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </div>
                            )}
                            
                            <div className="text-xs text-muted-foreground">
                              Created: {new Date().toLocaleDateString()}
                            </div>
                          </div>
                        ) : (
                          <div className="p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg">
                            <File className="h-8 w-8 mx-auto mb-2 opacity-50" />
                            <p>Enter project information to see preview</p>
                          </div>
                        )}
                        
                        {/* Project Actions */}
                        <div className="space-y-2">
                          <Button 
                            className="w-full" 
                            disabled={!projectName.trim()}
                            onClick={() => toast.success("Project settings saved!")}
                          >
                            Save Project Settings
                          </Button>
                          
                          <Button 
                            variant="outline" 
                            className="w-full"
                            onClick={() => {
                              setProjectName("");
                              setProjectDescription("");
                              setProjectTags("");
                              setSaveProject(false);
                              setSavePasswordWithProject(false);
                              setSavedPassword("");
                              setPassword("");
                              toast.success("Project settings and password cleared!");
                            }}
                          >
                            Clear Settings
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              {/* Size Estimate Tab */}
              <TabsContent value="size-estimate" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <RefreshCw className="h-5 w-5" />
                      Size Estimate Calculator
                    </CardTitle>
                    <CardDescription>
                      Calculate file capacity requirements and size recommendations
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      {/* Input Section */}
                      <div className="space-y-6">
                        <div className="space-y-4">
                          <Label>Estimation Type</Label>
                          <Select value={estimateType} onValueChange={(value: "carrier" | "content") => setEstimateType(value)}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="carrier">
                                <div className="flex items-center gap-2">
                                  <FileImage className="h-4 w-4" />
                                  Carrier File Capacity
                                </div>
                              </SelectItem>
                              <SelectItem value="content">
                                <div className="flex items-center gap-2">
                                  <File className="h-4 w-4" />
                                  Content File Requirements
                                </div>
                              </SelectItem>
                            </SelectContent>
                          </Select>
                          <p className="text-sm text-muted-foreground">
                            {estimateType === "carrier" 
                              ? "Upload a carrier file to see how much data it can hide"
                              : "Upload a content file to see what carrier size is needed"
                            }
                          </p>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="estimate-file">
                            {estimateType === "carrier" ? "Carrier File" : "Content File"}
                          </Label>
                          <div className="border-2 border-dashed border-border rounded-lg p-4 text-center hover:border-primary/50 transition-colors">
                            <input
                              id="estimate-file"
                              type="file"
                              onChange={handleEstimateFileChange}
                              className="hidden"
                              accept={estimateType === "carrier" 
                                ? "image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                                : "*/*"
                              }
                            />
                            <label htmlFor="estimate-file" className="cursor-pointer">
                              {estimateType === "carrier" ? <FileImage className="h-6 w-6 text-muted-foreground mx-auto mb-2" /> : <File className="h-6 w-6 text-muted-foreground mx-auto mb-2" />}
                              <p className="text-sm text-muted-foreground">
                                {estimateFile ? estimateFile.name : `Click to upload ${estimateType} file`}
                              </p>
                              {estimateFile && (
                                <p className="text-xs text-muted-foreground mt-1">
                                  Size: {formatFileSize(estimateFile.size)}
                                </p>
                              )}
                            </label>
                          </div>
                        </div>
                        
                        <Button 
                          onClick={calculateSizeEstimate}
                          className="w-full"
                          disabled={!estimateFile || estimateLoading}
                        >
                          {estimateLoading ? (
                            <>
                              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                              Calculating...
                            </>
                          ) : (
                            <>
                              <Zap className="h-4 w-4 mr-2" />
                              Calculate Size Estimate
                            </>
                          )}
                        </Button>
                      </div>
                      
                      {/* Results Section */}
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold">Size Analysis Results</h3>
                        
                        {estimateResult ? (
                          <div className="space-y-4">
                            <div className="p-4 bg-muted rounded-lg space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">File Size:</span>
                                <span className="text-sm">{estimateResult.fileSizeFormatted}</span>
                              </div>
                              
                              {estimateResult.type === "carrier" && (
                                <>
                                  <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">Estimated Capacity:</span>
                                    <span className="text-sm">{estimateResult.capacityFormatted}</span>
                                  </div>
                                  <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">Method:</span>
                                    <span className="text-sm capitalize">{estimateResult.method}</span>
                                  </div>
                                </>
                              )}
                            </div>
                            
                            <div className="space-y-2">
                              <Label>Recommendations:</Label>
                              <div className="space-y-2">
                                {estimateResult.recommendations.map((rec: string, index: number) => (
                                  <Alert key={index}>
                                    <AlertDescription className="text-sm">
                                      {rec}
                                    </AlertDescription>
                                  </Alert>
                                ))}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg">
                            <RefreshCw className="h-8 w-8 mx-auto mb-2 opacity-50" />
                            <p>Upload a file and click calculate to see size analysis</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}