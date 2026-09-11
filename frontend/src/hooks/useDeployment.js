import { useEffect, useState } from "react";

import {
  deployApplication,
  getDeploymentStatus,
  rollbackDeployment,
} from "../services/api";

function useDeployment() {
  const [loading, setLoading] = useState(false);
  const [deployment, setDeployment] = useState(null);
  const [error, setError] = useState(null);

  async function deploy(image, containerName) {
    try {
      setLoading(true);
      setError(null);

      const result = await deployApplication(
        image,
        containerName
      );

      setDeployment(result);

      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function refreshStatus() {
    try {
      const result = await getDeploymentStatus();

      setDeployment(result);
      setError(null);

      return result;
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refreshStatus();

    const interval = setInterval(() => {
      refreshStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  async function rollback(containerName, previousBaseUrl) {
  try {
    setLoading(true);
    setError(null);

    const result = await rollbackDeployment(
      containerName,
      previousBaseUrl
    );

    setDeployment(result);

    return result;
  } catch (err) {
    setError(err.message);
    throw err;
  } finally {
    setLoading(false);
  }
}

  return {
    loading,
    deployment,
    error,
    deploy,
    rollback,
    refreshStatus,
  };
}



export default useDeployment;