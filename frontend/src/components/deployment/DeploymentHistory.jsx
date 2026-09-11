import {
  CheckCircle2,
  Clock3,
  RotateCcw,
  XCircle,
} from "lucide-react";

const statusConfig = {
  success: {
    label: "Success",
    icon: CheckCircle2,
    className: "text-emerald-400",
  },

  failed: {
    label: "Failed",
    icon: XCircle,
    className: "text-red-400",
  },

  rolled_back: {
    label: "Rolled Back",
    icon: RotateCcw,
    className: "text-amber-400",
  },

  deploying: {
    label: "Deploying",
    icon: Clock3,
    className: "text-blue-400",
  },

  health_check: {
    label: "Health Check",
    icon: Clock3,
    className: "text-blue-400",
  },

  smoke_test: {
    label: "Smoke Test",
    icon: Clock3,
    className: "text-blue-400",
  },

  switching: {
    label: "Switching",
    icon: Clock3,
    className: "text-blue-400",
  },

  monitoring: {
    label: "Monitoring",
    icon: Clock3,
    className: "text-blue-400",
  },

  rolling_back: {
    label: "Rolling Back",
    icon: RotateCcw,
    className: "text-amber-400",
  },

  pending: {
    label: "Pending",
    icon: Clock3,
    className: "text-slate-400",
  },
};

function DeploymentHistory({ deployments = [] }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-6">
        <p className="text-xs uppercase tracking-wider text-slate-500">
          History
        </p>

        <h2 className="mt-1 text-xl font-semibold">
          Deployment History
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Previous deployment attempts for this application.
        </p>
      </div>

      {deployments.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 text-sm text-slate-400">
          No deployments found.
        </div>
      ) : (
        <div className="space-y-3">
          {deployments.map((deployment) => {
            const config =
              statusConfig[deployment.status] ||
              statusConfig.pending;

            const Icon = config.icon;

            return (
              <div
                key={deployment.deployment_id}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4"
              >
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                  <div className="flex items-start gap-3">
                    <Icon
                      size={20}
                      className={`mt-0.5 ${config.className}`}
                    />

                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold">
                          v{deployment.version}
                        </p>

                        <span className="rounded-full border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
                          {formatValue(
                            deployment.target_environment
                          )}
                        </span>

                        <span className="rounded-full border border-slate-700 px-2 py-0.5 text-xs text-slate-500">
                          {formatValue(
                            deployment.strategy
                          )}
                        </span>
                      </div>

                      <p
                        className={`mt-1 text-sm font-medium ${config.className}`}
                      >
                        {config.label}
                      </p>

                      {deployment.failure_reason && (
                        <p className="mt-2 text-sm text-red-400">
                          {deployment.failure_reason}
                        </p>
                      )}

                      <p className="mt-2 text-xs text-slate-600">
                        {formatDate(
                          deployment.created_at
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="text-left md:text-right">
                    <p className="text-xs text-slate-500">
                      Deployment ID
                    </p>

                    <p className="mt-1 max-w-xs truncate font-mono text-xs text-slate-400">
                      {deployment.deployment_id}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function formatValue(value) {
  if (!value) {
    return "Unknown";
  }

  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }

  return new Date(value).toLocaleString();
}

export default DeploymentHistory;