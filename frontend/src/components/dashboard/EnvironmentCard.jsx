import {
  CheckCircle2,
  Circle,
  Server,
} from "lucide-react";

function EnvironmentCard({
  name,
  version,
  port,
  status,
  active,
}) {
  return (
    <div
      className={`rounded-2xl border p-5 transition ${
        active
          ? "border-emerald-500/50 bg-emerald-500/5"
          : "border-slate-800 bg-slate-950"
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`rounded-xl p-2 ${
              active
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-slate-800 text-slate-400"
            }`}
          >
            <Server size={20} />
          </div>

          <div>
            <h3 className="font-semibold">{name}</h3>
            <p className="text-xs text-slate-500">
              Environment
            </p>
          </div>
        </div>

        {active ? (
          <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
            <CheckCircle2 size={15} />
            ACTIVE
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-slate-500">
            <Circle size={13} />
            STANDBY
          </span>
        )}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-3">
        <div>
          <p className="text-xs text-slate-500">Version</p>
          <p className="mt-1 font-medium">{version}</p>
        </div>

        <div>
          <p className="text-xs text-slate-500">Port</p>
          <p className="mt-1 font-medium">{port}</p>
        </div>

        <div>
          <p className="text-xs text-slate-500">Status</p>
          <p
            className={`mt-1 font-medium ${
              status === "Healthy"
                ? "text-emerald-400"
                : "text-slate-400"
            }`}
          >
            {status}
          </p>
        </div>
      </div>
    </div>
  );
}

export default EnvironmentCard;