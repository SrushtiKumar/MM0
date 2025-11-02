import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Shield, FileCheck, Lock } from "lucide-react";

import { supabase } from "@/integrations/supabase/client";

const ForensicEvidence = () => {
  const navigate = useNavigate();


  useEffect(() => {
    // Check authentication
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) {
        navigate("/auth");
      }
    });
  }, [navigate]);
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <div className="flex-1"></div>
              <div className="flex-1 flex justify-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10">
                  <Shield className="w-10 h-10 text-primary" />
                </div>
              </div>
              <div className="flex-1 flex justify-end">
                <Button onClick={() => navigate('/general')} variant="outline">
                  <Lock className="mr-2 h-4 w-4" />
                  New Project
                </Button>
              </div>
            </div>
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              Forensic Evidence Chain Protection
            </h1>
            <p className="text-xl text-muted-foreground">
              Maintain integrity and authenticity of digital evidence
            </p>
          </div>

          {/* Embed/Extract/Project Settings Section - Placeholder */}
          <div className="mb-12">
            <div className="text-center mb-8 animate-fade-in">
              <h2 className="text-3xl font-bold mb-4">Forensic Evidence Tools</h2>
              <p className="text-muted-foreground">
                Embed, extract, and manage your forensic evidence protection
              </p>
            </div>
            
            {/* Space reserved for embed/extract/project settings functionality */}
            <div className="min-h-[400px] rounded-lg border-2 border-dashed border-primary/30 bg-primary/5 flex items-center justify-center">
              <p className="text-muted-foreground text-lg">Embed/Extract/Project Settings Section</p>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <div className="p-6 rounded-lg border bg-card hover-scale transition-all">
              <FileCheck className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Evidence Integrity</h3>
              <p className="text-muted-foreground">
                Ensure digital evidence remains tamper-proof throughout legal proceedings
              </p>
            </div>

            <div className="p-6 rounded-lg border bg-card hover-scale transition-all">
              <Lock className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Secure Evidence</h3>
              <p className="text-muted-foreground">
                Maintain a verifiable record of all interactions with forensic evidence
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default ForensicEvidence;
