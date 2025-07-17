'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Car, 
  Clock, 
  BarChart3, 
  PieChart as PieChartIcon,
  Download,
  Calendar,
  Activity
} from 'lucide-react'

// Mock data for demonstration
const mockOccupancyData = [
  { time: '00:00', occupancy: 15, available: 85 },
  { time: '02:00', occupancy: 8, available: 92 },
  { time: '04:00', occupancy: 5, available: 95 },
  { time: '06:00', occupancy: 25, available: 75 },
  { time: '08:00', occupancy: 75, available: 25 },
  { time: '10:00', occupancy: 85, available: 15 },
  { time: '12:00', occupancy: 90, available: 10 },
  { time: '14:00', occupancy: 95, available: 5 },
  { time: '16:00', occupancy: 88, available: 12 },
  { time: '18:00', occupancy: 70, available: 30 },
  { time: '20:00', occupancy: 45, available: 55 },
  { time: '22:00', occupancy: 30, available: 70 }
]

const mockVehicleTypes = [
  { name: 'Cars', value: 78, color: '#3b82f6' },
  { name: 'SUVs', value: 15, color: '#10b981' },
  { name: 'Trucks', value: 5, color: '#f59e0b' },
  { name: 'Motorcycles', value: 2, color: '#ef4444' }
]

const mockWeeklyData = [
  { day: 'Mon', avgOccupancy: 72, peakOccupancy: 95 },
  { day: 'Tue', avgOccupancy: 68, peakOccupancy: 92 },
  { day: 'Wed', avgOccupancy: 75, peakOccupancy: 98 },
  { day: 'Thu', avgOccupancy: 73, peakOccupancy: 96 },
  { day: 'Fri', avgOccupancy: 80, peakOccupancy: 100 },
  { day: 'Sat', avgOccupancy: 85, peakOccupancy: 100 },
  { day: 'Sun', avgOccupancy: 45, peakOccupancy: 78 }
]

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('today')
  const [selectedMetric, setSelectedMetric] = useState('occupancy')

  const stats = [
    {
      title: 'Current Occupancy',
      value: '87%',
      change: '+5%',
      trend: 'up',
      icon: Car,
      description: '26 of 30 spaces occupied'
    },
    {
      title: 'Peak Time Today',
      value: '2:30 PM',
      change: '98% occupied',
      trend: 'up',
      icon: Clock,
      description: 'Highest occupancy period'
    },
    {
      title: 'Average Duration',
      value: '2.4 hrs',
      change: '-12 min',
      trend: 'down',
      icon: Activity,
      description: 'Average parking duration'
    },
    {
      title: 'Total Vehicles',
      value: '156',
      change: '+23',
      trend: 'up',
      icon: BarChart3,
      description: 'Vehicles detected today'
    }
  ]

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-6 w-6" />
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
              <SelectItem value="custom">Custom Range</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
                </div>
                <div className="flex flex-col items-end">
                  <stat.icon className="h-8 w-8 text-muted-foreground mb-2" />
                  <Badge variant={stat.trend === 'up' ? 'default' : 'secondary'} className="text-xs">
                    {stat.trend === 'up' ? (
                      <TrendingUp className="h-3 w-3 mr-1" />
                    ) : (
                      <TrendingDown className="h-3 w-3 mr-1" />
                    )}
                    {stat.change}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Occupancy Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Occupancy Over Time</CardTitle>
            <CardDescription>Parking space utilization throughout the day</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={mockOccupancyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="occupancy" 
                  stackId="1"
                  stroke="#3b82f6" 
                  fill="#3b82f6" 
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="available" 
                  stackId="1"
                  stroke="#10b981" 
                  fill="#10b981" 
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Vehicle Types */}
        <Card>
          <CardHeader>
            <CardTitle>Vehicle Type Distribution</CardTitle>
            <CardDescription>Types of vehicles detected</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={mockVehicleTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {mockVehicleTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Occupancy Trends</CardTitle>
            <CardDescription>Average vs peak occupancy by day</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockWeeklyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="avgOccupancy" fill="#3b82f6" name="Average" />
                <Bar dataKey="peakOccupancy" fill="#1d4ed8" name="Peak" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Processing Jobs</CardTitle>
            <CardDescription>Latest video analysis results</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { id: 'job-001', time: '2 hours ago', duration: '45 min', vehicles: 23, status: 'completed' },
                { id: 'job-002', time: '5 hours ago', duration: '1.2 hrs', vehicles: 31, status: 'completed' },
                { id: 'job-003', time: '1 day ago', duration: '30 min', vehicles: 18, status: 'completed' },
                { id: 'job-004', time: '2 days ago', duration: '2.1 hrs', vehicles: 45, status: 'completed' }
              ].map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{job.id}</p>
                    <p className="text-sm text-muted-foreground">{job.time}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{job.vehicles} vehicles</p>
                    <p className="text-sm text-muted-foreground">{job.duration}</p>
                  </div>
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    {job.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
