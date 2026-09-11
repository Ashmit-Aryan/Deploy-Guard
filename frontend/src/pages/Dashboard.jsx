import DeploymentOverview from "../components/dashboard/DeploymentOverview";
import DeploymentPipeline from "../components/dashboard/DeploymentPipeline";
import DeployForm from "../components/deployment/DeployForm";
import RollbackProtection from "../components/dashboard/RollbackProtection";
import useDeployment from "../hooks/useDeployment";
import DeploymentStatus from "../components/deployment/DeploymentStatus";
function Dashboard() {
  const deploymentState = useDeployment();

  return (
<div className="space-y-8">
  <DeploymentOverview
    deployment={deploymentState.deployment}
  />

  <DeploymentStatus
    status={deploymentState.deployment?.status || "pending"}
  />

  <DeploymentPipeline
    status={deploymentState.deployment?.status || "pending"}
  />

  <DeployForm
    deploy={deploymentState.deploy}
    loading={deploymentState.loading}
    error={deploymentState.error}
    deployment={deploymentState.deployment}
  />

  <RollbackProtection
    deployment={deploymentState.deployment}
    rollback={deploymentState.rollback}
    loading={deploymentState.loading}
  />
</div>
  );
}

export default Dashboard;