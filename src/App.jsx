import React, { useState, useEffect } from 'react';
import EcgSlider from './EcgSlider';
import Ecg3DSpace from './Ecg3DSpace';

export default function App() {
  const [timelineStep, setTimelineStep] = useState(0);
  const [ecgData, setEcgData] = useState([]);

  // Stream local structural JSON coordinates on load
  useEffect(() => {
    fetch('/ecg_data.json')
      .then(response => response.json())
      .then(data => {
        setEcgData(data);
        setTimelineStep(Math.floor(data.length / 4)); // Initialize starter point
      })
      .catch(err => console.error("Error streaming local JSON data channel:", err));
  }, []);

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-white p-6">
      <div className="w-full max-w-6xl bg-white rounded-[32px] p-12 flex gap-8 presentation-halo">
        
        {/* LEFT COLUMN: Control Deck Panel */}
        <div className="w-1/4 flex flex-col justify-between">
          <div>
            <h3 className="text-2xl font-bold text-slate-800 leading-tight">3D ECG Waveform</h3>
            <span className="text-sm font-medium text-slate-400 block mt-1">Visualization Panel</span>

            <div className="mt-8">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2">File Input</label>
              <div className="bg-slate-50 text-slate-700 text-xs font-mono p-3 rounded-lg border border-slate-100">
                public/ecg_data.json
              </div>
            </div>
            
            {/* DATA COORDINATE TRACKER CARD */}
            <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-100 text-xs space-y-2">
              <div className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Data Coordinate Tracker</div>
              {ecgData.length > 0 ? (
                <div className="font-mono text-slate-600 space-y-1">
                  <div>Index Frame: <span className="text-slate-800 font-bold">{timelineStep}</span></div>
                  <div>X State (τ₀): <span className="text-blue-600">{ecgData[timelineStep].x.toFixed(4)}</span></div>
                  <div>Y State (▼): <span className="text-green-600">{ecgData[timelineStep].y.toFixed(4)}</span></div>
                  <div>Z State (▲): <span className="text-purple-600">{ecgData[timelineStep].z.toFixed(4)}</span></div>
                </div>
              ) : (
                <div className="text-slate-400">Syncing data stream tracks...</div>
              )}
            </div>

            {/* PLACEMENT ZONE: PHASIC REGION LEGEND CARD */}
            <div className="mt-4 bg-slate-50 border border-slate-100 rounded-xl p-4 text-xs space-y-3">
              <div className="font-bold text-slate-500 uppercase tracking-wider text-[10px] mb-1">
                Phasic Region Legend
              </div>
              
              <div className="space-y-2.5">
                {/* QRS Complex */}
                <div className="flex items-center gap-2.5">
                  <div className="w-3 h-3 rounded-full bg-[#4361ee] shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 leading-none">QRS Complex</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">Ventricular Contraction</p>
                  </div>
                </div>

                {/* T Wave */}
                <div className="flex items-center gap-2.5">
                  <div className="w-3 h-3 rounded-full bg-[#b7094c] shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 leading-none">T Wave</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">Ventricular Repolarization</p>
                  </div>
                </div>

                {/* P Wave */}
                <div className="flex items-center gap-2.5">
                  <div className="w-3 h-3 rounded-full bg-[#f77f00] shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 leading-none">P Wave</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">Atrial Depolarization</p>
                  </div>
                </div>

                {/* Baseline */}
                <div className="flex items-center gap-2.5">
                  <div className="w-3 h-3 rounded-full bg-[#a7c957] shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 leading-none">Isoelectric Baseline</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">Resting / Diastolic Phase</p>
                  </div>
                </div>
              </div>
            </div>

          </div>
          
          <div className="text-[11px] font-mono text-slate-400 pt-4">Client-Side GPU Rendering Core v1.0</div>
        </div>

        {/* MID SEPARATION DIVIDER */}
        <div className="w-[1px] bg-slate-100 self-stretch min-h-[500px]"></div>

        {/* RIGHT COLUMN: Active Graphical Viewports */}
        <div className="w-3/4 flex flex-col justify-between gap-6">
          
          {/* TOP CANVAS: Hardware-Accelerated WebGL 3D Attractor Box */}
          <div className="flex-1 w-full bg-slate-50/50 rounded-2xl border border-slate-100 overflow-hidden relative min-h-[400px] flex items-center justify-center">
            {ecgData.length > 0 ? (
              <Ecg3DSpace data={ecgData} currentStep={timelineStep} />
            ) : (
              <div className="text-sm font-medium text-slate-400 animate-pulse">Initializing WebGL Engine instances...</div>
            )}
          </div>

          {/* BOTTOM CANVAS: Live Interactive D3.js Waveform Scrubber Slider */}
          <div className="h-32 w-full bg-slate-50/30 rounded-2xl border border-slate-100 p-4 overflow-hidden relative">
            {ecgData.length > 0 && (
              <EcgSlider data={ecgData} currentStep={timelineStep} onStepChange={setTimelineStep} />
            )}
          </div>

        </div>

      </div>
    </div>
  );
}