import { Rocket } from "lucide-react";
import { useEffect, useState } from "react";

function DeployForm({
  application,
  deploy,
  loading,
  error,
  deployment,
}) {
  const [image, setImage] = useState(
    application?.image_repository
      ? `${application.image_repository}:v2`
      : ""
  );

  const [version, setVersion] = useState(
    application?.current_version || "2.0.0"
  );

  useEffect(() => {
    if (!application) {
      return;
    }

    setImage(
      application.image_repository
        ? `${application.image_repository}:v2`
        : ""
    );

    setVersion(
      application.current_version || "2.0.0"
    );
  }, [application]);

  async function handleSubmit(event) {
    event.preventDefault();

    if (
      loading ||
      !application ||
      !version ||
      !image
    ) {
      return;
    }

    await deploy(
      application.id,
      version,
      image
    );
  }

  const status =
    deployment?.status || "pending";

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
              {application?.name || "No application selected"}
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
            Version
          </label>

          <input
            value={version}
            onChange={(event) =>
              setVersion(event.target.value)
            }
            disabled={isDeploying}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="2.0.0"
          />
        </div>

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
            placeholder="deployguard-demo:v2"
          />
        </div>

        <button
          type="submit"
          disabled={
            loading ||
            isDeploying ||
            !application ||
            !version ||
            !image
          }
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
            Current Deployment
          </p>

          <p className="mt-1 font-semibold capitalize">
            {status.replaceAll("_", " ")}
          </p>

          {deployment.target_environment && (
            <p className="mt-1 text-sm text-slate-500">
              Target:{" "}
              {deployment.target_environment}
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