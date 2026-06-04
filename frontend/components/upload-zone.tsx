"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileImage, Loader2, Info } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { PredictionResponse } from "@/types";

interface UploadZoneProps {
  onUploadSuccess: (res: PredictionResponse) => void;
}

export function UploadZone({ onUploadSuccess }: UploadZoneProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setPreview(URL.createObjectURL(file));
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await axios.post(`${apiUrl}/predict`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      onUploadSuccess(response.data);
      toast.success("Imagen analizada con éxito");
    } catch (error) {
      console.error(error);
      toast.error("Error al procesar la imagen");
    } finally {
      setIsUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpeg", ".jpg", ".png", ".tif"] },
    multiple: false
  });

  return (
    <div className="space-y-4">
      <div 
        {...getRootProps()} 
        className={`
          relative overflow-hidden rounded-[2.5rem] border-2 border-dashed transition-all duration-500 cursor-pointer
          ${isDragActive ? "border-primary bg-primary/5 shadow-2xl" : "border-border hover:border-primary/50 bg-secondary/30 hover:bg-secondary/50"}
          h-[350px] sm:h-[400px] flex flex-col items-center justify-center text-center p-8 group
        `}
      >
        <input {...getInputProps()} />
        
        {preview ? (
          <div className="absolute inset-0 z-0 overflow-hidden">
            <img src={preview} alt="Preview" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
            <div className="absolute inset-0 bg-background/40 backdrop-blur-[2px]" />
            {isUploading && <div className="scan-line" />}
          </div>
        ) : (
          <div className="absolute inset-0 z-0 opacity-5 bg-gradient-to-br from-primary to-purple-500" />
        )}

        <div className="relative z-10 flex flex-col items-center">
          {isUploading ? (
            <div className="relative">
              <Loader2 className="w-16 h-16 text-primary animate-spin mb-6" />
              <div className="absolute inset-0 blur-xl bg-primary/20 animate-pulse" />
            </div>
          ) : (
            <div className="w-20 h-20 rounded-3xl bg-background/80 border border-border flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-xl transition-all duration-300">
              <Upload className="w-10 h-10 text-primary" />
            </div>
          )}
          
          <h3 className="text-2xl sm:text-3xl font-black mb-3 tracking-tight text-foreground">
            {isUploading ? "Analizando Imagen..." : "Subir Vista Satelital"}
          </h3>
          <p className="text-muted-foreground text-sm sm:text-base max-w-[320px] leading-relaxed font-medium">
            {isDragActive 
              ? "Suelte la imagen para comenzar" 
              : "Arrastre su imagen aquí o haga clic para seleccionar un archivo."}
          </p>

          {!isUploading && (
            <div className="mt-8 flex items-center gap-2 px-6 py-2 rounded-full bg-background/50 border border-border text-[10px] uppercase tracking-widest text-muted-foreground font-black group-hover:border-primary/30 transition-all">
              PNG • JPG • TIF
            </div>
          )}
        </div>
      </div>
      
      <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 p-3 rounded-xl border border-border">
        <Info className="w-4 h-4 text-primary shrink-0" />
        Para mejores resultados, use imágenes centradas de 64x64 a 256x256 píxeles.
      </div>
    </div>
  );
}
