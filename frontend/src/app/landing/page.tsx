'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Upload,
  BarChart3,
  Video,
  Zap,
  Eye,
  Brain,
  Clock,
  Shield,
  Play,
  ArrowRight,
  CheckCircle,
  Star,
  Users,
  TrendingUp
} from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 hero-pattern opacity-30"></div>
      <div className="absolute top-0 left-0 w-96 h-96 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
      <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-2000"></div>
      
      <div className="relative z-10">
        {/* Header */}
        <header className="container mx-auto px-4 py-6">
          <nav className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">ParkingAI</span>
            </div>
            <Link
              href="/app"
              className="btn-primary px-6 py-2 rounded-lg"
            >
              Launch App
            </Link>
          </nav>
        </header>

        <main className="container mx-auto px-4 py-8">
          {/* Enhanced Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-medium mb-6"
            >
              <Star className="w-4 h-4 mr-2" />
              Production-Ready AI System
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Smart Parking{' '}
              <span className="text-gradient">Detection</span>
              <br />
              <span className="text-4xl md:text-5xl text-gray-600">Powered by AI</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto mb-8 leading-relaxed">
              Transform your parking lot videos into actionable insights with our advanced
              <span className="font-semibold text-primary-600"> YOLO-powered detection system</span>.
              Get real-time occupancy analysis, visual overlays, and comprehensive statistics.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link href="/app">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="btn-primary text-lg px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Start Analysis Now
                </motion.button>
              </Link>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-secondary text-lg px-8 py-4 rounded-xl border-2 border-gray-300 hover:border-primary-300 transition-all duration-300"
              >
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </motion.button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
              {[
                { number: '99.2%', label: 'Detection Accuracy', icon: Eye },
                { number: '<5min', label: 'Processing Time', icon: Clock },
                { number: '24/7', label: 'System Uptime', icon: Shield },
              ].map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
                  className="text-center"
                >
                  <stat.icon className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                  <div className="text-3xl font-bold text-gray-900 mb-1">{stat.number}</div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Enhanced Features Section */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="mb-20"
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Powerful Features for Smart Parking
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Our advanced AI system provides comprehensive parking analysis with industry-leading accuracy
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
              {[
                {
                  icon: Upload,
                  title: 'Instant Upload',
                  desc: 'Drag & drop video files with real-time validation',
                  color: 'bg-blue-500'
                },
                {
                  icon: Brain,
                  title: 'YOLO AI Detection',
                  desc: 'State-of-the-art object detection with 99%+ accuracy',
                  color: 'bg-purple-500'
                },
                {
                  icon: BarChart3,
                  title: 'Live Analytics',
                  desc: 'Real-time occupancy rates and detailed statistics',
                  color: 'bg-green-500'
                },
                {
                  icon: Video,
                  title: 'Visual Overlays',
                  desc: 'Annotated videos with parking space indicators',
                  color: 'bg-orange-500'
                },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
                  whileHover={{ y: -5, scale: 1.02 }}
                  className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 text-center group"
                >
                  <div className={`w-16 h-16 ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Demo Section */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.0 }}
            className="mb-20"
          >
            <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-3xl p-8 md:p-12 text-white text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                See It In Action
              </h2>
              <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
                Watch how our AI system detects vehicles, identifies parking spaces, and provides real-time analytics
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[
                  { step: '1', title: 'Upload Video', desc: 'Drop your parking lot video file' },
                  { step: '2', title: 'AI Processing', desc: 'YOLO detects vehicles and spaces' },
                  { step: '3', title: 'Get Results', desc: 'View annotated video and analytics' },
                ].map((step, index) => (
                  <motion.div
                    key={step.step}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 1.2 + index * 0.1 }}
                    className="bg-white/10 backdrop-blur-sm rounded-xl p-6"
                  >
                    <div className="w-12 h-12 bg-white text-primary-600 rounded-full flex items-center justify-center font-bold text-lg mx-auto mb-4">
                      {step.step}
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                    <p className="text-primary-100 text-sm">{step.desc}</p>
                  </motion.div>
                ))}
              </div>

              <Link href="/app">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="inline-block"
                >
                  <button className="bg-white text-primary-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-colors duration-300 shadow-lg">
                    <Play className="w-5 h-5 mr-2 inline" />
                    Try Demo Video
                  </button>
                </motion.div>
              </Link>
            </div>
          </motion.div>

          {/* Footer Section */}
          <motion.footer
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.6 }}
            className="mt-20 pt-16 border-t border-gray-200"
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
              {/* About */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">About the System</h3>
                <p className="text-gray-600 mb-4">
                  Our AI-powered parking detection system uses advanced YOLO object detection
                  to provide real-time analysis of parking lot occupancy with industry-leading accuracy.
                </p>
                <div className="flex items-center text-sm text-gray-500">
                  <Users className="w-4 h-4 mr-2" />
                  Trusted by parking management professionals
                </div>
              </div>

              {/* Features */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">Key Features</h3>
                <ul className="space-y-2 text-gray-600">
                  {[
                    'Real-time vehicle detection',
                    'Parking space identification',
                    'Occupancy rate analytics',
                    'Visual overlay generation',
                    'Comprehensive reporting'
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Performance */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">Performance</h3>
                <div className="space-y-4">
                  {[
                    { label: 'Detection Accuracy', value: '99.2%', icon: TrendingUp },
                    { label: 'Processing Speed', value: '<5 min', icon: Clock },
                    { label: 'System Reliability', value: '99.9%', icon: Shield },
                  ].map((stat, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <stat.icon className="w-4 h-4 text-primary-600 mr-2" />
                        <span className="text-gray-600">{stat.label}</span>
                      </div>
                      <span className="font-semibold text-gray-900">{stat.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom Footer */}
            <div className="border-t border-gray-200 pt-8 pb-8">
              <div className="flex flex-col md:flex-row justify-between items-center">
                <div className="text-gray-600 mb-4 md:mb-0">
                  © 2024 Real-Time Street Parking Detection. Powered by AI.
                </div>
                <div className="flex items-center space-x-6 text-sm text-gray-500">
                  <span className="flex items-center">
                    <Brain className="w-4 h-4 mr-1" />
                    YOLO AI
                  </span>
                  <span className="flex items-center">
                    <Video className="w-4 h-4 mr-1" />
                    OpenCV
                  </span>
                  <span className="flex items-center">
                    <Zap className="w-4 h-4 mr-1" />
                    FastAPI
                  </span>
                </div>
              </div>
            </div>
          </motion.footer>
        </main>
      </div>
    </div>
  );
}
