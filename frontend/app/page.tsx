"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadZone } from "@/components/upload-zone";
import { ResultCard } from "@/components/result-card";
import { PredictionHistory } from "@/components/history";
import { PredictionResponse } from "@/types";
import { Satellite, ShieldCheck, Zap, Layers, Activity, Sun, Moon } from "lucide-react";

const SUPPORTED_CLASSES = [
  { id: "AnnualCrop", es: "Cultivo Anual", desc: "Tierras aradas cultivadas periódicamente." },
  { id: "Forest", es: "Bosque", desc: "Zonas con alta densidad de árboles." },
  { id: "HerbaceousVegetation", es: "Vegetación Herbácea", desc: "Pastizales naturales y vegetación no leñosa." },
  { id: "Highway", es: "Carretera / Autopista", desc: "Caminos pavimentados e infraestructura." },
  { id: "Industrial", es: "Área Industrial", desc: "Fábricas y almacenes comerciales." },
  { id: "Pasture", es: "Pastizal", desc: "Terrenos cubiertos de hierba para pastoreo." },
  { id: "PermanentCrop", es: "Cultivo Permanente", desc: "Viñedos y plantaciones de ciclo largo." },
  { id: "Residential", es: "Área Residencial", desc: "Zonas urbanas y viviendas." },
  { id: "River", es: "Río", desc: "Cuerpos de agua corriente naturales." },
  { id: "SeaLake", es: "Mar o Lago", desc: "Grandes masas de agua estancada." }
];

export default function Home() {
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [history, setHistory] = useState<PredictionResponse[]>([]);
  const [serverStatus, setServerStatus] = useState<"checking" | "online" | "offline">("checking");
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Sync theme state with document class
    const isDark = document.documentElement.classList.contains("dark");
    setTheme(isDark ? "dark" : "light");

    const saved = localStorage.getItem("prediction-history");
    if (saved) setHistory(JSON.parse(saved));

    const checkHealth = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
        const res = await fetch(`${apiUrl}/health`);
        if (res.ok) {
          setServerStatus("online");
        } else {
          setServerStatus("offline");
        }
      } catch {
        setServerStatus("offline");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.classList.remove("light", "dark");
    document.documentElement.classList.add(newTheme);
  };

  const handleNewPrediction = (res: PredictionResponse) => {
    setPrediction(res);
    const newHistory = [res, ...history].slice(0, 10);
    setHistory(newHistory);
    localStorage.setItem("prediction-history", JSON.stringify(newHistory));
  };

  return (
    <div className="space-y-8 md:space-y-12 pb-12">
      {/* Top Navbar */}
      <nav className="flex flex-col sm:flex-row items-center justify-between py-4 sm:py-6 border-b border-border gap-4">
        <div className="flex items-center space-x-3 group cursor-default">
          <div className="p-2.5 rounded-2xl bg-primary/10 border border-primary/20">
            <Satellite className="w-6 h-6 text-primary" />
          </div>
          <div>
            <span className="font-bold tracking-tight text-foreground block text-xl sm:text-2xl">EUROSAT<span className="text-primary">AI</span></span>
            <span className="text-[10px] text-muted-foreground block uppercase tracking-[0.2em] font-bold">Satellite Analytics</span>
          </div>
        </div>

        <div className="flex items-center gap-3 sm:gap-4">
          {/* Theme Toggle */}
          <button 
            onClick={toggleTheme}
            className="p-2.5 rounded-2xl bg-secondary hover:bg-secondary/80 border border-border transition-all active:scale-95"
            aria-label="Toggle theme"
          >
            {theme === "light" ? <Moon className="w-5 h-5 text-slate-700" /> : <Sun className="w-5 h-5 text-yellow-400" />}
          </button>

          {/* Server status indicator */}
          <div className="flex items-center space-x-3 text-xs bg-secondary border border-border rounded-full px-4 sm:px-5 py-2">
            <span className="text-muted-foreground hidden xs:block">Estado:</span>
            {serverStatus === "checking" ? (
              <span className="flex items-center gap-2 text-muted-foreground">
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
                <span className="font-semibold">Verificando</span>
              </span>
            ) : serverStatus === "online" ? (
              <span className="flex items-center gap-2 text-green-600 dark:text-green-400 font-bold">
                <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)] animate-pulse" />
                <span>En línea</span>
              </span>
            ) : (
              <span className="flex items-center gap-2 text-red-500 font-bold">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span>Offline</span>
              </span>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="text-center max-w-4xl mx-auto space-y-4 pt-6 md:pt-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight mb-4 leading-tight">
            <span className="text-foreground">Análisis de Suelos</span>
            <br />
            <span className="gradient-text">por Satélite</span>
          </h1>
          <p className="text-muted-foreground text-base sm:text-lg md:text-xl leading-relaxed max-w-2xl mx-auto px-4">
            Plataforma profesional para la identificación de coberturas terrestres utilizando <span className="text-foreground font-semibold">Inteligencia Artificial</span> de última generación.
          </p>
        </motion.div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-10 items-start">
        {/* Left Side: Upload & Results */}
        <div className="lg:col-span-7 xl:col-span-8 space-y-8 sm:space-y-10">
          <UploadZone onUploadSuccess={handleNewPrediction} />
          
          <AnimatePresence mode="wait">
            {prediction && (
              <motion.div
                key={prediction.inference_time + prediction.class}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.4 }}
              >
                <ResultCard result={prediction} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Side: History & Guide */}
        <div className="lg:col-span-5 xl:col-span-4 space-y-6 sm:space-y-8">
          <PredictionHistory history={history} />

          {/* Supported Classes Guide */}
          <div className="glass rounded-[2rem] p-6 sm:p-8 space-y-6">
            <div className="flex items-center space-x-3 border-b border-border pb-4">
              <div className="p-2 rounded-xl bg-primary/10">
                <Layers className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-bold text-sm uppercase tracking-widest text-muted-foreground">Coberturas</h3>
            </div>
            
            <div className="space-y-2.5 max-h-[400px] overflow-y-auto custom-scrollbar pr-3">
              {SUPPORTED_CLASSES.map((cls) => (
                <div key={cls.id} className="p-4 rounded-2xl hover:bg-secondary/50 transition-colors border border-transparent hover:border-border group">
                  <div className="font-bold text-foreground mb-1 flex justify-between items-center">
                    {cls.es}
                    <div className="w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <div className="text-muted-foreground text-xs leading-relaxed">{cls.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modern Footer */}
      <footer className="py-12 border-t border-border mt-8">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 text-center sm:text-left">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4">
            <div className="p-3 rounded-2xl bg-secondary">
              <Zap className="w-5 h-5 text-primary" />
            </div>
            <div className="space-y-1">
              <span className="block text-xs font-black uppercase tracking-widest text-muted-foreground">Velocidad</span>
              <p className="text-[11px] text-muted-foreground font-medium">Inferencia en tiempo real optimizada.</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4">
            <div className="p-3 rounded-2xl bg-secondary">
              <ShieldCheck className="w-5 h-5 text-primary" />
            </div>
            <div className="space-y-1">
              <span className="block text-xs font-black uppercase tracking-widest text-muted-foreground">Modelo</span>
              <p className="text-[11px] text-muted-foreground font-medium">Arquitectura EfficientNetB0 (SOTA).</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4">
            <div className="p-3 rounded-2xl bg-secondary">
              <Activity className="w-5 h-5 text-primary" />
            </div>
            <div className="space-y-1">
              <span className="block text-xs font-black uppercase tracking-widest text-muted-foreground">Institución</span>
              <p className="text-[11px] text-muted-foreground font-medium">UNA Puno - Ingeniería de Sistemas.</p>
            </div>
          </div>
        </div>
        <div className="mt-12 text-center text-[10px] text-muted-foreground uppercase tracking-[0.3em] font-bold opacity-50">
          © 2026 EuroSAT Satellite Intelligence Systems
        </div>
      </footer>
    </div>
  );
}
