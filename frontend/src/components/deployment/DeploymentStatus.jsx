import {
  CheckCircle2,
  Clock3,
  Loader2,
  RotateCcw,
  XCircle,
} from "lucide-react";

const statusConfig = {
  pending: {
    label: "Pending",
    description: "Deployment is waiting to start.",
    icon: Clock3,
  },

  deploying: {
    label: "Deploying",
    description: "Starting the new application environment.",
    icon: Loader2,
  },

  health_check: {
    label: "Health Check",
    description: "Checking whether the new environment is healthy.",
    icon: Loader2,
  },

  smoke_test: {
    label: "Smoke Test",
    description: "Validating critical application endpoints.",
    icon: Loader2,
  },

  switching: {
    label: "Switching Traffic",
    description: "Moving production traffic to the new environment.",
    icon: Loader2,
  },

  monitoring: {
    label: "Monitoring",
    description: "Watching the new release for failures.",
    icon: Loader2,
  },

  success: {
    label: "Deployment Successful",
    description: "The new release is serving production traffic.",
    icon: CheckCircle2,
  },

  failed: {
    label: "Deployment Failed",
    description: "The deployment failed and needs attention.",
    icon: XCircle,
  },

  rolling_back: {
    label: "Rolling Back",
    description: "Restoring the previous healthy environment.",
    icon: RotateCcw,
  },

  rolled_back: {
    label: "Rolled Back",
    description: "Production traffic has been restored to the previous environment.",
    icon: RotateCcw,
  },
};

function DeploymentStatus({ status = "pending" }) {
  const config =
    statusConfig[status] || statusConfig.pending;

  const Icon = config.icon;

  const isActive = [
    "deploying",
    "health_check",
    "smoke_test",
    "switching",
    "monitoring",
    "rolling_back",
  ].includes(status);

  const isSuccess = [
    "success",
    "rolled_back",
  ].includes(status);

  const isFailed = status === "failed";

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex items-center gap-4">
        <div
          className={`rounded-xl p-3 ${
            isFailed
              ? "bg-red-500/10 text-red-400"
              : isSuccess
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-blue-500/10 text-blue-400"
          }`}
        >
          <Icon
            size={24}
            className={isActive ? "animate-spin" : ""}
          />
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Current Deployment State
          </p>

          <h2 className="mt-1 text-xl font-semibold">
            {config.label}
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            {config.description}
          </p>
        </div>
      </div>
    </section>
  );
}

export default DeploymentStatus;