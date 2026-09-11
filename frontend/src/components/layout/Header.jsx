import { CircleDot, ShieldCheck } from "lucide-react";

function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-950">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-blue-600 p-2">
            <ShieldCheck size={24} />
          </div>

          <div>
            <h1 className="text-xl font-bold">DeployGuard</h1>
            <p className="text-xs text-slate-400">
              Zero-Downtime Deployment Platform
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400">
          <CircleDot size={14} />
          System Operational
        </div>
      </div>
    </header>
  );
}

export default Header;