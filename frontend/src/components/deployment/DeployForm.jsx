import { Rocket } from "lucide-react";
import { useState } from "react";

function DeployForm({
  deploy,
  loading,
  error,
  deployment,
}) {
  const [image, setImage] = useState("deployguard-demo:v2");
  const [containerName, setContainerName] = useState(
    "deployguard-demo-green"
  );

  async function handleSubmit(event) {
    event.preventDefault();

    if (loading) {
      return;
    }

    await deploy(image, containerName);
  }

  const status = deployment?.status || "pending";

  const isDeploying = [
    "deploying",
    "health_check",
    "smoke_test",
    "switching",
    "monitoring",
    "rolling_back",
  ].includes(status);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-blue-500/10 p-2 text-blue-400">
            <Rocket size={20} />
          </div>

          <div>
            <h2 className="text-lg font-semibold">
              Deploy Application
            </h2>

            <p className="text-sm text-slate-400">
              Start a Blue-Green deployment
            </p>
          </div>
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        <div>
          <label className="mb-2 block text-sm text-slate-400">
            Docker Image
          </label>

          <input
            value={image}
            onChange={(event) =>
              setImage(event.target.value)
            }
            disabled={isDeploying}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="my-app:v2"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm text-slate-400">
            Container Name
          </label>

          <input
            value={containerName}
            onChange={(event) =>
              setContainerName(event.target.value)
            }
            disabled={isDeploying}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="deployguard-demo-green"
          />
        </div>

        <button
          type="submit"
          disabled={loading || isDeploying}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Rocket size={18} />

          {isDeploying
            ? "Deployment In Progress..."
            : "Deploy Application"}
        </button>
      </form>

      {deployment && (
        <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Current Status
          </p>

          <p className="mt-1 font-semibold capitalize">
            {status.replaceAll("_", " ")}
          </p>

          {deployment.active_environment && (
            <p className="mt-1 text-sm text-slate-500">
              Active environment:{" "}
              {deployment.active_environment}
            </p>
          )}
        </div>
      )}

      {error && (
        <div className="mt-5 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}
    </section>
  );
}

export default DeployForm;