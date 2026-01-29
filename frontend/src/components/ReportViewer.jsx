import React from "react";
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Globe,
  FileText,
  Zap,
  AlertOctagon,
  Info,
  ArrowRight,
  Lock,
  Unlock,
  Search,
  List,
} from "lucide-react";

const RISK_CONFIG = {
  LOW: {
    color: "text-green-400",
    bg: "bg-green-500/20",
    border: "border-green-500/50",
    icon: CheckCircle,
  },
  MEDIUM: {
    color: "text-yellow-400",
    bg: "bg-yellow-500/20",
    border: "border-yellow-500/50",
    icon: AlertTriangle,
  },
  HIGH: {
    color: "text-orange-400",
    bg: "bg-orange-500/20",
    border: "border-orange-500/50",
    icon: AlertOctagon,
  },
  CRITICAL: {
    color: "text-red-500",
    bg: "bg-red-500/20",
    border: "border-red-500/50",
    icon: AlertOctagon,
  },
};

const SeverityBadge = ({ severity }) => {
  const config = RISK_CONFIG[severity] || RISK_CONFIG.LOW;
  return (
    <span
      className={`px-2 py-0.5 text-xs rounded ${config.bg} ${config.color} ${config.border} border`}
    >
      {severity}
    </span>
  );
};

const Card = ({
  title,
  icon: Icon,
  children,
  className = "",
  iconColor = "text-green-400",
}) => (
  <div
    className={`bg-black/50 border border-green-900/50 rounded-lg overflow-hidden ${className}`}
  >
    <div className="flex items-center gap-2 px-4 py-3 bg-green-950/30 border-b border-green-900/50">
      <Icon size={18} className={iconColor} />
      <h3 className="text-sm font-semibold uppercase tracking-wide text-green-400">
        {title}
      </h3>
    </div>
    <div className="p-4">{children}</div>
  </div>
);

const StatBox = ({ label, value, icon: Icon, color = "text-green-400" }) => (
  <div className="bg-black/30 border border-green-900/30 rounded p-3 text-center">
    <Icon size={20} className={`mx-auto mb-1 ${color}`} />
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
    <div className="text-xs text-green-700 uppercase">{label}</div>
  </div>
);

export default function ReportViewer({ report }) {
  if (!report) return null;

  const riskConfig = RISK_CONFIG[report.risk_level] || RISK_CONFIG.LOW;
  const RiskIcon = riskConfig.icon;

  return (
    <div className="h-full overflow-y-auto space-y-4 pb-4">
      <div
        className={`p-4 rounded-lg ${riskConfig.bg} border ${riskConfig.border}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${riskConfig.bg}`}>
              <RiskIcon size={32} className={riskConfig.color} />
            </div>
            <div>
              <div className="text-xs text-green-600 uppercase">
                Overall Risk Level
              </div>
              <div className={`text-2xl font-bold ${riskConfig.color}`}>
                {report.risk_level || "LOW"}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-green-600 uppercase">Target</div>
            <div className="text-green-400 text-sm font-mono truncate max-w-xs">
              {report.target}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <StatBox
          label="Steps"
          value={report.steps_completed || 0}
          icon={Zap}
          color="text-cyan-400"
        />
        <StatBox
          label="Pages"
          value={report.pages_visited?.length || 0}
          icon={Globe}
          color="text-purple-400"
        />
        <StatBox
          label="Inputs Found"
          value={report.inputs_found?.length || 0}
          icon={FileText}
          color="text-blue-400"
        />
        <StatBox
          label="Vulnerabilities"
          value={report.vulnerabilities?.length || 0}
          icon={AlertTriangle}
          color={
            report.vulnerabilities?.length > 0
              ? "text-red-400"
              : "text-green-400"
          }
        />
      </div>

      <Card title="Executive Summary" icon={Info} iconColor="text-cyan-400">
        <p className="text-green-300 leading-relaxed">
          {report.summary || "No summary available."}
        </p>
      </Card>

      <Card
        title={`Vulnerabilities Found (${report.vulnerabilities?.length || 0})`}
        icon={AlertTriangle}
        iconColor={
          report.vulnerabilities?.length > 0 ? "text-red-400" : "text-green-400"
        }
      >
        {report.vulnerabilities?.length > 0 ? (
          <div className="space-y-3">
            {report.vulnerabilities.map((vuln, idx) => (
              <div
                key={idx}
                className="bg-red-950/20 border border-red-900/30 rounded p-3"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-red-400">
                    {vuln.type}
                  </span>
                  <SeverityBadge severity={vuln.severity} />
                </div>
                <div className="text-xs text-green-600 mb-1">
                  Location: {vuln.location}
                </div>
                <p className="text-sm text-green-300">{vuln.description}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-green-500">
            <CheckCircle size={18} />
            <span>No vulnerabilities detected. Site appears secure.</span>
          </div>
        )}
      </Card>

      <Card title="Inputs Tested" icon={Search} iconColor="text-blue-400">
        {report.inputs_tested?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-green-600 border-b border-green-900/50">
                  <th className="pb-2 pr-4">Input</th>
                  <th className="pb-2 pr-4">Payload</th>
                  <th className="pb-2">Result</th>
                </tr>
              </thead>
              <tbody>
                {report.inputs_tested.map((test, idx) => (
                  <tr key={idx} className="border-b border-green-900/20">
                    <td className="py-2 pr-4 text-cyan-400">{test.input}</td>
                    <td className="py-2 pr-4 font-mono text-xs text-yellow-400">
                      {test.payload}
                    </td>
                    <td className="py-2 text-green-300">{test.result}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-green-600 text-sm">
            No input fields were tested.
          </div>
        )}
      </Card>

      <Card title="Pages Visited" icon={Globe} iconColor="text-purple-400">
        {report.pages_visited?.length > 0 ? (
          <ul className="space-y-1">
            {report.pages_visited.map((page, idx) => (
              <li key={idx} className="flex items-center gap-2 text-sm">
                <ArrowRight size={14} className="text-purple-400" />
                <span className="text-green-300 font-mono truncate">
                  {page}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-green-600 text-sm">No pages recorded.</div>
        )}
      </Card>

      <Card
        title="Security Recommendations"
        icon={Shield}
        iconColor="text-yellow-400"
      >
        {report.recommendations?.length > 0 ? (
          <ul className="space-y-2">
            {report.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <CheckCircle
                  size={14}
                  className="text-yellow-400 mt-0.5 flex-shrink-0"
                />
                <span className="text-green-300">{rec}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-green-600 text-sm">
            No specific recommendations. Consider regular security audits.
          </div>
        )}
      </Card>
    </div>
  );
}
