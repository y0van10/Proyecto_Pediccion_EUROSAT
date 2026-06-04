export interface PredictionResponse {
  class: string;
  probability: number;
  inference_time: number;
  filename: string;
  domain?: string;
  top_5?: Array<{ class: string; probability: number }>;
}

export type EuroSATClass = 
  | 'AnnualCrop' 
  | 'Forest' 
  | 'HerbaceousVegetation' 
  | 'Highway' 
  | 'Industrial' 
  | 'Pasture' 
  | 'PermanentCrop' 
  | 'Residential' 
  | 'River' 
  | 'SeaLake';
