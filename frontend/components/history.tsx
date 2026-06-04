import { PredictionResponse } from "@/types";
import { History as HistoryIcon, Trash2, Clock } from "lucide-react";

const CLASS_COLORS: Record<string, string> = {
  AnnualCrop: "text-emerald-600 dark:text-emerald-400",
  Forest: "text-green-600 dark:text-green-400",
  HerbaceousVegetation: "text-lime-600 dark:text-lime-400",
  Highway: "text-slate-600 dark:text-slate-400",
  Industrial: "text-orange-600 dark:text-orange-400",
  Pasture: "text-yellow-600 dark:text-yellow-400",
  PermanentCrop: "text-emerald-700 dark:text-emerald-500",
  Residential: "text-rose-600 dark:text-rose-400",
  River: "text-cyan-600 dark:text-cyan-400",
  SeaLake: "text-blue-600 dark:text-blue-400"
};

const CLASS_TRANSLATIONS: Record<string, string> = {
  AnnualCrop: "Cultivo Anual",
  Forest: "Bosque",
  HerbaceousVegetation: "Vegetación Herbácea",
  Highway: "Carretera / Autopista",
  Industrial: "Área Industrial",
  Pasture: "Pastizal",
  PermanentCrop: "Cultivo Permanente",
  Residential: "Área Residencial",
  River: "Río",
  SeaLake: "Mar o Lago"
};

export function PredictionHistory({ history }: { history: PredictionResponse[] }) {
  const clearHistory = () => {
    localStorage.removeItem("prediction-history");
    window.location.reload();
  };

  return (
    <div className="glass rounded-[2rem] p-6 sm:p-8 h-full flex flex-col">
      <div className="flex items-center justify-between mb-8 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-primary/10">
            <HistoryIcon className="w-5 h-5 text-primary" />
          </div>
          <h3 className="font-black text-xs uppercase tracking-[0.2em] text-muted-foreground">Historial</h3>
        </div>
        {history.length > 0 && (
          <button 
            onClick={clearHistory}
            className="p-2 rounded-xl text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all active:scale-95"
            title="Borrar historial"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="space-y-4 flex-1 overflow-y-auto max-h-[450px] pr-2 custom-scrollbar">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center opacity-40">
            <div className="w-16 h-16 rounded-3xl bg-secondary flex items-center justify-center mb-4">
              <Clock className="w-8 h-8 text-muted-foreground" />
            </div>
            <p className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Vacío</p>
          </div>
        ) : (
          history.map((item, index) => {
            const spanishClass = CLASS_TRANSLATIONS[item.class] || item.class;
            const colorClass = CLASS_COLORS[item.class] || "text-primary";
            
            return (
              <div 
                key={index}
                className="group p-4 sm:p-5 rounded-2xl bg-secondary/30 border border-border hover:border-primary/20 hover:bg-secondary/60 transition-all cursor-default"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`font-black text-sm tracking-tight ${colorClass}`}>
                    {spanishClass}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-muted-foreground bg-background px-2 py-0.5 rounded-md border border-border/50">
                      {item.inference_time}s
                    </span>
                  </div>
                </div>
                
                <div className="text-[11px] text-muted-foreground truncate mb-3 font-medium opacity-70 group-hover:opacity-100 transition-opacity">
                  {item.filename}
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t border-border/50">
                  <span className="text-[9px] uppercase tracking-widest text-muted-foreground font-black">Confianza</span>
                  <span className="text-xs font-black text-foreground">{item.probability}%</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
