export default function Header() {
  return (
    <header className="px-6 pb-5 pt-7 lg:px-9">
      <h1 className="text-3xl font-bold tracking-tight text-white lg:text-4xl">
        Flight Connection{" "}
        <span className="bg-gradient-to-r from-[#8b7cff] to-[#a78bfa] bg-clip-text text-transparent">
          Risk Predictor
        </span>
      </h1>

      <p className="mt-2 max-w-3xl text-sm leading-6 text-[#aeb9cc] lg:text-base">
        Predict missed flight connections using machine learning trained on
        historical US flight data.
      </p>
    </header>
  );
}