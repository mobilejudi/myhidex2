export default function SmartActivityTable() {
  const activities = [
    { time: "1m ago", wallet: "KOL_Wallet_1", action: "BUY", amount: "10 SOL", mc: "$1.2M" },
    { time: "2m ago", wallet: "SmartMoney_2", action: "BUY", amount: "5 SOL", mc: "$1.1M" },
    { time: "5m ago", wallet: "KOL_Wallet_1", action: "SELL", amount: "2 SOL", mc: "$1.5M" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-gray-800 border border-gray-700">
        <thead>
          <tr>
            <th className="p-2 border-b border-gray-700 text-left">Time</th>
            <th className="p-2 border-b border-gray-700 text-left">Smart Money</th>
            <th className="p-2 border-b border-gray-700 text-left">Action</th>
            <th className="p-2 border-b border-gray-700 text-left">Amount</th>
            <th className="p-2 border-b border-gray-700 text-left">Market Cap</th>
          </tr>
        </thead>
        <tbody>
          {activities.map((activity, index) => (
            <tr key={index}>
              <td className="p-2 border-b border-gray-700">{activity.time}</td>
              <td className="p-2 border-b border-gray-700">{activity.wallet}</td>
              <td className={`p-2 border-b border-gray-700 ${activity.action === 'BUY' ? 'text-green-500' : 'text-red-500'}`}>{activity.action}</td>
              <td className="p-2 border-b border-gray-700">{activity.amount}</td>
              <td className="p-2 border-b border-gray-700">{activity.mc}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
