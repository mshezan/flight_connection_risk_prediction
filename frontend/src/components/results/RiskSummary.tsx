import type { ConnectionResult } from "@/types/flight";

interface RiskSummaryProps {
  result: ConnectionResult;
}

export default function RiskSummary({
  result,
}: RiskSummaryProps) {
  const riskPercentage = Math.round(
    result.risk_score * 100
  );

  function getRiskStyles() {
    switch (result.risk_level.toLowerCase()) {
      case "low":
        return {
          badge:
            "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
          bar:
            "from-emerald-500 to-emerald-400",
          glow:
            "shadow-emerald-500/10",
        };

      case "medium":
        return {
          badge:
            "border-amber-500/30 bg-amber-500/10 text-amber-400",
          bar:
            "from-amber-500 to-orange-400",
          glow:
            "shadow-amber-500/10",
        };

      case "high":
        return {
          badge:
            "border-red-500/30 bg-red-500/10 text-red-400",
          bar:
            "from-red-500 to-rose-400",
          glow:
            "shadow-red-500/10",
        };

      default:
        return {
          badge:
            "border-[#6657e8]/30 bg-[#6657e8]/10 text-[#9487ff]",
          bar:
            "from-[#6254e8] to-[#8b7cff]",
          glow:
            "shadow-[#6254e8]/10",
        };
    }
  }

  const styles = getRiskStyles();

  return (
    <section
      className={`
        rounded-2xl
        border
        border-[#26364d]
        bg-[#0d192b]
        p-6
        shadow-lg
        shadow-black/10
      `}
    >
      {/* RESULT HEADER */}

      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[#8b7cff]">
            Connection Analysis
          </p>

          <h2 className="mt-2 text-2xl font-bold tracking-tight text-white lg:text-3xl">
            Your connection risk is{" "}
            <span className="capitalize">
              {result.risk_level.toLowerCase()}
            </span>
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#aeb9cc] lg:text-base">
            Based on the predicted delay of your incoming
            flight and the available connection window.
          </p>
        </div>

        <div
          className={`
            shrink-0
            rounded-full
            border
            px-4
            py-2
            text-sm
            font-semibold
            ${styles.badge}
          `}
        >
          {result.risk_level} Risk
        </div>
      </div>

      {/* RISK SCORE */}

      <div className="mt-7 rounded-xl border border-[#26364d] bg-[#0a1425] p-5">
        <div className="mb-3 flex items-end justify-between">
          <div>
            <p className="text-sm font-medium text-[#aeb9cc]">
              Risk score
            </p>

            <p className="mt-1 text-xs text-[#718096]">
              Estimated probability of missing the connection
            </p>
          </div>

          <span className="text-4xl font-bold tracking-tight text-white">
            {riskPercentage}%
          </span>
        </div>

        <div className="h-2.5 overflow-hidden rounded-full bg-[#1a2940]">
          <div
            className={`
              h-full
              rounded-full
              bg-gradient-to-r
              transition-all
              duration-700
              ${styles.bar}
            `}
            style={{
              width: `${Math.min(
                Math.max(riskPercentage, 0),
                100
              )}%`,
            }}
          />
        </div>
      </div>

      {/* METRICS */}

      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <MetricCard
          label="Layover"
          value={`${result.layover_minutes} min`}
          description="Scheduled connection window"
        />

        <MetricCard
          label="Expected delay"
          value={`${result.expected_delay_minutes.toFixed(1)} min`}
          description="Predicted incoming flight delay"
        />

        <MetricCard
          label="Remaining buffer"
          value={`${result.remaining_buffer.toFixed(1)} min`}
          description="Estimated time left after delay"
        />
      </div>
    </section>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  description: string;
}

function MetricCard({
  label,
  value,
  description,
}: MetricCardProps) {
  return (
    <div
      className="
        rounded-xl
        border
        border-[#26364d]
        bg-[#0a1425]
        p-5
        transition
        hover:border-[#3b4c67]
      "
    >
      <p className="text-sm font-medium text-[#8f9db2]">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold tracking-tight text-white">
        {value}
      </p>

      <p className="mt-1 text-xs text-[#66758c]">
        {description}
      </p>
    </div>
  );
}