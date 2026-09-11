import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  deployApplication,
  getDeploymentStatus,
} from "../services/api";

const TERMINAL_STATES = new Set([
  "success",
  "failed",
  "rolled_back",
]);

function useDeployment() {
  const [loading, setLoading] =
    useState(false);

  const [deployment, setDeployment] =
    useState(null);

  const [deploymentId, setDeploymentId] =
    useState(null);

  const [error, setError] =
    useState(null);

  const deploy = useCallback(
    async (
      applicationId,
      version,
      image
    ) => {
      try {
        setLoading(true);
        setError(null);

        const result =
          await deployApplication(
            applicationId,
            version,
            image
          );

        setDeployment(result);
        setDeploymentId(
          result.deployment_id
        );

        return result;
      } catch (err) {
        setError(err.message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const refreshStatus =
    useCallback(async () => {
      if (!deploymentId) {
        return null;
      }

      try {
        const result =
          await getDeploymentStatus(
            deploymentId
          );

        setDeployment(result);
        setError(null);

        return result;
      } catch (err) {
        setError(err.message);
        return null;
      }
    }, [deploymentId]);

  useEffect(() => {
    if (!deploymentId) {
      return undefined;
    }

    let cancelled = false;

    const poll = async () => {
      if (!cancelled) {
        await refreshStatus();
      }
    };

    poll();

    const interval =
      setInterval(async () => {
        if (cancelled) {
          return;
        }

        const result =
          await refreshStatus();

        if (
          result &&
          TERMINAL_STATES.has(
            result.status
          )
        ) {
          clearInterval(interval);
        }
      }, 2000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [deploymentId, refreshStatus]);

  return {
    loading,
    deployment,
    deploymentId,
    error,
    deploy,
    refreshStatus,
  };
}

export default useDeployment;