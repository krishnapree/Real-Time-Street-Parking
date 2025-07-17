'use client';

import { useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Activity } from 'lucide-react';
import { FrameAnalysis } from '@/types';
import { formatDuration, formatPercentage } from '@/utils';

interface StatisticsChartProps {
  data: FrameAnalysis[];
  title?: string;
  className?: string;
}

type ChartType = 'line' | 'area' | 'bar';

export default function StatisticsChart({ 
  data, 
  title = "Parking Statistics",
  className = ""
}: StatisticsChartProps) {
  const [chartType, setChartType] = useState<ChartType>('line');
  const [selectedMetric, setSelectedMetric] = useState<'occupancy' | 'spaces'>('occupancy');

  // Transform data for charts
  const chartData = data.map((frame, index) => ({
    time: formatDuration(frame.timestamp),
    timestamp: frame.timestamp,
    occupancy_rate: frame.occupancy_rate * 100,
    occupied_spaces: frame.occupied_spaces,
    available_spaces: frame.available_spaces,
    total_spaces: frame.total_spaces,
    frame_number: frame.frame_number
  }));

  // Sample data points for better performance with large datasets
  const sampleData = chartData.length > 100 
    ? chartData.filter((_, index) => index % Math.ceil(chartData.length / 100) === 0)
    : chartData;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">{`Time: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.name}: ${
                entry.dataKey.includes('rate') 
                  ? `${entry.value.toFixed(1)}%`
                  : entry.value
              }`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderChart = () => {
    const commonProps = {
      data: sampleData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    if (selectedMetric === 'occupancy') {
      switch (chartType) {
        case 'area':
          return (
            <AreaChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="occupancy_rate"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
                name="Occupancy Rate"
                strokeWidth={2}
              />
            </AreaChart>
          );
        
        case 'bar':
          return (
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar
                dataKey="occupancy_rate"
                fill="#3b82f6"
                name="Occupancy Rate"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          );
        
        default:
          return (
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="occupancy_rate"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
                activeDot={{ r: 5, stroke: '#3b82f6', strokeWidth: 2 }}
                name="Occupancy Rate"
              />
            </LineChart>
          );
      }
    } else {
      switch (chartType) {
        case 'area':
          return (
            <AreaChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="occupied_spaces"
                stackId="1"
                stroke="#ef4444"
                fill="#ef4444"
                fillOpacity={0.6}
                name="Occupied Spaces"
              />
              <Area
                type="monotone"
                dataKey="available_spaces"
                stackId="1"
                stroke="#22c55e"
                fill="#22c55e"
                fillOpacity={0.6}
                name="Available Spaces"
              />
            </AreaChart>
          );
        
        case 'bar':
          return (
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar
                dataKey="occupied_spaces"
                stackId="a"
                fill="#ef4444"
                name="Occupied Spaces"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="available_spaces"
                stackId="a"
                fill="#22c55e"
                name="Available Spaces"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          );
        
        default:
          return (
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="occupied_spaces"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 3 }}
                name="Occupied Spaces"
              />
              <Line
                type="monotone"
                dataKey="available_spaces"
                stroke="#22c55e"
                strokeWidth={2}
                dot={{ fill: '#22c55e', strokeWidth: 2, r: 3 }}
                name="Available Spaces"
              />
            </LineChart>
          );
      }
    }
  };

  if (!data || data.length === 0) {
    return (
      <div className={`card ${className}`}>
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No data available for chart</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`card ${className}`}
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600">
            Visualize parking occupancy trends over time
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-4 mt-4 md:mt-0">
          {/* Metric Selector */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setSelectedMetric('occupancy')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                selectedMetric === 'occupancy'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Occupancy %
            </button>
            <button
              onClick={() => setSelectedMetric('spaces')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                selectedMetric === 'spaces'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Space Count
            </button>
          </div>

          {/* Chart Type Selector */}
          <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            {[
              { type: 'line' as ChartType, icon: TrendingUp },
              { type: 'area' as ChartType, icon: Activity },
              { type: 'bar' as ChartType, icon: BarChart3 },
            ].map(({ type, icon: Icon }) => (
              <button
                key={type}
                onClick={() => setChartType(type)}
                className={`p-2 rounded-md transition-colors ${
                  chartType === type
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title={`${type.charAt(0).toUpperCase() + type.slice(1)} chart`}
              >
                <Icon className="w-4 h-4" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t border-gray-200">
        <div className="text-center">
          <p className="text-sm text-gray-600">Average Occupancy</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatPercentage(
              chartData.reduce((sum, d) => sum + d.occupancy_rate, 0) / chartData.length / 100
            )}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Peak Occupancy</p>
          <p className="text-lg font-semibold text-error-600">
            {formatPercentage(Math.max(...chartData.map(d => d.occupancy_rate)) / 100)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Data Points</p>
          <p className="text-lg font-semibold text-gray-900">
            {chartData.length.toLocaleString()}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
