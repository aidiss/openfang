# Extension System

Plugin architecture for extending htmx functionality with custom behaviors, integrations, and advanced features through a comprehensive extension API.

## Capabilities

### Extension Registration

Register and manage htmx extensions to extend core functionality.

```javascript { .api }
/**
 * Initializes and registers an extension
 * @param name - Extension name for reference and activation
 * @param extension - Extension definition object implementing HtmxExtension interface
 */
function defineExtension(name: string, extension: Partial<HtmxExtension>): void;

/**
 * Removes an extension from the registry
 * @param name - Extension name to remove
 */
function removeExtension(name: string): void;
```

**Basic Extension Example:**

```javascript
// Simple logging extension
htmx.defineExtension('logger', {
  onEvent: function(name, evt) {
    console.log('HTMX Event:', name, evt.detail);
    return true; // Continue processing
  }
});

// Activate extension in HTML
// <div hx-ext="logger">Content with logging enabled</div>

// Remove extension
htmx.removeExtension('logger');
```

### Extension Interface

Complete extension interface for implementing sophisticated extensions.

```javascript { .api }
interface HtmxExtension {
  /**
   * Initialize extension with htmx internal API
   * @param api - htmx internal API object
   */
  init: (api: any) => void;
  
  /**
   * Handle htmx events before core processing
   * @param name - Event name
   * @param event - Custom event object
   * @returns boolean - true to continue processing, false to stop
   */
  onEvent: (name: string, event: CustomEvent) => boolean;
  
  /**
   * Transform response text before processing
   * @param text - Original response text
   * @param xhr - XMLHttpRequest object
   * @param elt - Triggering element
   * @returns Modified response text
   */
  transformResponse: (text: string, xhr: XMLHttpRequest, elt: Element) => string;
  
  /**
   * Determine if swap style should be handled inline
   * @param swapStyle - Swap style string
   * @returns true if swap should be handled by extension
   */
  isInlineSwap: (swapStyle: HtmxSwapStyle) => boolean;
  
  /**
   * Handle custom swap operations
   * @param swapStyle - Swap style string
   * @param target - Target element for swap
   * @param fragment - Content fragment to swap
   * @param settleInfo - Settlement information
   * @returns boolean or Node array - true if handled, false to continue, or nodes to settle
   */
  handleSwap: (swapStyle: HtmxSwapStyle, target: Node, fragment: Node, settleInfo: HtmxSettleInfo) => boolean | Node[];
  
  /**
   * Encode request parameters
   * @param xhr - XMLHttpRequest object
   * @param parameters - FormData parameters
   * @param elt - Triggering element
   * @returns Encoded parameters as string, object, or null
   */
  encodeParameters: (xhr: XMLHttpRequest, parameters: FormData, elt: Node) => any | string | null;
  
  /**
   * Return CSS selectors for elements this extension should process
   * @returns Array of CSS selectors or null
   */
  getSelectors: () => string[] | null;
}

type HtmxSwapStyle = "innerHTML" | "outerHTML" | "beforebegin" | "afterbegin" | "beforeend" | "afterend" | "delete" | "none" | string;

interface HtmxSettleInfo {
  tasks: HtmxSettleTask[];
  elts: Element[];
  title?: string;
}

type HtmxSettleTask = () => void;
```

## Extension Examples

### Authentication Extension

```javascript
htmx.defineExtension('auth', {
  onEvent: function(name, evt) {
    if (name === 'htmx:configRequest') {
      const xhr = evt.detail.xhr;
      const token = localStorage.getItem('authToken');
      
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
    }
    
    if (name === 'htmx:responseError') {
      const xhr = evt.detail.xhr;
      if (xhr.status === 401) {
        // Redirect to login on authentication failure
        window.location.href = '/login';
        return false; // Stop further processing
      }
    }
    
    return true;
  }
});
```

### JSON Request Extension

```javascript
htmx.defineExtension('json-enc', {
  onEvent: function(name, evt) {
    if (name === 'htmx:configRequest') {
      const xhr = evt.detail.xhr;
      const elt = evt.detail.elt;
      
      // Check if element wants JSON encoding
      if (elt.getAttribute('hx-ext')?.includes('json-enc')) {
        xhr.setRequestHeader('Content-Type', 'application/json');
      }
    }
    return true;
  },
  
  encodeParameters: function(xhr, parameters, elt) {
    // Only encode as JSON if this extension is active
    if (elt.getAttribute('hx-ext')?.includes('json-enc')) {
      const obj = {};
      parameters.forEach((value, key) => {
        obj[key] = value;
      });
      return JSON.stringify(obj);
    }
    return null; // Let htmx handle normally
  }
});

// Usage in HTML:
// <form hx-post="/api/users" hx-ext="json-enc">
//   <input name="name" value="John">
//   <input name="email" value="john@example.com">
//   <button type="submit">Create User</button>
// </form>
```

### Loading Indicators Extension

```javascript
htmx.defineExtension('loading-states', {
  onEvent: function(name, evt) {
    const elt = evt.detail.elt;
    
    if (name === 'htmx:beforeRequest') {
      // Add loading class to triggering element
      elt.classList.add('htmx-loading');
      elt.disabled = true;
      
      // Store original text if it's a button
      if (elt.tagName === 'BUTTON') {
        elt.dataset.originalText = elt.textContent;
        elt.textContent = 'Loading...';
      }
      
      // Show loading indicator if specified
      const indicator = document.querySelector(elt.getAttribute('loading-target'));
      if (indicator) {
        indicator.style.display = 'block';
      }
    }
    
    if (name === 'htmx:afterRequest') {
      // Remove loading states
      elt.classList.remove('htmx-loading');
      elt.disabled = false;
      
      // Restore original button text
      if (elt.tagName === 'BUTTON' && elt.dataset.originalText) {
        elt.textContent = elt.dataset.originalText;
        delete elt.dataset.originalText;
      }
      
      // Hide loading indicator
      const indicator = document.querySelector(elt.getAttribute('loading-target'));
      if (indicator) {
        indicator.style.display = 'none';
      }
    }
    
    return true;
  }
});
```

### Response Transformation Extension

```javascript
htmx.defineExtension('markdown', {
  transformResponse: function(text, xhr, elt) {
    // Check if response should be processed as markdown
    const contentType = xhr.getResponseHeader('Content-Type');
    if (contentType?.includes('text/markdown') || 
        elt.getAttribute('hx-markdown') !== null) {
      
      // Convert markdown to HTML (assuming marked.js is loaded)
      if (typeof marked !== 'undefined') {
        return marked(text);
      }
    }
    
    return text; // Return unchanged if not markdown
  }
});

// Usage:
// <div hx-get="/api/readme.md" hx-ext="markdown" hx-markdown></div>
```

### Custom Swap Style Extension

```javascript
htmx.defineExtension('fade-swap', {
  isInlineSwap: function(swapStyle) {
    return swapStyle === 'fade';
  },
  
  handleSwap: function(swapStyle, target, fragment, settleInfo) {
    if (swapStyle === 'fade') {
      // Fade out current content
      target.style.transition = 'opacity 0.3s';
      target.style.opacity = '0';
      
      setTimeout(() => {
        // Replace content
        target.innerHTML = fragment.innerHTML;
        
        // Fade in new content
        target.style.opacity = '1';
        
        // Add settle tasks for new elements
        const newElements = target.querySelectorAll('*');
        newElements.forEach(el => {
          settleInfo.elts.push(el);
        });
        
        // Run settle tasks
        settleInfo.tasks.forEach(task => task());
      }, 300);
      
      return true; // Handled by extension
    }
    
    return false; // Not handled
  }
});

// Usage:
// <button hx-get="/content" hx-swap="fade" hx-target="#main">Load Content</button>
```

### Debug Extension

```javascript
htmx.defineExtension('debug', {
  init: function(api) {
    console.log('Debug extension initialized with API:', api);
    this.api = api;
  },
  
  onEvent: function(name, evt) {
    console.group(`🔧 HTMX Debug: ${name}`);
    console.log('Event:', evt);
    console.log('Detail:', evt.detail);
    console.log('Target:', evt.target);
    console.groupEnd();
    
    // Log specific event details
    if (name === 'htmx:configRequest') {
      console.table({
        Method: evt.detail.verb,
        URL: evt.detail.path,
        Headers: evt.detail.headers,
        Parameters: evt.detail.parameters
      });
    }
    
    if (name === 'htmx:afterRequest') {
      console.table({
        Status: evt.detail.xhr.status,
        'Status Text': evt.detail.xhr.statusText,
        'Response Length': evt.detail.xhr.responseText.length,
        Success: evt.detail.successful
      });
    }
    
    return true;
  },
  
  transformResponse: function(text, xhr, elt) {
    console.log('🔄 Response Transform:', {
      length: text.length,
      contentType: xhr.getResponseHeader('Content-Type'),
      element: elt
    });
    return text;
  }
});
```

### Form Validation Extension

```javascript
htmx.defineExtension('validate', {
  onEvent: function(name, evt) {
    if (name === 'htmx:beforeRequest') {
      const form = evt.detail.elt.closest('form');
      if (form && form.hasAttribute('hx-validate')) {
        
        // Clear previous errors
        form.querySelectorAll('.error').forEach(error => {
          error.remove();
        });
        
        // Validate required fields
        const requiredFields = form.querySelectorAll('[required]');
        let hasErrors = false;
        
        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            hasErrors = true;
            
            const error = document.createElement('div');
            error.className = 'error';
            error.textContent = `${field.name || 'This field'} is required`;
            field.parentNode.insertBefore(error, field.nextSibling);
          }
        });
        
        // Validate email fields
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
          if (field.value && !isValidEmail(field.value)) {
            hasErrors = true;
            
            const error = document.createElement('div');
            error.className = 'error';
            error.textContent = 'Please enter a valid email address';
            field.parentNode.insertBefore(error, field.nextSibling);
          }
        });
        
        if (hasErrors) {
          evt.preventDefault(); // Stop the request
          return false;
        }
      }
    }
    
    return true;
  }
});

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

## Advanced Extension Patterns

### Multi-Extension Coordination

```javascript
// Extension that coordinates with other extensions
htmx.defineExtension('coordinator', {
  init: function(api) {
    this.extensions = new Map();
    this.api = api;
  },
  
  registerExtension: function(name, callbacks) {
    this.extensions.set(name, callbacks);
  },
  
  onEvent: function(name, evt) {
    // Notify all registered extensions
    this.extensions.forEach((callbacks, extName) => {
      if (callbacks[name]) {
        callbacks[name](evt);
      }
    });
    
    return true;
  }
});

// Usage by other extensions
const coordinator = htmx.extensions['coordinator'];
if (coordinator) {
  coordinator.registerExtension('myExtension', {
    'htmx:beforeRequest': function(evt) {
      console.log('My extension handling beforeRequest');
    }
  });
}
```

### Configuration-Aware Extensions

```javascript
htmx.defineExtension('configurable', {
  init: function(api) {
    // Read configuration from meta tags or global config
    this.config = {
      timeout: parseInt(document.querySelector('meta[name="htmx-timeout"]')?.content) || 5000,
      retries: parseInt(document.querySelector('meta[name="htmx-retries"]')?.content) || 3,
      baseURL: document.querySelector('meta[name="htmx-base-url"]')?.content || ''
    };
  },
  
  onEvent: function(name, evt) {
    if (name === 'htmx:configRequest') {
      // Apply configuration
      const xhr = evt.detail.xhr;
      xhr.timeout = this.config.timeout;
      
      // Modify URL if base URL is configured
      if (this.config.baseURL && !evt.detail.path.startsWith('http')) {
        evt.detail.path = this.config.baseURL + evt.detail.path;
      }
    }
    
    return true;
  }
});
```

### Conditional Extension Loading

```javascript
// Extension that only activates under certain conditions
htmx.defineExtension('conditional', {
  init: function(api) {
    this.active = this.shouldActivate();
  },
  
  shouldActivate: function() {
    // Check various conditions
    return window.innerWidth < 768 || // Mobile only
           localStorage.getItem('debug') === 'true' || // Debug mode
           document.body.classList.contains('dev-mode'); // Development environment
  },
  
  onEvent: function(name, evt) {
    if (!this.active) return true;
    
    // Extension logic only runs when active
    console.log('Conditional extension active for:', name);
    return true;
  }
});
```

## Extension Distribution and Loading

### Dynamic Extension Loading

```javascript
// Load extensions dynamically
async function loadExtension(name, url) {
  try {
    const response = await fetch(url);
    const extensionCode = await response.text();
    
    // Create a safe execution context
    const extensionFunction = new Function('htmx', extensionCode);
    extensionFunction(htmx);
    
    console.log(`Extension ${name} loaded successfully`);
  } catch (error) {
    console.error(`Failed to load extension ${name}:`, error);
  }
}

// Usage
loadExtension('custom-auth', '/js/extensions/auth.js');
```

### Extension Registry

```javascript
// Global extension registry
window.htmxExtensions = {
  available: new Map(),
  loaded: new Set(),
  
  register: function(name, factory) {
    this.available.set(name, factory);
  },
  
  load: function(name) {
    if (this.loaded.has(name)) return;
    
    const factory = this.available.get(name);
    if (factory) {
      htmx.defineExtension(name, factory());
      this.loaded.add(name);
    }
  },
  
  autoLoad: function() {
    // Auto-load extensions based on hx-ext attributes
    document.querySelectorAll('[hx-ext]').forEach(el => {
      const extensions = el.getAttribute('hx-ext').split(',');
      extensions.forEach(ext => {
        this.load(ext.trim());
      });
    });
  }
};

// Register extensions
htmxExtensions.register('my-extension', () => ({
  onEvent: function(name, evt) {
    console.log('My extension:', name);
    return true;
  }
}));

// Auto-load on page load
document.addEventListener('DOMContentLoaded', () => {
  htmxExtensions.autoLoad();
});
```