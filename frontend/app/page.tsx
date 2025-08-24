import SignalCard from "../components/SignalCard";
import SmartActivityTable from "../components/SmartActivityTable";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">AI Signals</h1>
      </div>

      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Placeholder for signal cards */}
        <SignalCard />
        <SignalCard />
        <SignalCard />
      </div>

      <div className="mt-24 w-full">
        <h2 className="text-2xl font-bold mb-4">Smart Activity</h2>
        <SmartActivityTable />
      </div>
    </main>
  );
}
