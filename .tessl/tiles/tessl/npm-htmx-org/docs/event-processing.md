# Event Processing

Core event handling and lifecycle management for processing new content and managing user interactions in htmx applications.

## Capabilities

### Process New Content

Processes new content to enable htmx behavior on dynamically added elements.

```javascript { .api }
/**
 * Processes new content, enabling htmx behavior on elements
 * @param elt - Element or CSS selector to process
 */
function process(elt: Element | string): void;
```

**Usage Example:**

```javascript
// Process dynamically added content
const newDiv = document.createElement('div');
newDiv.innerHTML = '<button hx-get="/api/data">Click me</button>';
document.body.appendChild(newDiv);

// Enable htmx behavior on the new content
htmx.process(newDiv);

// Or process by selector
htmx.process('#dynamic-content');
```

### Content Load Callbacks

Registers callbacks to run when new content is loaded and processed by htmx.

```javascript { .api }
/**
 * Adds a callback for the htmx:load event to process new content
 * @param callback - Function to call on newly loaded content
 * @returns EventListener that was registered
 */
function onLoad(callback: (elt: Node) => void): EventListener;
```

**Usage Example:**

```javascript
// Register callback for all newly loaded content
htmx.onLoad(function(content) {
  console.log('New content loaded:', content);
  
  // Initialize custom components in the new content
  const widgets = content.querySelectorAll('.my-widget');
  widgets.forEach(widget => {
    // Initialize widget functionality
    initializeWidget(widget);
  });
});

// The callback fires for:
// - Initial page load
// - AJAX response content
// - Content added via hx-swap-oob
```

### Event Listeners

Add and remove event listeners with htmx-aware handling.

```javascript { .api }
/**
 * Adds an event listener to an element with htmx-aware handling
 * Supports multiple overload patterns for flexible usage
 */
function on(target: EventTarget | string, event: string, listener: EventListener, options?: any): EventListener;
function on(event: string, listener: EventListener): EventListener; // Global listener
function on(target: EventTarget | string, event: string, listener: EventListener, options?: boolean): EventListener;

/**
 * Removes an event listener from an element
 */
function off(target: EventTarget | string, event: string, listener?: EventListener): EventListener;
function off(event: string, listener: EventListener): EventListener; // Global listener removal
```

**Usage Examples:**

```javascript
// Add event listener to specific element
const button = document.getElementById('my-button');
htmx.on(button, 'click', function(e) {
  console.log('Button clicked');
});

// Add global event listener using selector
htmx.on('click', function(e) {
  if (e.target.matches('.my-class')) {
    console.log('Element with .my-class clicked');
  }
});

// Add event listener by selector string
htmx.on('#my-form', 'submit', function(e) {
  console.log('Form submitted');
});

// Add with options
htmx.on(document, 'keydown', handleKeydown, { passive: true });

// Remove event listener
const handler = function(e) { console.log('clicked'); };
htmx.on('#button', 'click', handler);
htmx.off('#button', 'click', handler);

// Remove global listener
htmx.off('click', globalHandler);
```

### Event Triggering

Triggers custom events on elements, useful for programmatic event firing and inter-component communication.

```javascript { .api }
/**
 * Triggers a given event on an element
 * @param elt - Target element or CSS selector
 * @param eventName - Name of the event to trigger
 * @param detail - Optional event detail data
 * @returns boolean indicating if event was not cancelled
 */
function trigger(elt: EventTarget | string, eventName: string, detail?: any): boolean;
```

**Usage Examples:**

```javascript
// Trigger simple event
htmx.trigger('#my-element', 'customEvent');

// Trigger event with data
htmx.trigger(document.body, 'dataUpdated', {
  timestamp: Date.now(),
  source: 'user-action'
});

// Trigger htmx built-in events
htmx.trigger('#form', 'htmx:validate');
htmx.trigger('.loading-indicator', 'htmx:abort');

// Use return value to check if event was cancelled
const wasProcessed = htmx.trigger('#component', 'beforeAction');
if (wasProcessed) {
  // Event was not cancelled, proceed
  performAction();
}
```

## HTMX Event Lifecycle

Understanding htmx's event system is crucial for effective event processing:

### Request Lifecycle Events

- `htmx:configRequest` - Before request is configured
- `htmx:beforeRequest` - Before request is sent
- `htmx:afterRequest` - After request completes
- `htmx:sendError` - When request fails to send
- `htmx:responseError` - When response has error status

### Content Lifecycle Events

- `htmx:beforeSwap` - Before content is swapped
- `htmx:afterSwap` - After content is swapped
- `htmx:beforeSettle` - Before elements are settled
- `htmx:afterSettle` - After elements are settled
- `htmx:load` - When new content is loaded and processed

### Special Events

- `htmx:abort` - Cancel in-flight requests
- `htmx:confirm` - Override confirmation dialogs
- `htmx:prompt` - Override prompt dialogs
- `htmx:pushedIntoHistory` - When URL is pushed to history
- `htmx:replacedInHistory` - When URL replaces history entry

**Event Handling Example:**

```javascript
// Listen for request start
htmx.on('htmx:beforeRequest', function(evt) {
  console.log('Starting request to:', evt.detail.requestConfig.path);
  // Show loading indicator
  showLoading();
});

// Listen for request completion
htmx.on('htmx:afterRequest', function(evt) {
  console.log('Request completed');
  hideLoading();
  
  // Check for errors
  if (evt.detail.failed) {
    console.error('Request failed');
    showError('Request failed, please try again');
  }
});

// Listen for new content
htmx.on('htmx:load', function(evt) {
  // Initialize components in new content
  initializeComponents(evt.target);
});

// Override confirmation
htmx.on('htmx:confirm', function(evt) {
  // Use custom confirmation dialog
  evt.preventDefault();
  
  showCustomConfirm(evt.detail.question).then(confirmed => {
    if (confirmed) {
      evt.detail.issueRequest();
    }
  });
});
```

## Integration with Frameworks

Event processing integrates well with frontend frameworks:

```javascript
// React integration
useEffect(() => {
  const cleanup = htmx.onLoad((content) => {
    // Process React components in htmx content
    const reactMounts = content.querySelectorAll('[data-react-component]');
    reactMounts.forEach(mount => {
      const componentName = mount.dataset.reactComponent;
      const props = JSON.parse(mount.dataset.reactProps || '{}');
      ReactDOM.render(React.createElement(components[componentName], props), mount);
    });
  });
  
  return () => htmx.off('htmx:load', cleanup);
}, []);

// Vue integration
htmx.onLoad((content) => {
  const vueApps = content.querySelectorAll('[data-vue-app]');
  vueApps.forEach(el => {
    const app = createApp({
      // Vue component definition
    });
    app.mount(el);
  });
});
```