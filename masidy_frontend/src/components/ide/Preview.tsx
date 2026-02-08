'use client'

import React, { useState } from 'react'
import { Monitor, Smartphone, Tablet, RefreshCw, ExternalLink, Loader2 } from 'lucide-react'

interface PreviewProps {
  url?: string
  isLoading?: boolean
  projectName?: string
}

type DeviceSize = 'desktop' | 'tablet' | 'mobile'

const deviceSizes: Record<DeviceSize, { width: string; label: string }> = {
  desktop: { width: '100%', label: 'Desktop' },
  tablet: { width: '768px', label: 'Tablet' },
  mobile: { width: '375px', label: 'Mobile' },
}

export function Preview({ url, isLoading, projectName = 'Project' }: PreviewProps) {
  const [device, setDevice] = useState<DeviceSize>('desktop')
  const [refreshKey, setRefreshKey] = useState(0)

  const refresh = () => setRefreshKey((k) => k + 1)

  const DeviceButton = ({
    deviceType,
    icon: Icon,
  }: {
    deviceType: DeviceSize
    icon: React.ElementType
  }) => (
    <button
      className={`p-1.5 rounded transition-colors ${
        device === deviceType
          ? 'bg-primary text-white'
          : 'hover:bg-surface text-secondary'
      }`}
      onClick={() => setDevice(deviceType)}
      title={deviceSizes[deviceType].label}
    >
      <Icon className="w-4 h-4" />
    </button>
  )

  return (
    <div className="h-full bg-surface flex flex-col">
      {/* Toolbar */}
      <div className="h-10 bg-white border-b border-border flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Preview</span>
          {url && (
            <span className="text-xs text-secondary px-2 py-0.5 bg-surface rounded">
              {projectName}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 border border-border rounded p-0.5">
            <DeviceButton deviceType="desktop" icon={Monitor} />
            <DeviceButton deviceType="tablet" icon={Tablet} />
            <DeviceButton deviceType="mobile" icon={Smartphone} />
          </div>

          <button
            onClick={refresh}
            className="p-1.5 hover:bg-surface rounded transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4 text-secondary" />
          </button>

          {url && (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 hover:bg-surface rounded transition-colors"
              title="Open in new tab"
            >
              <ExternalLink className="w-4 h-4 text-secondary" />
            </a>
          )}
        </div>
      </div>

      {/* Preview Area */}
      <div className="flex-1 flex items-center justify-center p-4 overflow-hidden">
        {isLoading ? (
          <div className="text-center">
            <Loader2 className="w-8 h-8 text-secondary animate-spin mx-auto mb-3" />
            <p className="text-secondary">Building preview...</p>
          </div>
        ) : url ? (
          <div
            className="bg-white rounded-lg shadow-lg overflow-hidden transition-all duration-300"
            style={{
              width: deviceSizes[device].width,
              maxWidth: '100%',
              height: '100%',
            }}
          >
            <iframe
              key={refreshKey}
              src={url}
              className="w-full h-full border-0"
              title="Preview"
            />
          </div>
        ) : (
          <div className="text-center max-w-sm">
            <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mx-auto mb-4">
              <Monitor className="w-8 h-8 text-secondary" />
            </div>
            <h3 className="font-semibold mb-2">No Preview Available</h3>
            <p className="text-secondary text-sm">
              Start building your project and the preview will appear here automatically.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
