# AJAX Requests

Programmatic AJAX request functionality for issuing htmx-style requests with full configuration options and promise-based responses.

## Capabilities

### AJAX Helper Function

Issues htmx-style AJAX requests programmatically with the same behavior as declarative attributes.

```javascript { .api }
/**
 * Issues an htmx-style AJAX request programmatically
 * @param verb - HTTP method to use
 * @param path - URL to request
 * @param context - Target element, selector, or detailed configuration object
 * @returns Promise that resolves when the request completes
 */
function ajax(verb: HttpVerb, path: string, context: Element | string | HtmxAjaxHelperContext): Promise<void>;

type HttpVerb = "get" | "head" | "post" | "put" | "delete" | "connect" | "options" | "trace" | "patch";
```

**Basic Usage Examples:**

```javascript
// Simple GET request updating target element
htmx.ajax('GET', '/api/users', '#user-list');

// POST request with element target
const form = document.getElementById('my-form');
htmx.ajax('POST', '/api/users', form);

// Using promises
htmx.ajax('GET', '/api/data', '#content')
  .then(() => {
    console.log('Request completed successfully');
  })
  .catch((error) => {
    console.error('Request failed:', error);
  });

// DELETE request
htmx.ajax('DELETE', '/api/users/123', '#user-123');
```

### Advanced Context Configuration

For complex scenarios, use the context object to specify detailed request configuration.

```javascript { .api }
interface HtmxAjaxHelperContext {
  /** Element that triggered the request */
  source?: Element | string;
  
  /** Event that triggered the request */
  event?: Event;
  
  /** Custom handler for response processing */
  handler?: HtmxAjaxHandler;
  
  /** Target element for content replacement */
  target?: Element | string;
  
  /** How to swap the content (innerHTML, outerHTML, etc.) */
  swap?: HtmxSwapStyle;
  
  /** Form data or additional values to send */
  values?: any | FormData;
  
  /** Additional HTTP headers */
  headers?: Record<string, string>;
  
  /** CSS selector to choose part of response */
  select?: string;
}

type HtmxAjaxHandler = (elt: Element, responseInfo: HtmxResponseInfo) => any;
type HtmxSwapStyle = "innerHTML" | "outerHTML" | "beforebegin" | "afterbegin" | "beforeend" | "afterend" | "delete" | "none" | string;
```

**Advanced Usage Examples:**

```javascript
// Complex request with full configuration
htmx.ajax('POST', '/api/users', {
  source: document.getElementById('create-button'),
  target: '#user-list',
  swap: 'beforeend',
  values: {
    name: 'John Doe',
    email: 'john@example.com'
  },
  headers: {
    'X-Custom-Header': 'value',
    'Content-Type': 'application/json'
  },
  select: '.user-item'
});

// Using FormData for file uploads
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('description', 'Profile photo');

htmx.ajax('POST', '/api/upload', {
  target: '#upload-result',
  values: formData,
  swap: 'innerHTML'
});

// Custom response handler
htmx.ajax('GET', '/api/stats', {
  target: '#stats',
  handler: function(element, responseInfo) {
    if (responseInfo.xhr.status === 200) {
      // Custom processing of successful response
      const data = JSON.parse(responseInfo.xhr.responseText);
      element.innerHTML = `<h3>Stats: ${data.count} items</h3>`;
    }
  }
});

// Conditional swapping based on response
htmx.ajax('POST', '/api/validate', {
  source: '#validation-form',
  target: '#validation-result',
  handler: function(element, responseInfo) {
    if (responseInfo.xhr.status === 422) {
      // Validation errors - swap with error styling
      element.innerHTML = responseInfo.xhr.responseText;
      element.className = 'validation-errors';
    } else {
      // Success - different styling
      element.innerHTML = '<div class="success">Validation passed!</div>';
    }
  }
});
```

### Request and Response Objects

Understanding the request and response objects helps with advanced request handling.

```javascript { .api }
interface HtmxRequestConfig {
  boosted: boolean;
  useUrlParams: boolean;
  formData: FormData;
  parameters: any; // formData proxy
  unfilteredFormData: FormData;
  unfilteredParameters: any; // unfilteredFormData proxy
  headers: HtmxHeaderSpecification;
  elt: Element;
  target: Element;
  verb: HttpVerb;
  errors: HtmxElementValidationError[];
  withCredentials: boolean;
  timeout: number;
  path: string;
  triggeringEvent: Event;
}

interface HtmxResponseInfo {
  xhr: XMLHttpRequest;
  target: Element;
  requestConfig: HtmxRequestConfig;
  etc: HtmxAjaxEtc;
  boosted: boolean;
  select: string;
  pathInfo: {
    requestPath: string;
    finalRequestPath: string;
    responsePath: string | null;
    anchor: string;
  };
  failed?: boolean;
  successful?: boolean;
  keepIndicators?: boolean;
}

type HtmxHeaderSpecification = Record<string, string>;

interface HtmxElementValidationError {
  elt: Element;
  message: string;
  validity: ValidityState;
}

interface HtmxAjaxEtc {
  returnPromise?: boolean;
  handler?: HtmxAjaxHandler;
  select?: string;
  targetOverride?: Element;
  swapOverride?: HtmxSwapStyle;
  headers?: Record<string, string>;
  values?: any | FormData;
  credentials?: boolean;
  timeout?: number;
}
```

**Working with Request Configuration:**

```javascript
// Listen for request configuration
htmx.on('htmx:configRequest', function(evt) {
  const config = evt.detail;
  
  // Add authentication header
  config.headers['Authorization'] = 'Bearer ' + getAuthToken();
  
  // Add CSRF token for unsafe methods
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.verb.toUpperCase())) {
    config.headers['X-CSRF-Token'] = getCsrfToken();
  }
  
  // Modify parameters
  config.parameters.timestamp = Date.now();
  
  console.log('Request config:', config);
});

// Handle responses
htmx.on('htmx:afterRequest', function(evt) {
  const responseInfo = evt.detail;
  
  console.log('Response status:', responseInfo.xhr.status);
  console.log('Response headers:', responseInfo.xhr.getAllResponseHeaders());
  console.log('Target element:', responseInfo.target);
  
  // Handle specific status codes
  if (responseInfo.xhr.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  } else if (responseInfo.xhr.status === 403) {
    // Show access denied message
    showNotification('Access denied', 'error');
  }
});
```

### Error Handling

Robust error handling for AJAX requests with custom error processing.

```javascript
// Promise-based error handling
htmx.ajax('POST', '/api/risky-operation', '#result')
  .then(() => {
    showNotification('Operation completed successfully', 'success');
  })
  .catch((error) => {
    console.error('Operation failed:', error);
    showNotification('Operation failed, please try again', 'error');
  });

// Event-based error handling
htmx.on('htmx:responseError', function(evt) {
  const xhr = evt.detail.xhr;
  const target = evt.detail.target;
  
  console.log('Response error:', xhr.status, xhr.statusText);
  
  // Custom error handling based on status
  switch (xhr.status) {
    case 400:
      target.innerHTML = '<div class="error">Bad request. Please check your input.</div>';
      break;
    case 404:
      target.innerHTML = '<div class="error">Resource not found.</div>';
      break;
    case 500:
      target.innerHTML = '<div class="error">Server error. Please try again later.</div>';
      break;
    default:
      target.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
  }
});

// Handle network errors
htmx.on('htmx:sendError', function(evt) {
  console.error('Network error:', evt.detail.error);
  showNotification('Network error. Please check your connection.', 'error');
});

// Global error handler with retry logic
let retryCount = 0;
const maxRetries = 3;

htmx.on('htmx:responseError', function(evt) {
  if (retryCount < maxRetries && evt.detail.xhr.status >= 500) {
    retryCount++;
    console.log(`Retrying request (attempt ${retryCount}/${maxRetries})`);
    
    // Retry after delay
    setTimeout(() => {
      htmx.ajax(
        evt.detail.requestConfig.verb,
        evt.detail.requestConfig.path,
        evt.detail.target
      );
    }, 1000 * retryCount); // Exponential backoff
  } else {
    retryCount = 0; // Reset for next operation
    showNotification('Operation failed after retries', 'error');
  }
});
```

### Integration Patterns

Common patterns for integrating AJAX requests with application logic.

```javascript
// API wrapper functions
function createUser(userData, targetElement) {
  return htmx.ajax('POST', '/api/users', {
    target: targetElement,
    values: userData,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

function updateUser(userId, userData, targetElement) {
  return htmx.ajax('PUT', `/api/users/${userId}`, {
    target: targetElement,
    values: JSON.stringify(userData),
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

function deleteUser(userId, targetElement) {
  return htmx.ajax('DELETE', `/api/users/${userId}`, {
    target: targetElement,
    swap: 'delete'
  });
}

// Usage with confirmation
async function handleUserDelete(userId) {
  const confirmed = await showConfirmDialog('Delete this user?');
  if (confirmed) {
    try {
      await deleteUser(userId, `#user-${userId}`);
      showNotification('User deleted successfully', 'success');
    } catch (error) {
      showNotification('Failed to delete user', 'error');
    }
  }
}

// Chaining requests
async function createAndSetupUser(userData) {
  try {
    // Create user
    await createUser(userData, '#user-list');
    
    // Send welcome email
    await htmx.ajax('POST', '/api/send-welcome-email', {
      values: { userId: userData.id },
      target: '#notification-area'
    });
    
    // Log activity
    await htmx.ajax('POST', '/api/log-activity', {
      values: { 
        action: 'user_created',
        userId: userData.id 
      }
    });
    
    showNotification('User created and setup completed', 'success');
  } catch (error) {
    console.error('User creation flow failed:', error);
    showNotification('Failed to complete user setup', 'error');
  }
}
```