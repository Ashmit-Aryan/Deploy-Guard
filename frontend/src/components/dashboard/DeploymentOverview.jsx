import { Activity, GitBranch, Rocket } from "lucide-react";
import EnvironmentCard from "./EnvironmentCard";
function DeploymentOverview({ deployment }) {
  const activeEnvironment = deployment?.active_environment || "blue";

  const deploymentStatus = deployment?.status || "pending";

  const activeVersion = activeEnvironment === "green" ? "2.0.0" : "1.0.0";

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Production Deployment</h2>

          <p className="mt-1 text-sm text-slate-400">
            Current Blue-Green deployment state
          </p>
        </div>

        <Rocket className="text-blue-400" size={24} />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          label="Active Version"
          value={activeVersion}
          icon={<GitBranch size={20} />}
        />

        <StatCard
          label="Environment"
          value={
            activeEnvironment.charAt(0).toUpperCase() +
            activeEnvironment.slice(1)
          }
          icon={<Activity size={20} />}
        />

        <StatCard
          label="Deployment Status"
          value={formatStatus(deploymentStatus)}
          icon={<Rocket size={20} />}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <EnvironmentCard
          name="Blue"
          version="1.0.0"
          port="8001"
          status={
            activeEnvironment === "blue"
              ? "Active"
              : deploymentStatus === "rolled_back"
                ? "Restored"
                : "Standby"
          }
          active={activeEnvironment === "blue"}
        />

        <EnvironmentCard
          name="Green"
          version="2.0.0"
          port="8002"
          status={
            activeEnvironment === "green"
              ? "Active"
              : deploymentStatus === "rolled_back"
                ? "Rolled Back"
                : "Standby"
          }
          active={activeEnvironment === "green"}
        />
      </div>
    </section>
  );
}

function formatStatus(status) {
  return status
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function StatCard({ label, value, icon }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center gap-2 text-slate-400">
        {icon}
        <span className="text-sm">{label}</span>
      </div>

      <p className="mt-4 text-2xl font-bold">{value}</p>
    </div>
  );
}

export default DeploymentOverview;
