import { useEffect, useState } from "react";
import {
  AlertCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";

import DeployForm from "../components/deployment/DeployForm";
import DeploymentStatus from "../components/deployment/DeploymentStatus";
import DeploymentOverview from "../components/dashboard/DeploymentOverview";
import DeploymentHistory from "../components/deployment/DeploymentHistory";
import ManualRollback from "../components/deployment/ManualRollback";

import useDeployment from "../hooks/useDeployment";

import {
  getApplications,
  getApplication,
  getApplicationDeployments,
} from "../services/api";

function Dashboard() {
  const [applications, setApplications] =
    useState([]);

  const [selectedApplicationId, setSelectedApplicationId] =
    useState("");

  const [selectedApplication, setSelectedApplication] =
    useState(null);

  const [deployments, setDeployments] =
    useState([]);

  const [loadingApplications, setLoadingApplications] =
    useState(true);

  const [loadingHistory, setLoadingHistory] =
    useState(false);

  const [applicationError, setApplicationError] =
    useState(null);

  const [historyError, setHistoryError] =
    useState(null);

  const deploymentState = useDeployment();

  async function loadApplications() {
    try {
      setLoadingApplications(true);
      setApplicationError(null);

      const data = await getApplications();

      setApplications(data);

      if (
        data.length > 0 &&
        !selectedApplicationId
      ) {
        setSelectedApplicationId(data[0].id);
      }
    } catch (error) {
      setApplicationError(error.message);
    } finally {
      setLoadingApplications(false);
    }
  }

  async function loadApplication(applicationId) {
    if (!applicationId) {
      setSelectedApplication(null);
      return;
    }

    try {
      const data = await getApplication(
        applicationId
      );

      setSelectedApplication(data);
    } catch (error) {
      setApplicationError(error.message);
    }
  }

  async function loadDeploymentHistory(
    applicationId
  ) {
    if (!applicationId) {
      setDeployments([]);
      return;
    }

    try {
      setLoadingHistory(true);
      setHistoryError(null);

      const data =
        await getApplicationDeployments(
          applicationId
        );

      setDeployments(data);
    } catch (error) {
      setHistoryError(error.message);
    } finally {
      setLoadingHistory(false);
    }
  }

  async function refreshApplicationData() {
    if (!selectedApplicationId) {
      return;
    }

    await Promise.all([
      loadApplication(selectedApplicationId),
      loadDeploymentHistory(
        selectedApplicationId
      ),
    ]);
  }

  useEffect(() => {
    loadApplications();
  }, []);

  useEffect(() => {
    if (!selectedApplicationId) {
      return;
    }

    loadApplication(selectedApplicationId);
    loadDeploymentHistory(
      selectedApplicationId
    );
  }, [selectedApplicationId]);

  useEffect(() => {
    if (!deploymentState.deployment) {
      return;
    }

    const status =
      deploymentState.deployment.status;

    if (
      [
        "success",
        "failed",
        "rolled_back",
      ].includes(status)
    ) {
      refreshApplicationData();
    }
  }, [deploymentState.deployment]);

  return (
    <div className="space-y-8">
      {/* Application selector */}
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Application
            </p>

            <h1 className="mt-1 text-2xl font-bold">
              DeployGuard
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Manage Blue-Green deployments.
            </p>
          </div>

          <button
            type="button"
            onClick={refreshApplicationData}
            disabled={
              loadingApplications ||
              loadingHistory ||
              !selectedApplicationId
            }
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-700 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={
                loadingApplications ||
                loadingHistory
                  ? "animate-spin"
                  : ""
              }
            />

            Refresh
          </button>
        </div>

        <div className="mt-6">
          {loadingApplications ? (
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Loader2
                size={16}
                className="animate-spin"
              />
              Loading applications...
            </div>
          ) : applicationError ? (
            <div className="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
              <AlertCircle size={18} />
              {applicationError}
            </div>
          ) : applications.length === 0 ? (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-400">
              No applications are registered yet.
            </div>
          ) : (
            <>
              <label className="mb-2 block text-sm text-slate-400">
                Select application
              </label>

              <select
                value={selectedApplicationId}
                onChange={(event) =>
                  setSelectedApplicationId(
                    event.target.value
                  )
                }
                disabled={
                  deploymentState.loading
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
              >
                {applications.map(
                  (application) => (
                    <option
                      key={application.id}
                      value={application.id}
                    >
                      {application.name}
                    </option>
                  )
                )}
              </select>
            </>
          )}
        </div>
      </section>

      {selectedApplication && (
        <>
          <DeploymentOverview
            application={selectedApplication}
            deployment={
              deploymentState.deployment
            }
          />

          <DeploymentStatus
            status={
              deploymentState.deployment?.status ||
              "pending"
            }
          />

          <DeployForm
            application={selectedApplication}
            deploy={deploymentState.deploy}
            loading={deploymentState.loading}
            error={deploymentState.error}
            deployment={
              deploymentState.deployment
            }
          />

          <ManualRollback
            application={selectedApplication}
            onRollbackComplete={
              refreshApplicationData
            }
          />

          <DeploymentHistory
            deployments={deployments}
          />

          {loadingHistory && (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2
                size={16}
                className="animate-spin"
              />
              Refreshing deployment history...
            </div>
          )}

          {historyError && (
            <p className="text-sm text-red-400">
              {historyError}
            </p>
          )}
        </>
      )}
    </div>
  );
}

export default Dashboard;