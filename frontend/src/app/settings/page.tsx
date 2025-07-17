'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Settings, Save, RotateCcw, Camera, Cpu, Palette } from 'lucide-react'

interface DetectionSettings {
  confidenceThreshold: number
  iouThreshold: number
  frameSkip: number
  enableRealProcessing: boolean
  maxProcessingTime: number
}

interface DisplaySettings {
  showBoundingBoxes: boolean
  showConfidenceScores: boolean
  showParkingSpaceLabels: boolean
  overlayOpacity: number
  colorScheme: 'default' | 'high-contrast' | 'colorblind'
}

export default function SettingsPage() {
  const [detectionSettings, setDetectionSettings] = useState<DetectionSettings>({
    confidenceThreshold: 0.5,
    iouThreshold: 0.4,
    frameSkip: 5,
    enableRealProcessing: true,
    maxProcessingTime: 300
  })

  const [displaySettings, setDisplaySettings] = useState<DisplaySettings>({
    showBoundingBoxes: true,
    showConfidenceScores: true,
    showParkingSpaceLabels: true,
    overlayOpacity: 0.7,
    colorScheme: 'default'
  })

  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const handleSaveSettings = async () => {
    setSaveStatus('saving')
    try {
      // Simulate API call to save settings
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } catch (error) {
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    }
  }

  const handleResetSettings = () => {
    setDetectionSettings({
      confidenceThreshold: 0.5,
      iouThreshold: 0.4,
      frameSkip: 5,
      enableRealProcessing: true,
      maxProcessingTime: 300
    })
    setDisplaySettings({
      showBoundingBoxes: true,
      showConfidenceScores: true,
      showParkingSpaceLabels: true,
      overlayOpacity: 0.7,
      colorScheme: 'default'
    })
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex items-center gap-2 mb-6">
        <Settings className="h-6 w-6" />
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>

      <div className="max-w-4xl mx-auto">
        <Tabs defaultValue="detection" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="detection" className="flex items-center gap-2">
              <Camera className="h-4 w-4" />
              Detection
            </TabsTrigger>
            <TabsTrigger value="processing" className="flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              Processing
            </TabsTrigger>
            <TabsTrigger value="display" className="flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Display
            </TabsTrigger>
          </TabsList>

          <TabsContent value="detection" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>YOLO Detection Settings</CardTitle>
                <CardDescription>
                  Configure the AI model parameters for vehicle detection
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="confidence">
                    Confidence Threshold: {detectionSettings.confidenceThreshold}
                  </Label>
                  <Slider
                    id="confidence"
                    min={0.1}
                    max={0.9}
                    step={0.05}
                    value={[detectionSettings.confidenceThreshold]}
                    onValueChange={(value) =>
                      setDetectionSettings(prev => ({ ...prev, confidenceThreshold: value[0] }))
                    }
                    className="w-full"
                  />
                  <p className="text-sm text-muted-foreground">
                    Higher values = fewer false positives, lower values = more detections
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="iou">
                    IoU Threshold: {detectionSettings.iouThreshold}
                  </Label>
                  <Slider
                    id="iou"
                    min={0.1}
                    max={0.8}
                    step={0.05}
                    value={[detectionSettings.iouThreshold]}
                    onValueChange={(value) =>
                      setDetectionSettings(prev => ({ ...prev, iouThreshold: value[0] }))
                    }
                    className="w-full"
                  />
                  <p className="text-sm text-muted-foreground">
                    Controls overlap threshold for duplicate detection removal
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="processing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Processing Configuration</CardTitle>
                <CardDescription>
                  Configure video processing and performance settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="real-processing">Enable Real AI Processing</Label>
                    <p className="text-sm text-muted-foreground">
                      Use actual YOLO detection vs fast demo mode
                    </p>
                  </div>
                  <Switch
                    id="real-processing"
                    checked={detectionSettings.enableRealProcessing}
                    onCheckedChange={(checked) =>
                      setDetectionSettings(prev => ({ ...prev, enableRealProcessing: checked }))
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="frame-skip">
                    Frame Skip: {detectionSettings.frameSkip}
                  </Label>
                  <Slider
                    id="frame-skip"
                    min={1}
                    max={10}
                    step={1}
                    value={[detectionSettings.frameSkip]}
                    onValueChange={(value) =>
                      setDetectionSettings(prev => ({ ...prev, frameSkip: value[0] }))
                    }
                    className="w-full"
                  />
                  <p className="text-sm text-muted-foreground">
                    Process every Nth frame (higher = faster but less accurate)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max-time">Max Processing Time (seconds)</Label>
                  <Input
                    id="max-time"
                    type="number"
                    value={detectionSettings.maxProcessingTime}
                    onChange={(e) =>
                      setDetectionSettings(prev => ({ 
                        ...prev, 
                        maxProcessingTime: parseInt(e.target.value) || 300 
                      }))
                    }
                    className="w-full"
                  />
                  <p className="text-sm text-muted-foreground">
                    Maximum time allowed for video processing
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="display" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Display Options</CardTitle>
                <CardDescription>
                  Customize how detection results are displayed
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="show-boxes">Show Bounding Boxes</Label>
                    <Switch
                      id="show-boxes"
                      checked={displaySettings.showBoundingBoxes}
                      onCheckedChange={(checked) =>
                        setDisplaySettings(prev => ({ ...prev, showBoundingBoxes: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="show-confidence">Show Confidence Scores</Label>
                    <Switch
                      id="show-confidence"
                      checked={displaySettings.showConfidenceScores}
                      onCheckedChange={(checked) =>
                        setDisplaySettings(prev => ({ ...prev, showConfidenceScores: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="show-labels">Show Parking Space Labels</Label>
                    <Switch
                      id="show-labels"
                      checked={displaySettings.showParkingSpaceLabels}
                      onCheckedChange={(checked) =>
                        setDisplaySettings(prev => ({ ...prev, showParkingSpaceLabels: checked }))
                      }
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="opacity">
                    Overlay Opacity: {Math.round(displaySettings.overlayOpacity * 100)}%
                  </Label>
                  <Slider
                    id="opacity"
                    min={0.1}
                    max={1.0}
                    step={0.1}
                    value={[displaySettings.overlayOpacity]}
                    onValueChange={(value) =>
                      setDisplaySettings(prev => ({ ...prev, overlayOpacity: value[0] }))
                    }
                    className="w-full"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {saveStatus !== 'idle' && (
          <Alert className={saveStatus === 'error' ? 'border-red-500' : 'border-green-500'}>
            <AlertDescription>
              {saveStatus === 'saving' && 'Saving settings...'}
              {saveStatus === 'saved' && 'Settings saved successfully!'}
              {saveStatus === 'error' && 'Error saving settings. Please try again.'}
            </AlertDescription>
          </Alert>
        )}

        <div className="flex gap-4 justify-end">
          <Button variant="outline" onClick={handleResetSettings}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button onClick={handleSaveSettings} disabled={saveStatus === 'saving'}>
            <Save className="h-4 w-4 mr-2" />
            {saveStatus === 'saving' ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </div>
    </div>
  )
}
