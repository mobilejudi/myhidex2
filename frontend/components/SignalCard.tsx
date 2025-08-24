export default function SignalCard() {
  return (
    <div className="p-4 border rounded-lg bg-gray-800 border-gray-700">
      <h3 className="text-lg font-bold">Token Name (TKR)</h3>
      <p className="text-sm text-gray-400">Strength: 2.5x</p>
      <div className="mt-2 h-16 bg-gray-700 rounded-md">
        {/* Placeholder for sparkline chart */}
      </div>
      <div className="mt-4 flex justify-between">
        <button className="px-4 py-2 bg-green-600 rounded-md hover:bg-green-700">Buy</button>
        <button className="px-4 py-2 bg-red-600 rounded-md hover:bg-red-700">Sell</button>
      </div>
    </div>
  );
}
