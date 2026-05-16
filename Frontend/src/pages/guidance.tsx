import { useState, useEffect } from "react";
import '../index.css'

type LEDDisplay = {
  arrow: string;
  color: string;
  message: string;
  available: number;
  capacity: number;
};

type LEDBoard = {
  ledID: string;
  location: string;
  x: number;
  y: number;
  status: string;
  displays: LEDDisplay[];
};

export default function Guidance() {
  const [boards, setBoards] = useState<LEDBoard[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const fetchGuidanceData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/guidance/status");
      const data = await res.json();
      if (data.led_boards) {
        setBoards(data.led_boards);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (err) {
      console.error("Failed to fetch guidance data:", err);
    }
  };

  useEffect(() => {
    fetchGuidanceData();
    const interval = setInterval(fetchGuidanceData, 3000);
    return () => clearInterval(interval);
  }, []);

  const getColorStyles = (color: string) => {
    switch (color) {
      case "GREEN":
        return "text-green-500 drop-shadow-[0_0_8px_rgba(34,197,94,1)]";
      case "YELLOW":
        return "text-yellow-400 drop-shadow-[0_0_8px_rgba(250,204,21,1)]";
      case "RED":
        return "text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,1)]";
      default:
        return "text-gray-600";
    }
  };

  const renderArrow = (direction: string, colorClass: string) => {
    const baseClasses = `w-6 h-6 ${colorClass}`;
    switch (direction) {
      case "LEFT":
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        );
      case "RIGHT":
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        );
      default:
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 md:p-8 font-sans flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-end border-b border-gray-800 pb-4 mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">Bản Đồ Điều Hướng Bãi Đỗ Xe</h1>
          <p className="text-gray-400 mt-1">2D Spatial Monitoring - Live</p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2 justify-end mb-1">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
            </span>
            <span className="text-sm font-medium text-blue-400 uppercase tracking-wider">Hệ Thống Đang Chạy</span>
          </div>
          <p className="text-xs text-gray-500 font-mono">Đồng bộ: {lastUpdated || "--:--:--"}</p>
        </div>
      </div>

      {/* 2D Map Canvas Container */}
      <div className="flex-grow relative w-full rounded-xl overflow-hidden border-4 border-gray-800 shadow-2xl bg-gray-900">
        
        {/* MAP BACKGROUND IMAGE */}
        <div 
          className="absolute inset-0 opacity-40 mix-blend-luminosity"
          style={{
            backgroundImage: "url('images/parking_map.png')",
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></div>

        {/* Grid Overlay to look technical */}
        <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>

        {/* RENDER LED BOARD MARKERS */}
        {boards.map((board) => (
          <div 
            key={board.ledID} 
            className="absolute flex flex-col items-center group transition-transform duration-300 hover:scale-110 hover:z-50"
            // We use transform -translate-x-1/2 -translate-y-full so the "pole" points exactly at the X,Y coordinate
            style={{ left: `${board.x}%`, top: `${board.y}%`, transform: 'translate(-50%, -100%)' }}
          >
            
            {/* The physical LED screen box */}
            <div className="bg-black p-1.5 rounded border-2 border-gray-700 shadow-[0_0_20px_rgba(0,0,0,0.9)] flex items-center gap-2">
              {board.displays.map((display, index) => (
                <div key={index} className="flex flex-col items-center justify-center min-w-[30px]">
                  {renderArrow(display.arrow, getColorStyles(display.color))}
                  <span className={`text-[10px] font-mono font-bold mt-1 ${getColorStyles(display.color)}`}>
                    {display.available}
                  </span>
                </div>
              ))}
            </div>

            {/* The Signpost pole */}
            <div className="w-1.5 h-8 bg-gradient-to-b from-gray-600 to-gray-800 shadow-md"></div>
            
            {/* The Base/Dot on the ground */}
            <div className="w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow-[0_0_15px_rgba(59,130,246,0.8)] absolute bottom-0 translate-y-1/2"></div>
            
            {/* Location Label (floating below the dot) */}
            <div className="absolute bottom-[-24px] bg-gray-900/90 backdrop-blur-sm px-2 py-0.5 rounded border border-gray-700 text-xs font-bold text-gray-200 whitespace-nowrap shadow-lg">
              {board.location}
            </div>

          </div>
        ))}

      </div>
    </div>
  );
}