import {
  AlertTriangle,
  CheckCircle2,
  RotateCcw,
} from "lucide-react";

function RollbackProtection({
  deployment,
  loading,
  rollback,
}) {
  const activeEnvironment =
    deployment?.active_environment || "blue";

  const status =
    deployment?.status || "pending";

  const canRollback =
    activeEnvironment === "green" &&
    !loading;

  const rolledBack =
    status === "rolled_back";

  async function handleRollback() {
    if (!canRollback) {
      return;
    }

    await rollback(
      "deployguard-demo-green",
      "http://localhost:8001"
    );
  }

  return (
    <section className="rounded-2xl border border-amber-500/20 bg-slate-900 p-6">
      <div className="flex items-start gap-4">
        <div className="rounded-xl bg-amber-500/10 p-2 text-amber-400">
          <AlertTriangle size={22} />
        </div>

        <div className="flex-1">
          <h2 className="font-semibold">
            Rollback Protection
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Restore the previous healthy environment
            if the current release fails.
          </p>

          {rolledBack && (
            <div className="mt-4 flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-400">
              <CheckCircle2 size={18} />

              Previous healthy environment restored.
            </div>
          )}

          <button
            onClick={handleRollback}
            disabled={!canRollback}
            className="mt-5 flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm font-semibold text-amber-400 transition hover:bg-amber-500/20 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <RotateCcw size={17} />

            {loading
              ? "Rolling Back..."
              : "Rollback Deployment"}
          </button>

          {!canRollback && !rolledBack && (
            <p className="mt-3 text-xs text-slate-600">
              Rollback is available when Green is active.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default RollbackProtection;