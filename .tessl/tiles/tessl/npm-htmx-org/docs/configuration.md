# Configuration

Global configuration object controlling all aspects of htmx behavior including defaults, timeouts, CSS classes, security settings, and request handling options.

## Capabilities

### Configuration Object

The main configuration object containing all htmx runtime settings.

```javascript { .api }
// Main configuration object
const config: {
  // History & Navigation
  historyEnabled: boolean;
  historyCacheSize: number;
  refreshOnHistoryMiss: boolean;
  scrollIntoViewOnBoost: boolean;
  historyRestoreAsHxRequest: boolean;
  
  // Swap Behavior  
  defaultSwapStyle: HtmxSwapStyle;
  defaultSwapDelay: number;
  defaultSettleDelay: number;
  globalViewTransitions: boolean;
  allowNestedOobSwaps: boolean;
  
  // CSS Classes
  includeIndicatorStyles: boolean;
  indicatorClass: string;
  requestClass: string;
  addedClass: string;
  settlingClass: string;
  swappingClass: string;
  
  // Security & Evaluation
  allowEval: boolean;
  allowScriptTags: boolean;
  inlineScriptNonce: string;
  inlineStyleNonce: string;
  selfRequestsOnly: boolean;
  
  // Form & Request Handling
  attributesToSettle: string[];
  withCredentials: boolean;
  timeout: number;
  methodsThatUseUrlParams: HttpVerb[];
  getCacheBusterParam: boolean;
  
  // WebSocket Configuration
  wsReconnectDelay: string | function;
  wsBinaryType: BinaryType;
  
  // Element Selection & Behavior
  disableSelector: string;
  scrollBehavior: string;
  defaultFocusScroll: boolean;
  ignoreTitle: boolean;
  disableInheritance: boolean;
  
  // Advanced Configuration
  triggerSpecsCache: Object | null;
  responseHandling: HtmxResponseHandlingConfig[];
};

type HtmxSwapStyle = "innerHTML" | "outerHTML" | "beforebegin" | "afterbegin" | "beforeend" | "afterend" | "delete" | "none" | string;
type HttpVerb = "get" | "head" | "post" | "put" | "delete" | "connect" | "options" | "trace" | "patch";
type BinaryType = "blob" | "arraybuffer";

interface HtmxResponseHandlingConfig {
  code?: string;
  swap: boolean;
  error?: boolean;
  ignoreTitle?: boolean;
  select?: string;
  target?: string;
  swapOverride?: string;
  event?: string;
}
```

## Configuration Categories

### History & Navigation

Controls browser history management and navigation behavior.

```javascript { .api }
// History configuration
htmx.config.historyEnabled = true; // Enable/disable history support
htmx.config.historyCacheSize = 10; // Number of pages cached in sessionStorage
htmx.config.refreshOnHistoryMiss = false; // Refresh page if history cache miss
htmx.config.scrollIntoViewOnBoost = true; // Scroll boosted elements into view
htmx.config.historyRestoreAsHxRequest = true; // Treat history restore as HX-Request
```

**Usage Examples:**

```javascript
// Disable history for SPA-like behavior
htmx.config.historyEnabled = false;

// Increase history cache for better back/forward navigation
htmx.config.historyCacheSize = 20;

// Force page refresh when history cache is missed
htmx.config.refreshOnHistoryMiss = true;

// Custom history handling
htmx.on('htmx:pushedIntoHistory', function(evt) {
  console.log('Pushed URL to history:', evt.detail.path);
  // Custom analytics tracking
  analytics.track('page_view', { path: evt.detail.path });
});

htmx.on('htmx:replacedInHistory', function(evt) {
  console.log('Replaced URL in history:', evt.detail.path);
});
```

### Swap Behavior

Controls how content is swapped and timing of swap operations.

```javascript { .api }
// Swap configuration
htmx.config.defaultSwapStyle = 'innerHTML'; // Default swap style
htmx.config.defaultSwapDelay = 0; // Delay before swap (ms)
htmx.config.defaultSettleDelay = 20; // Delay before settle (ms)
htmx.config.globalViewTransitions = false; // Use View Transition API
htmx.config.allowNestedOobSwaps = true; // Process nested out-of-band swaps
```

**Usage Examples:**

```javascript
// Change default swap behavior
htmx.config.defaultSwapStyle = 'outerHTML';

// Add delays for smoother animations
htmx.config.defaultSwapDelay = 100;
htmx.config.defaultSettleDelay = 50;

// Enable View Transitions API for modern browsers
if ('startViewTransition' in document) {
  htmx.config.globalViewTransitions = true;
}

// Custom swap timing based on content type
htmx.on('htmx:beforeSwap', function(evt) {
  const contentLength = evt.detail.xhr.responseText.length;
  
  if (contentLength > 10000) {
    // Longer delays for large content
    evt.detail.shouldSwap = true;
    evt.detail.target.style.transition = 'opacity 0.5s';
  }
});
```

### CSS Classes

Controls CSS classes applied during various htmx operations.

```javascript { .api }
// CSS class configuration
htmx.config.includeIndicatorStyles = true; // Inject default indicator styles
htmx.config.indicatorClass = 'htmx-indicator'; // Loading indicator class
htmx.config.requestClass = 'htmx-request'; // Class during requests
htmx.config.addedClass = 'htmx-added'; // Class for newly added elements
htmx.config.settlingClass = 'htmx-settling'; // Class during settling
htmx.config.swappingClass = 'htmx-swapping'; // Class during swapping
```

**Usage Examples:**

```javascript
// Custom CSS classes for branding
htmx.config.indicatorClass = 'my-app-loading';
htmx.config.requestClass = 'my-app-requesting';
htmx.config.addedClass = 'my-app-new-content';

// Disable built-in indicator styles to use custom ones
htmx.config.includeIndicatorStyles = false;

// Dynamic class configuration based on theme
function updateHtmxClasses(theme) {
  htmx.config.indicatorClass = `${theme}-loading`;
  htmx.config.requestClass = `${theme}-requesting`;
  htmx.config.addedClass = `${theme}-new-content`;
}

// Apply theme-specific classes
updateHtmxClasses(getCurrentTheme());

// CSS for custom classes
/*
.my-app-loading {
  opacity: 0.6;
  pointer-events: none;
}

.my-app-requesting {
  cursor: wait;
}

.my-app-new-content {
  animation: slideIn 0.3s ease-out;
}
*/
```

### Security & Evaluation

Controls security-related features and code evaluation.

```javascript { .api }
// Security configuration
htmx.config.allowEval = true; // Allow eval-like functionality
htmx.config.allowScriptTags = true; // Interpret script tags in responses
htmx.config.inlineScriptNonce = ''; // Nonce for inline scripts  
htmx.config.inlineStyleNonce = ''; // Nonce for inline styles
htmx.config.selfRequestsOnly = true; // Disable non-origin requests
```

**Usage Examples:**

```javascript
// High security setup
htmx.config.allowEval = false; // Disable eval functionality
htmx.config.allowScriptTags = false; // Don't execute scripts in responses
htmx.config.selfRequestsOnly = true; // Only allow same-origin requests

// CSP nonce support
htmx.config.inlineScriptNonce = document.querySelector('meta[name="csp-nonce"]')?.content || '';
htmx.config.inlineStyleNonce = htmx.config.inlineScriptNonce;

// Development vs production security
if (process.env.NODE_ENV === 'development') {
  htmx.config.allowEval = true;
  htmx.config.allowScriptTags = true;
} else {
  htmx.config.allowEval = false;
  htmx.config.allowScriptTags = false;
}

// Custom security validation
htmx.on('htmx:beforeRequest', function(evt) {
  const url = new URL(evt.detail.path, window.location.origin);
  
  // Block requests to external domains in production
  if (htmx.config.selfRequestsOnly && url.origin !== window.location.origin) {
    console.warn('Blocked external request:', url.href);
    evt.preventDefault();
    return false;
  }
});
```

### Request Handling

Controls form data handling, request timeouts, and parameter encoding.

```javascript { .api }
// Request handling configuration
htmx.config.attributesToSettle = ['class', 'style', 'width', 'height']; // Attributes to settle
htmx.config.withCredentials = false; // Send credentials with requests
htmx.config.timeout = 0; // Request timeout (0 = no timeout)
htmx.config.methodsThatUseUrlParams = ['get', 'delete']; // Methods using URL params
htmx.config.getCacheBusterParam = false; // Add cache-busting parameter
```

**Usage Examples:**

```javascript
// Global timeout for all requests
htmx.config.timeout = 30000; // 30 seconds

// Include credentials for cross-origin requests
htmx.config.withCredentials = true;

// Add cache busting for GET requests
htmx.config.getCacheBusterParam = true;

// Settle additional attributes for animations
htmx.config.attributesToSettle = [
  'class', 'style', 'width', 'height', 
  'data-state', 'aria-expanded'
];

// Custom parameter encoding for different methods
htmx.config.methodsThatUseUrlParams = ['get', 'delete', 'head'];

// Per-request timeout override
htmx.on('htmx:configRequest', function(evt) {
  if (evt.detail.path.includes('/slow-endpoint')) {
    evt.detail.timeout = 60000; // 60 seconds for slow endpoints
  }
});
```

### WebSocket Configuration

Controls WebSocket connection behavior and reconnection strategy.

```javascript { .api }
// WebSocket configuration
htmx.config.wsReconnectDelay = 'full-jitter'; // Reconnection delay strategy
htmx.config.wsBinaryType = 'blob'; // Binary data type for WebSocket
```

**Usage Examples:**

```javascript
// Custom reconnection delay function
htmx.config.wsReconnectDelay = function(retryCount) {
  // Exponential backoff with max delay
  return Math.min(1000 * Math.pow(2, retryCount), 30000);
};

// Fixed delay reconnection
htmx.config.wsReconnectDelay = '5s';

// Use ArrayBuffer for binary WebSocket data
htmx.config.wsBinaryType = 'arraybuffer';

// WebSocket event handling
htmx.on('htmx:wsConnecting', function(evt) {
  console.log('WebSocket connecting...');
  showConnectionStatus('connecting');
});

htmx.on('htmx:wsOpen', function(evt) {
  console.log('WebSocket connected');
  showConnectionStatus('connected');
});

htmx.on('htmx:wsClose', function(evt) {
  console.log('WebSocket disconnected');
  showConnectionStatus('disconnected');
});
```

### Element Selection & Behavior

Controls element selection, scrolling, and inheritance behavior.

```javascript { .api }
// Element behavior configuration
htmx.config.disableSelector = '[hx-disable], [data-hx-disable]'; // Selector for disabled elements
htmx.config.scrollBehavior = 'instant'; // Scroll behavior
htmx.config.defaultFocusScroll = false; // Whether focused elements scroll into view
htmx.config.ignoreTitle = false; // Whether to ignore title updates
htmx.config.disableInheritance = false; // Whether to disable attribute inheritance
```

**Usage Examples:**

```javascript
// Custom disable selector
htmx.config.disableSelector = '[disabled], .htmx-disabled, [aria-disabled="true"]';

// Smooth scrolling
htmx.config.scrollBehavior = 'smooth';

// Enable focus scrolling by default
htmx.config.defaultFocusScroll = true;

// Ignore title updates for SPA behavior
htmx.config.ignoreTitle = true;

// Disable attribute inheritance for isolated components
htmx.config.disableInheritance = true;

// Dynamic behavior based on user preferences
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  htmx.config.scrollBehavior = 'instant';
  htmx.config.defaultSwapDelay = 0;
  htmx.config.defaultSettleDelay = 0;
}
```

### Response Handling

Advanced response handling configuration for different HTTP status codes.

```javascript { .api }
// Response handling configuration array
htmx.config.responseHandling = [
  { code: '204', swap: false }, // No Content - don't swap
  { code: '422', swap: true, error: false }, // Validation errors - swap but not error
  { code: '500', swap: true, error: true, target: '#error-container' }
];
```

**Usage Examples:**

```javascript
// Custom response handling rules
htmx.config.responseHandling = [
  // Handle 204 No Content
  { code: '204', swap: false },
  
  // Handle 422 Validation Errors
  { code: '422', swap: true, error: false, target: '#validation-errors' },
  
  // Handle 401 Unauthorized
  { code: '401', swap: false, event: 'unauthorized' },
  
  // Handle 403 Forbidden
  { code: '403', swap: true, target: '#access-denied', swapOverride: 'innerHTML' },
  
  // Handle 500 Server Error
  { code: '500', swap: true, error: true, target: '#error-display' },
  
  // Handle 503 Service Unavailable
  { code: '503', swap: true, target: '#maintenance-mode' }
];

// Listen for custom events
htmx.on('unauthorized', function(evt) {
  // Redirect to login
  window.location.href = '/login?return=' + encodeURIComponent(window.location.pathname);
});

// Handle validation errors differently
htmx.on('htmx:responseError', function(evt) {
  if (evt.detail.xhr.status === 422) {
    const errors = JSON.parse(evt.detail.xhr.responseText);
    displayValidationErrors(errors);
    evt.preventDefault(); // Prevent default error handling
  }
});
```

## Configuration Best Practices

### Environment-Specific Configuration

```javascript
// Configuration based on environment
function configureHtmx() {
  const isDevelopment = process.env.NODE_ENV === 'development';
  const isProduction = process.env.NODE_ENV === 'production';
  const isTesting = process.env.NODE_ENV === 'test';
  
  if (isDevelopment) {
    // Development configuration
    htmx.config.allowEval = true;
    htmx.config.allowScriptTags = true;
    htmx.config.timeout = 10000;
    
    // Enable debug logging
    htmx.logAll();
  } else if (isProduction) {
    // Production configuration
    htmx.config.allowEval = false;
    htmx.config.allowScriptTags = false;
    htmx.config.selfRequestsOnly = true;
    htmx.config.timeout = 30000;
    
    // Disable logging
    htmx.logNone();
  } else if (isTesting) {
    // Testing configuration
    htmx.config.historyEnabled = false;
    htmx.config.defaultSwapDelay = 0;
    htmx.config.defaultSettleDelay = 0;
  }
}

configureHtmx();
```

### Dynamic Configuration

```javascript
// Configuration that adapts to runtime conditions
function adaptiveConfiguration() {
  // Adjust timeouts based on connection speed
  if (navigator.connection) {
    const effectiveType = navigator.connection.effectiveType;
    
    switch (effectiveType) {
      case 'slow-2g':
      case '2g':
        htmx.config.timeout = 60000; // 60 seconds for slow connections
        break;
      case '3g':
        htmx.config.timeout = 30000; // 30 seconds for 3G
        break;
      case '4g':
        htmx.config.timeout = 15000; // 15 seconds for 4G
        break;
    }
  }
  
  // Adjust behavior based on device capabilities
  if (window.matchMedia('(hover: none)').matches) {
    // Touch device - disable hover-triggered requests
    htmx.config.disableSelector += ', [hx-trigger*="mouseenter"]';
  }
  
  // Adjust for reduced motion preference
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    htmx.config.defaultSwapDelay = 0;
    htmx.config.defaultSettleDelay = 0;
    htmx.config.globalViewTransitions = false;
  }
}

adaptiveConfiguration();

// Re-evaluate configuration on network changes
if (navigator.connection) {
  navigator.connection.addEventListener('change', adaptiveConfiguration);
}
```

### Configuration Validation

```javascript
// Validate configuration settings
function validateConfiguration() {
  const config = htmx.config;
  const warnings = [];
  
  // Check for potentially problematic settings
  if (config.allowEval && config.allowScriptTags && location.protocol === 'https:') {
    warnings.push('Both allowEval and allowScriptTags are enabled in production');
  }
  
  if (config.timeout === 0) {
    warnings.push('Request timeout is disabled - requests may hang indefinitely');
  }
  
  if (config.historyCacheSize > 50) {
    warnings.push('Large history cache size may impact memory usage');
  }
  
  if (!config.selfRequestsOnly && location.protocol === 'https:') {
    warnings.push('Cross-origin requests are enabled in production');
  }
  
  // Log warnings
  warnings.forEach(warning => {
    console.warn('HTMX Configuration Warning:', warning);
  });
  
  return warnings.length === 0;
}

// Validate configuration after setup
document.addEventListener('DOMContentLoaded', validateConfiguration);
```

### Meta Tag Configuration

```html
<!-- Configure htmx via meta tags -->
<meta name="htmx-config" content='{"timeout": 30000, "defaultSwapStyle": "outerHTML"}'>
<meta name="htmx-csp-nonce" content="random-nonce-value">
<meta name="htmx-base-url" content="/api/v1">
```

```javascript
// Apply meta tag configuration
function applyMetaConfiguration() {
  const configMeta = document.querySelector('meta[name="htmx-config"]');
  if (configMeta) {
    try {
      const config = JSON.parse(configMeta.content);
      Object.assign(htmx.config, config);
    } catch (e) {
      console.error('Invalid htmx configuration in meta tag:', e);
    }
  }
  
  // Apply CSP nonce
  const nonceMeta = document.querySelector('meta[name="htmx-csp-nonce"]');
  if (nonceMeta) {
    htmx.config.inlineScriptNonce = nonceMeta.content;
    htmx.config.inlineStyleNonce = nonceMeta.content;
  }
}

applyMetaConfiguration();
```