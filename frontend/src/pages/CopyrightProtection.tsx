import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import {
  Shield, 
  Copyright, 
  FileImage, 
  Lock, 
  Eye, 
  Users, 
  BarChart3, 
  Settings,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertTriangle
} from "lucide-react";

export default function CopyrightProtection() {
  const navigate = useNavigate();


  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
    
    // Check authentication
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) {
        navigate("/auth");
      }
    });
  }, [navigate]);

  const features = [
    {
      icon: <Copyright className="h-6 w-6 text-primary" />,
      title: "IP Watermarking",
      description: "Embed invisible copyright information directly into your creative works"
    },
    {
      icon: <Shield className="h-6 w-6 text-primary" />,
      title: "Ownership Proof",
      description: "Generate integrity-verified certificates of ownership and creation timestamps"
    }
  ];

  const useCases = [
    {
      title: "Digital Art Protection",
      description: "Protect paintings, illustrations, and digital artwork from unauthorized use",
      icon: <FileImage className="h-8 w-8 text-primary" />
    },
    {
      title: "Photography Rights",
      description: "Secure your photographs with invisible watermarks and protection monitoring",
      icon: <Eye className="h-8 w-8 text-primary" />
    },
    {
      title: "Brand Asset Security",
      description: "Protect logos, marketing materials, and brand assets from misuse",
      icon: <Shield className="h-8 w-8 text-primary" />
    }
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-20">
        {/* Header Section */}
        <section className="py-12 bg-gradient-to-r from-primary/5 to-sea-light/10 dark:from-primary/10 dark:to-background">
          <div className="container">
            <div className="animate-fade-in">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mr-6">
                    <Shield className="h-8 w-8 text-primary" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold mb-2">Copyright Protection</h1>
                    <p className="text-xl text-muted-foreground">
                      Advanced intellectual property protection for creative industries
                    </p>
                  </div>
                </div>
                <Button onClick={() => navigate('/general')} variant="outline">
                  <Shield className="mr-2 h-4 w-4" />
                  New Project
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-4 mb-8">
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Copyright className="h-3 w-3" />
                  IP Watermarking
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Lock className="h-3 w-3" />
                  Legal Compliance
                </Badge>
              </div>

            </div>
          </div>
        </section>

        {/* Embed/Extract/Project Settings Section - Placeholder */}
        <section className="py-16 bg-card">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-8 animate-fade-in">
              <h2 className="text-3xl font-bold mb-4">Copyright Protection Tools</h2>
              <p className="text-muted-foreground">
                Embed, extract, and manage your intellectual property protection
              </p>
            </div>
            
            {/* Space reserved for embed/extract/project settings functionality */}
            <div className="min-h-[400px] rounded-lg border-2 border-dashed border-primary/30 bg-primary/5 flex items-center justify-center">
              <p className="text-muted-foreground text-lg">Embed/Extract/Project Settings Section</p>
            </div>
          </div>
        </section>

        {/* Features Overview */}
        <section className="py-16">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold mb-4">Comprehensive IP Protection</h2>
              <p className="text-muted-foreground">
                Protect your creative works with advanced steganography designed specifically for intellectual property rights
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {features.map((feature, index) => (
                <Card key={index} className={`animate-fade-in hover:shadow-lg transition-all duration-300`} style={{ animationDelay: `${index * 100}ms` }}>
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                        {feature.icon}
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                        <p className="text-muted-foreground">{feature.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="py-16 bg-card">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold mb-4">Industry Applications</h2>
              <p className="text-muted-foreground">
                Tailored solutions for different creative industries and copyright protection needs
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {useCases.map((useCase, index) => (
                <Card key={index} className={`animate-fade-in text-center hover:shadow-lg transition-all duration-300`} style={{ animationDelay: `${index * 100}ms` }}>
                  <CardContent className="p-6">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      {useCase.icon}
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{useCase.title}</h3>
                    <p className="text-sm text-muted-foreground">{useCase.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Workflow Preview */}
        <section className="py-16">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold mb-4">Protection Workflow</h2>
              <p className="text-muted-foreground">
                How VeilForge's copyright protection will secure your intellectual property
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center animate-fade-in">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-primary">1</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">Upload & Register</h3>
                <p className="text-muted-foreground">
                  Upload your creative work and register copyright information with timestamped proof of creation
                </p>
              </div>
              
              <div className="text-center animate-fade-in [animation-delay:200ms]">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-primary">2</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">Embed & Protect</h3>
                <p className="text-muted-foreground">
                  Apply invisible watermarks and embed ownership data using advanced steganography techniques
                </p>
              </div>
              
              <div className="text-center animate-fade-in [animation-delay:400ms]">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-primary">3</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">Verify</h3>
                <p className="text-muted-foreground">
                  Verify copyright embeddings with proper password to confirm ownership and authenticity
                </p>
              </div>
            </div>
          </div>
        </section>

      </main>
      
      <Footer />
    </div>
  );
}