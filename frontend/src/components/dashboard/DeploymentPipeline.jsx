import {
  CheckCircle2,
  Circle,
  Loader2,
  RotateCcw,
  XCircle,
} from "lucide-react";

const stages = [
  { key: "deploying", label: "Deploying" },
  { key: "health_check", label: "Health Check" },
  { key: "smoke_test", label: "Smoke Test" },
  { key: "switching", label: "Switching Traffic" },
  { key: "monitoring", label: "Monitoring" },
  { key: "success", label: "Success" },
];

function DeploymentPipeline({ status = "pending" }) {
  const currentIndex = getCurrentIndex(status);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold">
          Deployment Pipeline
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Live deployment progress
        </p>
      </div>

      <div className="space-y-1">
        {stages.map((stage, index) => {
          const state = getStageState(
            index,
            currentIndex,
            status
          );

          return (
            <div key={stage.key}>
              <div className="flex items-center gap-4 py-3">
                <StageIcon state={state} />

                <div>
                  <p
                    className={`font-medium ${
                      state === "completed"
                        ? "text-emerald-400"
                        : state === "active"
                          ? "text-blue-400"
                          : state === "failed"
                            ? "text-red-400"
                            : "text-slate-500"
                    }`}
                  >
                    {stage.label}
                  </p>

                  {state === "active" && (
                    <p className="mt-1 text-xs text-slate-500">
                      In progress...
                    </p>
                  )}

                  {state === "completed" && (
                    <p className="mt-1 text-xs text-slate-600">
                      Completed
                    </p>
                  )}
                </div>
              </div>

              {index < stages.length - 1 && (
                <div className="ml-[10px] h-3 border-l border-slate-800" />
              )}
            </div>
          );
        })}
      </div>

      {status === "rolled_back" && (
        <div className="mt-5 flex items-center gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-400">
          <RotateCcw size={18} />
          Deployment was rolled back to the previous environment.
        </div>
      )}
    </section>
  );
}

function getCurrentIndex(status) {
  if (status === "pending") {
    return -1;
  }

  if (status === "failed") {
    return -1;
  }

  if (status === "rolled_back") {
    return stages.findIndex(
      (stage) => stage.key === "monitoring"
    );
  }

  const index = stages.findIndex(
    (stage) => stage.key === status
  );

  return index;
}

function getStageState(index, currentIndex, status) {
  if (status === "success") {
    return "completed";
  }

  if (status === "failed") {
    return index === 0 ? "failed" : "pending";
  }

  if (status === "rolled_back") {
    if (index < currentIndex) {
      return "completed";
    }

    if (index === currentIndex) {
      return "failed";
    }

    return "pending";
  }

  if (index < currentIndex) {
    return "completed";
  }

  if (index === currentIndex) {
    return "active";
  }

  return "pending";
}

function StageIcon({ state }) {
  if (state === "completed") {
    return (
      <CheckCircle2
        size={22}
        className="text-emerald-400"
      />
    );
  }

  if (state === "active") {
    return (
      <Loader2
        size={22}
        className="animate-spin text-blue-400"
      />
    );
  }

  if (state === "failed") {
    return (
      <XCircle
        size={22}
        className="text-red-400"
      />
    );
  }

  return (
    <Circle
      size={22}
      className="text-slate-700"
    />
  );
}

export default DeploymentPipeline;