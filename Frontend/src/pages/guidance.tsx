import { useState, useEffect } from "react";

type LEDDisplay = {
  arrow: string;
  color: string;
  message: string;
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

  const fetchGuidanceData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/guidance/status");
      const data = await res.json();
      if (data.led_boards) {
        setBoards(data.led_boards);
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

  // Standard Tailwind colors
  const getColorStyles = (color: string) => {
    switch (color) {
      case "GREEN":
        return "text-green-500";
      case "YELLOW":
        return "text-yellow-500";
      case "RED":
        return "text-red-500";
      default:
        return "text-gray-500";
    }
  };

  const renderIcon = (direction: string, color: string) => {
    const styleClass = `w-8 h-8 ${getColorStyles(color)}`;
    
    if (color === "RED") {
      return (
        <svg className={styleClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="3">
          <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }

    switch (direction) {
      case "LEFT":
        return (
          <svg className={styleClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="3">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        );
      case "RIGHT":
        return (
          <svg className={styleClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="3">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        );
      default:
        return (
          <svg className={styleClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="3">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        );
    }
  };

  return (
    <div className="p-6 flex flex-col font-sans h-screen w-full">
      
      <h1 className="text-3xl font-bold mb-6">
        Bản đồ điều hướng bãi đậu xe
      </h1>

      <div className="flex-grow w-full overflow-auto border rounded relative cursor-move">
        
        <div className="w-[1500px] h-[1000px] relative">
          
          {/* MAP BACKGROUND */}
          <div 
            className="absolute inset-0 opacity-80 bg-cover bg-center"
            style={{ backgroundImage: 'images/parking_map.png' }}
          ></div>

          {boards.map((board) => (
            <div 
              key={board.ledID} 
              className="absolute flex flex-col items-center hover:scale-110 transition-transform hover:z-50"
              style={{ left: `${board.x}%`, top: `${board.y}%`, transform: 'translate(-50%, -100%)' }}
            >
              
              <div className="bg-white p-2 rounded border shadow flex items-center gap-2">
                {board.displays.map((display, index) => (
                  <div key={index} className="flex justify-center items-center">
                    {renderIcon(display.arrow, display.color)}
                  </div>
                ))}
              </div>

              <div className="w-1 h-8 bg-gray-300"></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full border border-white absolute bottom-0 translate-y-1/2 shadow"></div>
              
              <div className="absolute bottom-[-24px] text-xs font-semibold bg-white px-2 py-0.5 rounded border whitespace-nowrap">
                {board.location}
              </div>

            </div>
          ))}

        </div>
      </div>
    </div>
  );
}