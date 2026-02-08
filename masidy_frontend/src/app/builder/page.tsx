'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ComponentProperty {
  name: string;
  type: string;
  default: any;
  options?: string[];
  description?: string;
}

interface ComponentDefinition {
  id: string;
  name: string;
  category: string;
  icon: string;
  properties: ComponentProperty[];
  children_allowed: boolean;
  default_styles: Record<string, any>;
}

interface ComponentInstance {
  id: string;
  component_id: string;
  properties: Record<string, any>;
  styles: Record<string, any>;
  children: ComponentInstance[];
}

const CATEGORY_ICONS: Record<string, string> = {
  layout: '📐',
  input: '✏️',
  display: '📄',
  navigation: '🧭',
};

export default function VisualBuilderPage() {
  const { isAuthenticated } = useAuth();
  const [components, setComponents] = useState<ComponentDefinition[]>([]);
  const [canvas, setCanvas] = useState<ComponentInstance[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<ComponentInstance | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/visual-builder/components`);
        const data = await res.json();
        setComponents(data);
      } catch (error) {
        console.error('Failed to fetch components:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchComponents();
  }, []);

  const categories = ['all', ...new Set(components.map(c => c.category))];

  const filteredComponents = selectedCategory === 'all' 
    ? components 
    : components.filter(c => c.category === selectedCategory);

  const addToCanvas = useCallback((componentDef: ComponentDefinition) => {
    const newInstance: ComponentInstance = {
      id: `${componentDef.id}-${Date.now()}`,
      component_id: componentDef.id,
      properties: componentDef.properties.reduce((acc, prop) => {
        acc[prop.name] = prop.default;
        return acc;
      }, {} as Record<string, any>),
      styles: { ...componentDef.default_styles },
      children: [],
    };
    
    setCanvas(prev => [...prev, newInstance]);
    setSelectedComponent(newInstance);
  }, []);

  const updateComponentProperty = useCallback((instanceId: string, propName: string, value: any) => {
    setCanvas(prev => prev.map(comp => {
      if (comp.id === instanceId) {
        return {
          ...comp,
          properties: { ...comp.properties, [propName]: value }
        };
      }
      return comp;
    }));
    
    if (selectedComponent?.id === instanceId) {
      setSelectedComponent(prev => prev ? {
        ...prev,
        properties: { ...prev.properties, [propName]: value }
      } : null);
    }
  }, [selectedComponent]);

  const removeFromCanvas = useCallback((instanceId: string) => {
    setCanvas(prev => prev.filter(comp => comp.id !== instanceId));
    if (selectedComponent?.id === instanceId) {
      setSelectedComponent(null);
    }
  }, [selectedComponent]);

  const moveComponent = useCallback((instanceId: string, direction: 'up' | 'down') => {
    setCanvas(prev => {
      const index = prev.findIndex(c => c.id === instanceId);
      if (index === -1) return prev;
      
      const newIndex = direction === 'up' ? index - 1 : index + 1;
      if (newIndex < 0 || newIndex >= prev.length) return prev;
      
      const newCanvas = [...prev];
      [newCanvas[index], newCanvas[newIndex]] = [newCanvas[newIndex], newCanvas[index]];
      return newCanvas;
    });
  }, []);

  const renderComponent = (instance: ComponentInstance) => {
    const def = components.find(c => c.id === instance.component_id);
    if (!def) return null;

    const props = instance.properties;
    const isSelected = selectedComponent?.id === instance.id;

    const commonClasses = `relative cursor-pointer transition-all ${
      isSelected ? 'ring-2 ring-blue-500 ring-offset-2' : 'hover:ring-2 hover:ring-gray-300'
    }`;

    const renderByType = () => {
      switch (instance.component_id) {
        case 'heading':
          const HeadingTag = (props.level || 'h2') as keyof JSX.IntrinsicElements;
          return <HeadingTag className="text-2xl font-bold">{props.text}</HeadingTag>;
        
        case 'text':
          return <p className={`text-${props.size || 'base'}`}>{props.content}</p>;
        
        case 'button':
          return (
            <button className={`px-4 py-2 rounded ${
              props.variant === 'primary' ? 'bg-black text-white' :
              props.variant === 'secondary' ? 'bg-gray-200 text-black' :
              props.variant === 'outline' ? 'border border-black' : ''
            }`}>
              {props.text}
            </button>
          );
        
        case 'input':
          return (
            <div>
              <label className="block text-sm font-medium mb-1">{props.label}</label>
              <input 
                type={props.type || 'text'} 
                placeholder={props.placeholder}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
          );
        
        case 'image':
          return (
            <div className="bg-gray-100 flex items-center justify-center p-8 rounded">
              <span className="text-gray-400">🖼️ Image: {props.alt || 'placeholder'}</span>
            </div>
          );
        
        case 'card':
          return (
            <div className={`bg-white rounded-lg p-4 shadow-${props.shadow || 'md'}`}>
              <h3 className="font-semibold">{props.title}</h3>
              <p className="text-sm text-gray-600">{props.description}</p>
            </div>
          );
        
        case 'container':
        case 'section':
        case 'row':
        case 'column':
          return (
            <div className={`min-h-[60px] border-2 border-dashed border-gray-300 p-4 rounded ${
              instance.component_id === 'row' ? 'flex gap-4' : ''
            }`}>
              <span className="text-xs text-gray-400 uppercase">{def.name}</span>
            </div>
          );
        
        case 'navbar':
          return (
            <nav className="bg-white border-b p-4 flex justify-between items-center">
              <span className="font-bold">{props.logo}</span>
              <div className="flex gap-4 text-sm">
                {props.links?.split(',').map((link: string, i: number) => (
                  <a key={i} href="#" className="hover:text-gray-600">{link.trim()}</a>
                ))}
              </div>
            </nav>
          );
        
        case 'footer':
          return (
            <footer className="bg-gray-100 p-4 text-center text-sm text-gray-600">
              {props.copyright}
            </footer>
          );
        
        case 'divider':
          return <hr className="border-gray-200 my-4" />;
        
        default:
          return <div className="p-4 bg-gray-50 rounded">{def.name}</div>;
      }
    };

    return (
      <div
        key={instance.id}
        className={commonClasses}
        onClick={() => setSelectedComponent(instance)}
      >
        {renderByType()}
        {isSelected && (
          <div className="absolute -top-8 right-0 flex gap-1">
            <button
              onClick={(e) => { e.stopPropagation(); moveComponent(instance.id, 'up'); }}
              className="p-1 bg-gray-800 text-white rounded text-xs"
            >
              ↑
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); moveComponent(instance.id, 'down'); }}
              className="p-1 bg-gray-800 text-white rounded text-xs"
            >
              ↓
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); removeFromCanvas(instance.id); }}
              className="p-1 bg-red-500 text-white rounded text-xs"
            >
              ✕
            </button>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700">
            ← Back
          </Link>
          <h1 className="font-semibold">Visual Builder</h1>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 text-sm border rounded hover:bg-gray-50">
            Preview
          </button>
          <button className="px-3 py-1.5 text-sm bg-black text-white rounded hover:bg-gray-800">
            Export Code
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Components */}
        <div className="w-64 bg-white border-r overflow-y-auto">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-sm">Components</h2>
          </div>
          
          {/* Category Tabs */}
          <div className="flex flex-wrap gap-1 p-2 border-b">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-2 py-1 text-xs rounded capitalize ${
                  selectedCategory === cat 
                    ? 'bg-black text-white' 
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Component List */}
          <div className="p-2 space-y-1">
            {filteredComponents.map(comp => (
              <button
                key={comp.id}
                onClick={() => addToCanvas(comp)}
                className="w-full flex items-center gap-2 p-2 text-left text-sm rounded hover:bg-gray-100 transition-colors"
              >
                <span>{CATEGORY_ICONS[comp.category] || '📦'}</span>
                <span>{comp.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg min-h-[600px] p-4">
            {canvas.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <p className="text-4xl mb-2">🎨</p>
                  <p>Click components from the sidebar to add them here</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {canvas.map(instance => renderComponent(instance))}
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar - Properties */}
        <div className="w-72 bg-white border-l overflow-y-auto">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-sm">Properties</h2>
          </div>
          
          {selectedComponent ? (
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Component</label>
                <p className="text-sm font-medium capitalize">
                  {components.find(c => c.id === selectedComponent.component_id)?.name}
                </p>
              </div>
              
              {components
                .find(c => c.id === selectedComponent.component_id)
                ?.properties.map(prop => (
                  <div key={prop.name}>
                    <label className="block text-xs font-medium text-gray-500 mb-1 capitalize">
                      {prop.name.replace(/_/g, ' ')}
                    </label>
                    
                    {prop.type === 'select' && prop.options ? (
                      <select
                        value={selectedComponent.properties[prop.name] || prop.default}
                        onChange={(e) => updateComponentProperty(selectedComponent.id, prop.name, e.target.value)}
                        className="w-full px-2 py-1.5 text-sm border rounded"
                      >
                        {prop.options.map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    ) : prop.type === 'boolean' ? (
                      <input
                        type="checkbox"
                        checked={selectedComponent.properties[prop.name] || false}
                        onChange={(e) => updateComponentProperty(selectedComponent.id, prop.name, e.target.checked)}
                        className="rounded"
                      />
                    ) : prop.type === 'number' ? (
                      <input
                        type="number"
                        value={selectedComponent.properties[prop.name] || prop.default || 0}
                        onChange={(e) => updateComponentProperty(selectedComponent.id, prop.name, parseInt(e.target.value))}
                        className="w-full px-2 py-1.5 text-sm border rounded"
                      />
                    ) : prop.type === 'color' ? (
                      <input
                        type="color"
                        value={selectedComponent.properties[prop.name] || prop.default || '#000000'}
                        onChange={(e) => updateComponentProperty(selectedComponent.id, prop.name, e.target.value)}
                        className="w-full h-8 rounded cursor-pointer"
                      />
                    ) : (
                      <input
                        type="text"
                        value={selectedComponent.properties[prop.name] || ''}
                        onChange={(e) => updateComponentProperty(selectedComponent.id, prop.name, e.target.value)}
                        className="w-full px-2 py-1.5 text-sm border rounded"
                        placeholder={prop.default?.toString()}
                      />
                    )}
                  </div>
                ))}
            </div>
          ) : (
            <div className="p-4 text-center text-gray-400 text-sm">
              Select a component to edit its properties
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
