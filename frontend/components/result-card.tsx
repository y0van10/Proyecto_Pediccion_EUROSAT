import { PredictionResponse } from "@/types";
import { CheckCircle2, Timer, BarChart3, Database } from "lucide-react";

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
  SeaLake: "Mar o Lago",
  Buildings: "Edificaciones / Construcciones",
  Glacier: "Glaciar",
  Mountain: "Montaña",
  Sea: "Mar / Océano Terrestre",
  Street: "Calle / Vía Terrestre"
};

export function ResultCard({ result }: { result: PredictionResponse }) {
  const spanishClass = CLASS_TRANSLATIONS[result.class] || result.class;
  const isSatellite = result.domain === "satellite";

  return (
    <div className="glass rounded-3xl p-6 md:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="text-xl md:text-2xl font-bold flex items-center gap-2 text-white">
          <CheckCircle2 className="text-blue-400 w-6 h-6 shrink-0" />
          Resultado del Análisis
        </h2>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {result.domain && (
            <span className="px-3 py-1 rounded-full bg-white/5 text-gray-300 text-xs font-semibold border border-white/10 tracking-wide">
              {isSatellite ? "Satelital" : "Terrestre"}
            </span>
          )}
          <span className="px-4.5 py-1.5 rounded-full bg-blue-500/10 text-blue-400 text-sm font-semibold border border-blue-500/25 tracking-wide">
            Confianza: {result.probability}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {/* Prediccion */}
        <div className="p-4.5 rounded-2xl bg-white/5 border border-white/10 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase tracking-wider font-semibold mb-2">
            <BarChart3 className="w-3.5 h-3.5" /> Predicción
          </div>
          <div>
            <div className="text-lg font-bold text-white tracking-wide">
              {spanishClass}
            </div>
            <div className="text-[10px] font-mono text-gray-500 uppercase mt-0.5">
              ID: {result.class}
            </div>
          </div>
        </div>

        {/* Latencia */}
        <div className="p-4.5 rounded-2xl bg-white/5 border border-white/10 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase tracking-wider font-semibold mb-2">
            <Timer className="w-3.5 h-3.5" /> Latencia de Red
          </div>
          <div>
            <div className="text-lg font-bold text-white">
              {result.inference_time} segundos
            </div>
            <div className="text-[10px] font-mono text-gray-500 uppercase mt-0.5">
              Inferencia API
            </div>
          </div>
        </div>

        {/* Archivo origen */}
        <div className="p-4.5 rounded-2xl bg-white/5 border border-white/10 flex flex-col justify-between sm:col-span-2 md:col-span-1">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase tracking-wider font-semibold mb-2">
            <Database className="w-3.5 h-3.5" /> Origen de Datos
          </div>
          <div>
            <div className="text-sm font-bold text-white truncate max-w-[220px]">
              {result.filename}
            </div>
            <div className="text-[10px] font-mono text-gray-500 uppercase mt-0.5">
              Archivo Subido
            </div>
          </div>
        </div>
      </div>

      {/* Top-5 probability breakdown progress bars */}
      {result.top_5 && result.top_5.length > 0 && (
        <div className="border-t border-white/5 pt-6 space-y-4">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            Distribución de Probabilidades (Top-5)
          </h3>
          <div className="space-y-3.5">
            {result.top_5.map((item, idx) => {
              const itemClassSpanish = CLASS_TRANSLATIONS[item.class] || item.class;
              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-300 font-medium">{itemClassSpanish}</span>
                    <span className="text-gray-400 font-mono">{item.probability}%</span>
                  </div>
                  <div className="relative h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="absolute top-0 left-0 h-full bg-blue-500/80 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${item.probability}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
