# Debugging & Utilities

Tools for debugging htmx behavior, utility functions for common operations, and development helpers for building htmx applications.

## Capabilities

### Debug Logging

Control htmx's built-in logging system for debugging and development.

```javascript { .api }
/**
 * Enables logging of all htmx events (useful for debugging)
 */
function logAll(): void;

/**
 * Disables htmx event logging
 */
function logNone(): void;

/**
 * Custom logger for htmx events
 * Set to null to use console.log, or provide custom logging function
 */
let logger: any;
```

**Usage Examples:**

```javascript
// Enable all logging
htmx.logAll();

// Disable logging
htmx.logNone();

// Custom logger implementation
htmx.logger = function(elt, event, data) {
  // Custom logging format
  console.group(`🔧 HTMX: ${event}`);
  console.log('Element:', elt);
  console.log('Data:', data);
  console.groupEnd();
  
  // Send to analytics service
  if (window.analytics && event.startsWith('htmx:')) {
    analytics.track('htmx_event', {
      event: event,
      element: elt.tagName,
      timestamp: Date.now()
    });
  }
};

// Conditional logging based on environment
if (process.env.NODE_ENV === 'development') {
  htmx.logAll();
} else {
  htmx.logNone();
}

// Log only specific events
const originalLogger = htmx.logger;
htmx.logger = function(elt, event, data) {
  // Only log errors and important events
  if (event.includes('Error') || event.includes('failed') || event === 'htmx:responseError') {
    originalLogger.call(this, elt, event, data);
  }
};
```

### Utility Functions

Helper functions for common operations and data processing.

```javascript { .api }
/**
 * Parses an interval string consistent with htmx timing specifications
 * @param str - Timing string (e.g., "1s", "500ms", "2.5s")
 * @returns Number in milliseconds or undefined if invalid
 */
function parseInterval(str: string): number | undefined;
```

**Usage Examples:**

```javascript
// Parse timing strings
const delay1 = htmx.parseInterval('1s');        // 1000
const delay2 = htmx.parseInterval('500ms');     // 500
const delay3 = htmx.parseInterval('2.5s');      // 2500
const delay4 = htmx.parseInterval('invalid');    // undefined

// Use in dynamic timing
function setDynamicDelay(element, delayString) {
  const delay = htmx.parseInterval(delayString);
  if (delay !== undefined) {
    element.style.animationDelay = `${delay}ms`;
  }
}

// Parse timing from HTML attributes
document.querySelectorAll('[data-delay]').forEach(el => {
  const delayString = el.getAttribute('data-delay');
  const delay = htmx.parseInterval(delayString);
  
  if (delay !== undefined) {
    setTimeout(() => {
      el.classList.add('delayed-action');
    }, delay);
  }
});

// Validate timing configurations
function validateTimingConfig(config) {
  const validatedConfig = {};
  
  for (const [key, value] of Object.entries(config)) {
    if (typeof value === 'string') {
      const parsed = htmx.parseInterval(value);
      validatedConfig[key] = parsed !== undefined ? parsed : 0;
    } else {
      validatedConfig[key] = value;
    }
  }
  
  return validatedConfig;
}

const config = validateTimingConfig({
  swapDelay: '100ms',
  settleDelay: '20ms',
  timeout: '30s'
});
```

### Version Information

Access to htmx version information for compatibility checks and debugging.

```javascript { .api }
/**
 * Current htmx version string
 */
const version: string; // "2.0.6"
```

**Usage Examples:**

```javascript
// Check htmx version
console.log('HTMX Version:', htmx.version);

// Version comparison utility
function compareVersions(version1, version2) {
  const v1parts = version1.split('.').map(Number);
  const v2parts = version2.split('.').map(Number);
  
  for (let i = 0; i < Math.max(v1parts.length, v2parts.length); i++) {
    const v1part = v1parts[i] || 0;
    const v2part = v2parts[i] || 0;
    
    if (v1part > v2part) return 1;
    if (v1part < v2part) return -1;
  }
  
  return 0;
}

// Feature detection based on version
function supportsFeature(feature) {
  const currentVersion = htmx.version;
  
  const featureVersions = {
    'view-transitions': '2.0.0',
    'websockets': '1.6.0',
    'extensions': '1.0.0'
  };
  
  const requiredVersion = featureVersions[feature];
  if (!requiredVersion) return false;
  
  return compareVersions(currentVersion, requiredVersion) >= 0;
}

// Conditional feature usage
if (supportsFeature('view-transitions')) {
  htmx.config.globalViewTransitions = true;
}

// Report version info for support
function getDebugInfo() {
  return {
    htmxVersion: htmx.version,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    config: htmx.config
  };
}
```

### Location Proxy

Access to location-related utilities for navigation and URL handling.

```javascript { .api }
/**
 * Proxy of window.location used for page reload functions
 */
const location: Location;
```

**Usage Examples:**

```javascript
// Access current location
console.log('Current URL:', htmx.location.href);
console.log('Current path:', htmx.location.pathname);

// Navigation utilities
function navigateTo(url) {
  htmx.location.href = url;
}

function reloadPage() {
  htmx.location.reload();
}

// URL manipulation
function updateURL(path, replaceState = false) {
  if (replaceState) {
    history.replaceState(null, '', path);
  } else {
    history.pushState(null, '', path);
  }
}

// Check if URL is same origin
function isSameOrigin(url) {
  try {
    const urlObj = new URL(url, htmx.location.origin);
    return urlObj.origin === htmx.location.origin;
  } catch (e) {
    return false;
  }
}
```

## Development Tools

### Debug Panel

Create a debug panel for development and testing.

```javascript
// Create debug panel
function createDebugPanel() {
  const panel = document.createElement('div');
  panel.id = 'htmx-debug-panel';
  panel.style.cssText = `
    position: fixed;
    bottom: 10px;
    right: 10px;
    width: 300px;
    max-height: 400px;
    background: #333;
    color: #fff;
    padding: 10px;
    border-radius: 5px;
    font-family: monospace;
    font-size: 12px;
    overflow-y: auto;
    z-index: 10000;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  `;
  
  const header = document.createElement('h3');
  header.textContent = `HTMX Debug (v${htmx.version})`;
  header.style.margin = '0 0 10px 0';
  panel.appendChild(header);
  
  const logContainer = document.createElement('div');
  logContainer.id = 'htmx-debug-log';
  panel.appendChild(logContainer);
  
  const controls = document.createElement('div');
  controls.style.marginTop = '10px';
  
  const clearBtn = document.createElement('button');
  clearBtn.textContent = 'Clear';
  clearBtn.onclick = () => logContainer.innerHTML = '';
  controls.appendChild(clearBtn);
  
  const toggleBtn = document.createElement('button');
  toggleBtn.textContent = 'Toggle Logging';
  toggleBtn.onclick = toggleLogging;
  controls.appendChild(toggleBtn);
  
  panel.appendChild(controls);
  document.body.appendChild(panel);
  
  return { panel, logContainer };
}

let debugPanel = null;
let loggingEnabled = false;

function toggleLogging() {
  if (loggingEnabled) {
    htmx.logNone();
    loggingEnabled = false;
  } else {
    htmx.logAll();
    loggingEnabled = true;
  }
}

// Initialize debug panel
if (process.env.NODE_ENV === 'development') {
  document.addEventListener('DOMContentLoaded', () => {
    debugPanel = createDebugPanel();
    
    // Custom logger for debug panel
    const originalLogger = console.log;
    htmx.logger = function(elt, event, data) {
      if (debugPanel) {
        const logEntry = document.createElement('div');
        logEntry.style.borderBottom = '1px solid #555';
        logEntry.style.padding = '5px 0';
        logEntry.innerHTML = `
          <strong>${event}</strong><br>
          Element: ${elt.tagName}${elt.id ? '#' + elt.id : ''}<br>
          Time: ${new Date().toLocaleTimeString()}
        `;
        
        debugPanel.logContainer.appendChild(logEntry);
        debugPanel.logContainer.scrollTop = debugPanel.logContainer.scrollHeight;
      }
      
      originalLogger.call(console, 'HTMX:', event, elt, data);
    };
  });
}
```

### Performance Monitoring

Monitor htmx performance and request timing.

```javascript
// Performance monitoring
const HtmxPerformanceMonitor = {
  requests: [],
  startTimes: new Map(),
  
  init() {
    htmx.on('htmx:beforeRequest', (evt) => {
      const requestId = this.generateRequestId(evt);
      this.startTimes.set(requestId, performance.now());
    });
    
    htmx.on('htmx:afterRequest', (evt) => {
      const requestId = this.generateRequestId(evt);
      const startTime = this.startTimes.get(requestId);
      
      if (startTime) {
        const duration = performance.now() - startTime;
        this.recordRequest({
          url: evt.detail.requestConfig.path,
          method: evt.detail.requestConfig.verb,
          duration: duration,
          status: evt.detail.xhr.status,
          size: evt.detail.xhr.responseText.length,
          timestamp: Date.now(),
          successful: evt.detail.successful
        });
        
        this.startTimes.delete(requestId);
      }
    });
  },
  
  generateRequestId(evt) {
    return `${evt.detail.requestConfig.verb}-${evt.detail.requestConfig.path}-${Date.now()}`;
  },
  
  recordRequest(requestInfo) {
    this.requests.push(requestInfo);
    
    // Keep only last 100 requests
    if (this.requests.length > 100) {
      this.requests.shift();
    }
    
    // Log slow requests
    if (requestInfo.duration > 2000) {
      console.warn('Slow HTMX request:', requestInfo);
    }
  },
  
  getStats() {
    if (this.requests.length === 0) return null;
    
    const durations = this.requests.map(r => r.duration);
    const sizes = this.requests.map(r => r.size);
    
    return {
      totalRequests: this.requests.length,
      averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
      maxDuration: Math.max(...durations),
      minDuration: Math.min(...durations),
      averageSize: sizes.reduce((a, b) => a + b, 0) / sizes.length,
      errorRate: this.requests.filter(r => !r.successful).length / this.requests.length,
      slowRequests: this.requests.filter(r => r.duration > 2000).length
    };
  },
  
  exportData() {
    return {
      stats: this.getStats(),
      requests: this.requests,
      config: htmx.config,
      version: htmx.version,
      timestamp: new Date().toISOString()
    };
  }
};

// Initialize monitoring in development
if (process.env.NODE_ENV === 'development') {
  HtmxPerformanceMonitor.init();
  
  // Global access for debugging
  window.htmxStats = HtmxPerformanceMonitor;
}
```

### Testing Utilities

Utilities for testing htmx applications.

```javascript
// Testing utilities
const HtmxTestUtils = {
  // Wait for htmx requests to complete
  async waitForRequests(timeout = 5000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      // Check if any requests are in flight
      const activeRequests = document.querySelectorAll('.htmx-request');
      if (activeRequests.length === 0) {
        return true;
      }
      
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    throw new Error('Timeout waiting for HTMX requests to complete');
  },
  
  // Trigger htmx event and wait for completion
  async triggerAndWait(element, event, detail = {}) {
    const promise = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Timeout waiting for htmx event'));
      }, 5000);
      
      const handler = () => {
        clearTimeout(timeout);
        htmx.off('htmx:afterRequest', handler);
        resolve();
      };
      
      htmx.on('htmx:afterRequest', handler);
    });
    
    htmx.trigger(element, event, detail);
    return promise;
  },
  
  // Mock htmx responses for testing
  mockResponse(url, responseText, status = 200) {
    const originalAjax = htmx.ajax;
    
    htmx.ajax = function(method, path, context) {
      if (path === url) {
        // Create mock response
        setTimeout(() => {
          const mockEvent = new CustomEvent('htmx:afterRequest', {
            detail: {
              xhr: {
                status: status,
                responseText: responseText,
                getResponseHeader: () => 'text/html'
              },
              successful: status < 400,
              target: typeof context === 'string' ? document.querySelector(context) : context
            }
          });
          
          document.dispatchEvent(mockEvent);
        }, 10);
        
        return Promise.resolve();
      }
      
      return originalAjax.call(this, method, path, context);
    };
    
    // Return cleanup function
    return () => {
      htmx.ajax = originalAjax;
    };
  },
  
  // Get current htmx state
  getState() {
    return {
      activeRequests: document.querySelectorAll('.htmx-request').length,
      indicators: document.querySelectorAll('.htmx-indicator').length,
      config: htmx.config,
      version: htmx.version
    };
  }
};

// Example test usage
/*
// In Jest or similar testing framework
test('htmx request updates content', async () => {
  const cleanup = HtmxTestUtils.mockResponse('/api/data', '<div>New Content</div>');
  
  const button = document.querySelector('#load-button');
  await HtmxTestUtils.triggerAndWait(button, 'click');
  
  expect(document.querySelector('#content').textContent).toBe('New Content');
  
  cleanup();
});
*/
```

### Development Configuration

Helpful configurations for development environments.

```javascript
// Development-specific configuration
function setupDevelopmentEnvironment() {
  // Enable comprehensive logging
  htmx.logAll();
  
  // Add request timing
  htmx.on('htmx:beforeRequest', (evt) => {
    evt.detail.requestStart = performance.now();
  });
  
  htmx.on('htmx:afterRequest', (evt) => {
    if (evt.detail.requestStart) {
      const duration = performance.now() - evt.detail.requestStart;
      console.log(`Request to ${evt.detail.requestConfig.path} took ${duration.toFixed(2)}ms`);
    }
  });
  
  // Highlight htmx elements
  const style = document.createElement('style');
  style.textContent = `
    [hx-get], [hx-post], [hx-put], [hx-patch], [hx-delete] {
      outline: 1px dashed #007bff !important;
      outline-offset: 2px !important;
    }
    
    .htmx-request {
      background-color: rgba(255, 193, 7, 0.2) !important;
    }
    
    .htmx-indicator {
      border: 1px solid #dc3545 !important;
    }
  `;
  document.head.appendChild(style);
  
  // Global error handler
  window.addEventListener('error', (evt) => {
    console.error('Global error:', evt.error);
  });
  
  // Expose utilities globally
  window.htmxTestUtils = HtmxTestUtils;
  
  console.log('🔧 HTMX development environment initialized');
}

// Auto-initialize in development
if (process.env.NODE_ENV === 'development' || 
    window.location.hostname === 'localhost' ||
    window.location.hostname.endsWith('.local')) {
  document.addEventListener('DOMContentLoaded', setupDevelopmentEnvironment);
}
```