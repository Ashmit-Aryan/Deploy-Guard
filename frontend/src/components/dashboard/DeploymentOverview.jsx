import {
  Activity,
  GitBranch,
  Rocket,
} from "lucide-react";

function DeploymentOverview({
  application,
  deployment,
}) {
  if (!application) {
    return null;
  }

  const activeEnvironment =
    application.active_environment || "unknown";

  const activeVersion =
    application.current_version || "—";

  const deploymentStatus =
    deployment?.status ||
    application.status ||
    "unknown";

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Production Deployment
          </p>

          <h2 className="mt-1 text-xl font-semibold">
            {application.name}
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Current application state
          </p>
        </div>

        <Rocket
          className="text-blue-400"
          size={24}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          label="Active Version"
          value={activeVersion}
          icon={<GitBranch size={20} />}
        />

        <StatCard
          label="Environment"
          value={formatValue(activeEnvironment)}
          icon={<Activity size={20} />}
        />

        <StatCard
          label="Status"
          value={formatStatus(deploymentStatus)}
          icon={<Rocket size={20} />}
        />
      </div>

      {deployment && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="grid gap-4 sm:grid-cols-3">
            <Info
              label="Deployment ID"
              value={deployment.deployment_id}
            />

            <Info
              label="Target Environment"
              value={formatValue(
                deployment.target_environment
              )}
            />

            <Info
              label="Image"
              value={deployment.image}
            />
          </div>
        </div>
      )}
    </section>
  );
}

function StatCard({
  label,
  value,
  icon,
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center gap-2 text-slate-400">
        {icon}
        <span className="text-sm">
          {label}
        </span>
      </div>

      <p className="mt-4 text-2xl font-bold">
        {value}
      </p>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-1 truncate text-sm text-slate-200">
        {value || "—"}
      </p>
    </div>
  );
}

function formatValue(value) {
  if (!value) {
    return "—";
  }

  return (
    value.charAt(0).toUpperCase() +
    value.slice(1)
  );
}

function formatStatus(status) {
  return status
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

export default DeploymentOverview;