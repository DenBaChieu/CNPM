import { useState, useEffect, useRef } from "react";
// Import the image directly so Vite knows to bundle it
import mapImage from '../../images/parking_map.png';

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
  
  // Refs and State for Panning & Zooming Map
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [startY, setStartY] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [scrollTop, setScrollTop] = useState(0);
  const [zoom, setZoom] = useState(1);

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

  // --- Mouse Events for Click and Drag Panning ---
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!mapContainerRef.current) return;
    setIsDragging(true);
    setStartX(e.pageX - mapContainerRef.current.offsetLeft);
    setStartY(e.pageY - mapContainerRef.current.offsetTop);
    setScrollLeft(mapContainerRef.current.scrollLeft);
    setScrollTop(mapContainerRef.current.scrollTop);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !mapContainerRef.current) return;
    e.preventDefault(); 
    const x = e.pageX - mapContainerRef.current.offsetLeft;
    const y = e.pageY - mapContainerRef.current.offsetTop;
    const walkX = (x - startX) * 1.5; 
    const walkY = (y - startY) * 1.5;
    mapContainerRef.current.scrollLeft = scrollLeft - walkX;
    mapContainerRef.current.scrollTop = scrollTop - walkY;
  };

  // --- Scroll Wheel Zoom Logic ---
  const handleWheel = (e: React.WheelEvent) => {
    if (!mapContainerRef.current) return;
    
    const rect = mapContainerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const currentScrollLeft = mapContainerRef.current.scrollLeft;
    const currentScrollTop = mapContainerRef.current.scrollTop;

    // Calculate minimum zoom to ensure the map is never smaller than its container
    const minZoomX = rect.width / 1500;
    const minZoomY = rect.height / 1000;
    const minZoom = Math.max(minZoomX, minZoomY);
    const maxZoom = Math.max(minZoom, 3); // Keep max zoom at 3x, or higher if screen is massive

    setZoom(prevZoom => {
      // Calculate new zoom level
      const zoomDelta = -e.deltaY * 0.001;
      let newZoom = prevZoom + zoomDelta;
      
      // Clamp zoom between the calculated minimum and max limit
      newZoom = Math.min(Math.max(minZoom, newZoom), maxZoom);

      // Adjust scroll to zoom in on the exact mouse pointer location
      if (newZoom !== prevZoom) {
        const ratio = newZoom / prevZoom;
        setTimeout(() => {
          if (mapContainerRef.current) {
            mapContainerRef.current.scrollLeft = (currentScrollLeft + mouseX) * ratio - mouseX;
            mapContainerRef.current.scrollTop = (currentScrollTop + mouseY) * ratio - mouseY;
          }
        }, 0);
      }
      return newZoom;
    });
  };

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

      <div 
        ref={mapContainerRef}
        onMouseDown={handleMouseDown}
        onMouseLeave={handleMouseLeave}
        onMouseUp={handleMouseUp}
        onMouseMove={handleMouseMove}
        onWheel={handleWheel}
        className={`flex-grow w-full overflow-auto rounded border relative ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        <style>
          {`
            div::-webkit-scrollbar {
              display: none;
            }
          `}
        </style>

        {/* Scaled Inner Map Container */}
        <div 
          className="relative pointer-events-none"
          style={{ width: `${1500 * zoom}px`, height: `${1000 * zoom}px` }}
        >
          
          {/* MAP BACKGROUND */}
          <div 
            className="absolute inset-0 opacity-40 bg-cover bg-center"
            style={{ backgroundImage: `url(${mapImage})` }}
          ></div>

          {boards.map((board) => (
            <div 
              key={board.ledID} 
              className="absolute flex flex-col items-center pointer-events-auto transition-transform hover:z-50 hover:scale-110"
              style={{ left: `${board.x}%`, top: `${board.y}%`, transform: 'translate(-50%, -100%)' }}
            >
              
              <div className="bg-white p-2 rounded border shadow flex items-center gap-2">
                {board.displays.map((display, index) => (
                  <div key={index} className="flex justify-center items-center">
                    {renderIcon(display.arrow, display.color)}
                  </div>
                ))}
              </div>

              <div className="w-1 h-2 bg-gray-300"></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full border border-white absolute bottom-0 translate-y-1/2 shadow"></div>
              
              <div className="absolute bottom-[-16px] text-xs font-semibold bg-white px-2 py-0.5 rounded border whitespace-nowrap">
                {board.location}
              </div>

            </div>
          ))}

        </div>
      </div>
    </div>
  );
}