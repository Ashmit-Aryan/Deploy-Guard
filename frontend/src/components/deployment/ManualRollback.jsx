import { useState } from "react";
import { RotateCcw, Loader2 } from "lucide-react";

import { rollbackApplication } from "../../services/api";

function ManualRollback({
  application,
  onRollbackComplete,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleRollback() {
    if (!application || loading) {
      return;
    }

    const confirmed = window.confirm(
      `Rollback ${application.name} to the previous deployment?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await rollbackApplication(application.id);

      if (onRollbackComplete) {
        await onRollbackComplete();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-2xl border border-amber-500/20 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Deployment Control
          </p>

          <h2 className="mt-1 text-lg font-semibold">
            Manual Rollback
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Restore the previous healthy deployment.
          </p>
        </div>

        <button
          type="button"
          onClick={handleRollback}
          disabled={
            loading ||
            !application ||
            application.status !== "active"
          }
          className="flex items-center justify-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-5 py-3 text-sm font-semibold text-amber-300 transition hover:bg-amber-500/20 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <Loader2
              size={18}
              className="animate-spin"
            />
          ) : (
            <RotateCcw size={18} />
          )}

          {loading
            ? "Rolling Back..."
            : "Rollback"}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}
    </section>
  );
}

export default ManualRollback;