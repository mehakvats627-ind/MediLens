import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const monthlyData = [
  { month: "Jan", reports: 4 },
  { month: "Feb", reports: 7 },
  { month: "Mar", reports: 6 },
  { month: "Apr", reports: 9 },
  { month: "May", reports: 12 },
  { month: "Jun", reports: 8 },
];

const pieData = [
  { name: "Normal", value: 18 },
  { name: "Abnormal", value: 7 },
];

const COLORS = ["#2563eb", "#10b981"];

function ChartSection() {
  return (
    <div className="charts-section">

      {/* Bar Chart */}

      <div className="chart-card">

        <h3>Monthly Reports</h3>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyData}>
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Bar
              dataKey="reports"
              fill="#2563eb"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>

      </div>

      {/* Pie Chart */}

      <div className="chart-card">

        <h3>Report Status</h3>

        <ResponsiveContainer width="100%" height={300}>
          <PieChart>

            <Pie
              data={pieData}
              dataKey="value"
              outerRadius={80}
              label
            >
              {pieData.map((item, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index]}
                />
              ))}
            </Pie>

            <Legend />

            <Tooltip />

          </PieChart>
        </ResponsiveContainer>

      </div>

    </div>
  );
}

export default ChartSection;