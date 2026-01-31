import React, { useState, useEffect, useRef } from "react";
import {
  Terminal,
  ShieldAlert,
  Wifi,
  Activity,
  AlertCircle,
  CheckCircle,
  Loader,
  Zap,
  Globe,
  ArrowRight,
  Clock,
  X,
} from "lucide-react";
import ReportViewer from "./components/ReportViewer";

const API_BASE_URL = import.meta.env.VITE_API_URL || "https://fortex26-2.onrender.com";

function App() {
  const [url, setUrl] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [runId, setRunId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState("IDLE");
  const [currentStep, setCurrentStep] = useState(0);
  const [report, setReport] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const logsEndRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setIsRunning(true);
    setStatus("INITIALIZING");
    setCurrentStep(0);
    setReport(null);
    setShowReport(false);
    setLogs([
      {
        timestamp: new Date().toISOString(),
        message: `Initializing scan on ${url}...`,
        type: "info",
      },
    ]);

    try {
      const response = await fetch(`${API_BASE_URL}/attack`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      setRunId(data.runId);
      setStatus("SCANNING");
    } catch (error) {
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          message: `Connection failed: ${error.message}`,
          type: "error",
        },
      ]);
      setIsRunning(false);
      setStatus("ERROR");
    }
  };


  useEffect(() => {
    if (!runId) return;

    // HTTP polling instead of Firebase
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/status/${runId}`);

        if (response.status === 404) {
          setIsRunning(false);
          setStatus("ERROR");
          setLogs((prev) => [
            ...prev,
            {
              timestamp: new Date().toISOString(),
              message: "Scan session lost (server likely restarted). Please start a new scan.",
              type: "error",
            },
          ]);
          clearInterval(pollInterval);
          return;
        }

        if (!response.ok) return;

        const data = await response.json();

        // Update status
        if (data.status) {
          setStatus(data.status);
          if (data.status === "COMPLETE" || data.status === "ERROR") {
            setIsRunning(false);
            clearInterval(pollInterval);
          }
        }

        // Update logs
        if (data.logs) {
          let latestStep = 0;
          data.logs.forEach((log) => {
            if (log.type === "step") {
              const match = log.message.match(/\[Step (\d+)\]/);
              if (match) latestStep = parseInt(match[1]);
            }
          });
          setCurrentStep(latestStep);
          setLogs(data.logs);
        }

        // Update report
        if (data.report) {
          setReport(data.report);
          setShowReport(true);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [runId]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const getLogIcon = (type) => {
    switch (type) {
      case "error":
        return <AlertCircle size={14} className="text-red-500" />;
      case "success":
        return <CheckCircle size={14} className="text-cyan-400" />;
      case "step":
        return <ArrowRight size={14} className="text-purple-400" />;
      default:
        return <Zap size={14} className="text-green-500" />;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case "error":
        return "text-red-400";
      case "success":
        return "text-cyan-400";
      case "step":
        return "text-purple-300";
      default:
        return "text-green-400";
    }
  };

  const getStatusDisplay = () => {
    switch (status) {
      case "INITIALIZING":
        return {
          text: "INITIALIZING",
          color: "text-yellow-500",
          icon: <Loader size={14} className="animate-spin" />,
        };
      case "SCANNING":
        return {
          text: "SCANNING",
          color: "text-green-500 animate-pulse",
          icon: <Activity size={14} />,
        };
      case "COMPLETE":
        return {
          text: "COMPLETE",
          color: "text-cyan-400",
          icon: <CheckCircle size={14} />,
        };
      case "ERROR":
        return {
          text: "ERROR",
          color: "text-red-500",
          icon: <AlertCircle size={14} />,
        };
      default:
        return {
          text: "IDLE",
          color: "text-green-700",
          icon: <Activity size={14} />,
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  const handleReset = () => {
    setIsRunning(false);
    setRunId(null);
    setLogs([]);
    setStatus("IDLE");
    setCurrentStep(0);
    setReport(null);
    setShowReport(false);
  };

  return (
    <div className="h-screen w-full flex flex-col p-4 font-mono text-green-500 bg-black overflow-hidden">
      <header className="flex justify-between items-center mb-4 border-b border-green-900 pb-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <Terminal size={32} className="text-green-400" />
          <h1 className="text-2xl font-bold tracking-widest uppercase">
            Neural X <span className="text-green-700 text-sm">V.002</span>
          </h1>
        </div>
        <div className="flex gap-6 text-sm">
          <div className="flex items-center gap-2 text-green-700">
            <Wifi size={16} />
            <span>CONNECTED</span>
          </div>
          <div className={`flex items-center gap-2 ${statusDisplay.color}`}>
            {statusDisplay.icon}
            <span>{statusDisplay.text}</span>
          </div>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden gap-4">
        {!isRunning && !report ? (
          <div className="flex-1 flex flex-col justify-center items-center">
            <div className="w-full max-w-4xl">
              <div className="mb-8 text-center">
                <ShieldAlert
                  size={64}
                  className="mx-auto mb-4 text-green-600"
                />
                <h1 className="text-4xl mb-2" style={{ color: '#00c950' }}>
                  Full Security Audit
                </h1>
                <p className="text-green-700 text-lg">
                  Enter a URL to begin automated security scanning
                </p>
              </div>
              <form onSubmit={handleSubmit} className="relative">
                <div className="flex items-center border border-green-800 bg-black/50 focus-within:border-green-500 focus-within:ring-1 focus-within:ring-green-500 rounded">
                  <Globe size={20} className="ml-4 text-green-700" />
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://target.com"
                    className="flex-1 bg-transparent p-4 text-xl focus:outline-none placeholder-green-900/50"
                    autoFocus
                  />
                  <button
                    type="submit"
                    className="m-2 uppercase text-sm bg-green-900 border border-green-600 px-6 py-2 hover:bg-green-800 transition-all flex items-center gap-2 rounded"
                  >
                    <Zap size={16} />
                    Scan
                  </button>
                </div>
              </form>
            </div>
          </div>
        ) : (
          <>
            <div
              className={`flex flex-col border border-green-900 bg-black/50 rounded overflow-hidden ${showReport ? "w-1/3 min-w-80" : "flex-1"}`}
            >
              <div className="flex justify-between items-center border-b border-green-900/50 px-3 py-2 bg-green-950/30 flex-shrink-0">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50" />
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/50" />
                  </div>
                  <span className="text-xs opacity-70 ml-2">Terminal</span>
                </div>
                {!isRunning && (
                  <button
                    onClick={handleReset}
                    className="text-xs text-green-600 hover:text-green-400"
                  >
                    New Scan
                  </button>
                )}
              </div>

              {isRunning && (
                <div className="px-3 py-2 border-b border-green-900/30 flex-shrink-0">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-green-600">Scanning...</span>
                    <span className="text-green-500">Step {currentStep}</span>
                  </div>
                  <div className="h-1.5 bg-green-950 rounded overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-600 to-cyan-500 transition-all duration-500"
                      style={{ width: `${Math.min(currentStep * 8, 100)}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex-1 overflow-y-auto p-3 space-y-1 text-xs">
                {logs.map((log, idx) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-2 ${getLogColor(log.type)}`}
                  >
                    <span className="mt-0.5">{getLogIcon(log.type)}</span>
                    <span className="opacity-50">
                      [{new Date(log.timestamp).toLocaleTimeString()}]
                    </span>
                    <span className="flex-1 break-all">{log.message}</span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            </div>

            {showReport && report && (
              <div className="flex-1 flex flex-col border border-cyan-900/50 bg-black/30 rounded overflow-hidden">
                <div className="flex justify-between items-center border-b border-cyan-900/50 px-4 py-2 bg-cyan-950/20 flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <ShieldAlert size={18} className="text-cyan-400" />
                    <span className="text-sm font-semibold text-cyan-400 uppercase">
                      Security Report
                    </span>
                  </div>
                  <button
                    onClick={() => setShowReport(false)}
                    className="text-cyan-600 hover:text-cyan-400"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                  <ReportViewer report={report} />
                </div>
              </div>
            )}
          </>
        )}
      </main>

      <footer className="mt-2 pt-2 border-t border-green-950 text-center text-base font-semibold text-green-900 flex-shrink-0">
        Team Neural X
      </footer>
    </div>
  );
}

export default App;
