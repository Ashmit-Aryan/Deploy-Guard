const API_BASE_URL = "http://localhost:8000";

export async function deployApplication(image, containerName) {
  const response = await fetch(`${API_BASE_URL}/api/deploy`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      image,
      container_name: containerName,
    }),
  });

  if (!response.ok) {
    throw new Error("Deployment request failed");
  }

  return response.json();
}

export async function getDeploymentStatus() {
  const response = await fetch(`${API_BASE_URL}/api/status`);

  if (!response.ok) {
    throw new Error("Failed to fetch deployment status");
  }

  return response.json();
}

export async function rollbackDeployment(
  containerName,
  previousBaseUrl
) {
  const response = await fetch(
    `${API_BASE_URL}/api/rollback`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        container_name: containerName,
        previous_base_url: previousBaseUrl,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Rollback request failed");
  }

  return response.json();
}