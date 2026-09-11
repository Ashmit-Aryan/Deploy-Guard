const API_BASE_URL = "http://localhost:8000";

async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    // No JSON body.
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Request failed with status ${response.status}`,
    );
  }

  return data;
}

export async function getApplications() {
  return request(`${API_BASE_URL}/api/applications`);
}

export async function getApplication(applicationId) {
  return request(`${API_BASE_URL}/api/applications/${applicationId}`);
}

export async function deployApplication(applicationId, version, image) {
  return request(`${API_BASE_URL}/api/applications/${applicationId}/deploy`, {
    method: "POST",
    body: JSON.stringify({
      version,
      image,
    }),
  });
}

export async function getDeploymentStatus(deploymentId) {
  return request(`${API_BASE_URL}/api/deployments/${deploymentId}`);
}

export async function getApplicationDeployments(applicationId) {
  return request(
    `${API_BASE_URL}/api/applications/${applicationId}/deployments`,
  );
}

export async function rollbackApplication(applicationId) {
  return request(`${API_BASE_URL}/api/applications/${applicationId}/rollback`, {
    method: "POST",
  });
}
