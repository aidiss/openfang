# HTMX

HTMX is a JavaScript library that extends HTML with modern web interactions through declarative attributes, providing access to AJAX, CSS Transitions, WebSockets, and Server-Sent Events without requiring custom JavaScript code. It enables progressive enhancement by completing HTML as a true hypertext system.

## Package Information

- **Package Name**: htmx.org
- **Package Type**: npm
- **Language**: JavaScript
- **Installation**: `npm install htmx.org`

## Core Imports

**Browser Script Tag:**
```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.6/dist/htmx.min.js"></script>
```

**ES Modules:**
```javascript
import htmx from "htmx.org";
```

**CommonJS:**
```javascript
const htmx = require("htmx.org");
```

**AMD:**
```javascript
require(["htmx.org"], function(htmx) {
  // use htmx
});
```

## Basic Usage

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.6/dist/htmx.min.js"></script>
</head>
<body>
  <!-- Simple AJAX request triggered by button click -->
  <button hx-get="/api/data" hx-target="#content">
    Load Data
  </button>
  <div id="content">
    <!-- Response will be inserted here -->
  </div>
  
  <!-- Form submission with AJAX -->
  <form hx-post="/api/users" hx-target="#result">
    <input type="text" name="name" placeholder="Name">
    <button type="submit">Create User</button>
  </form>
  <div id="result"></div>
</body>
</html>
```

## Architecture

HTMX extends HTML through several key components:

- **Attribute System**: HTML attributes that declaratively specify behavior (hx-get, hx-post, hx-target, etc.)
- **Event System**: Rich event lifecycle with custom events for request/response handling
- **Swap System**: Flexible content replacement strategies (innerHTML, outerHTML, beforeend, etc.)
- **Request Processing**: Automatic form data collection, header management, and response handling
- **Extension System**: Plugin architecture for custom behaviors and integrations
- **Configuration**: Global settings for default behaviors, timeouts, CSS classes, and more

## Capabilities

### Event Processing

Core event handling and lifecycle management for processing new content and managing user interactions.

```javascript { .api }
// Register callback for newly loaded content
function onLoad(callback: (elt: Node) => void): EventListener;

// Process new content to enable htmx behavior
function process(elt: Element | string): void;

// Add event listeners with htmx-aware handling
function on(target: EventTarget | string, event: string, listener: EventListener, options?: any): EventListener;

// Remove event listeners
function off(target: EventTarget | string, event: string, listener?: EventListener): EventListener;

// Trigger events on elements
function trigger(elt: EventTarget | string, eventName: string, detail?: any): boolean;
```

[Event Processing](./event-processing.md)

### AJAX Requests

Programmatic AJAX request functionality for issuing htmx-style requests with full configuration options.

```javascript { .api }
// Issue htmx-style AJAX request
function ajax(verb: HttpVerb, path: string, context: Element | string | HtmxAjaxHelperContext): Promise<void>;

type HttpVerb = "get" | "head" | "post" | "put" | "delete" | "connect" | "options" | "trace" | "patch";

interface HtmxAjaxHelperContext {
  source?: Element | string;
  event?: Event;
  handler?: HtmxAjaxHandler;
  target?: Element | string;
  swap?: HtmxSwapStyle;
  values?: any | FormData;
  headers?: Record<string, string>;
  select?: string;
}
```

[AJAX Requests](./ajax-requests.md)

### DOM Querying

Utility functions for finding and querying DOM elements with htmx-aware selectors.

```javascript { .api }
// Find single element matching selector
function find(eltOrSelector: ParentNode | string, selector?: string): Element | null;

// Find all elements matching selector
function findAll(eltOrSelector: ParentNode | string, selector?: string): NodeListOf<Element>;

// Find closest matching element in parentage
function closest(elt: Element | string, selector: string): Element | null;

// Get input values for element using htmx resolution
function values(elt: Element, type: HttpVerb): Object;
```

[DOM Querying](./dom-querying.md)

### DOM Manipulation

Functions for manipulating DOM elements including class management, content swapping, and element removal.

```javascript { .api }
// Remove element with optional delay
function remove(elt: Node, delay?: number): void;

// Add CSS class to element
function addClass(elt: Element | string, clazz: string, delay?: number): void;

// Remove CSS class from element
function removeClass(node: Node | string, clazz: string, delay?: number): void;

// Toggle CSS class on element
function toggleClass(elt: Element | string, clazz: string): void;

// Take class from siblings (ensure only this element has class)
function takeClass(elt: Node | string, clazz: string): void;

// Perform complete content swap with transitions
function swap(target: string | Element, content: string, swapSpec: HtmxSwapSpecification, swapOptions?: SwapOptions): void;
```

[DOM Manipulation](./dom-manipulation.md)

### Extension System

Plugin architecture for extending htmx functionality with custom behaviors and integrations.

```javascript { .api }
// Register new extension
function defineExtension(name: string, extension: Partial<HtmxExtension>): void;

// Remove registered extension
function removeExtension(name: string): void;

interface HtmxExtension {
  init: (api: any) => void;
  onEvent: (name: string, event: CustomEvent) => boolean;
  transformResponse: (text: string, xhr: XMLHttpRequest, elt: Element) => string;
  isInlineSwap: (swapStyle: HtmxSwapStyle) => boolean;
  handleSwap: (swapStyle: HtmxSwapStyle, target: Node, fragment: Node, settleInfo: HtmxSettleInfo) => boolean | Node[];
  encodeParameters: (xhr: XMLHttpRequest, parameters: FormData, elt: Node) => any | string | null;
  getSelectors: () => string[] | null;
}
```

[Extension System](./extension-system.md)

### Configuration

Global configuration object controlling all aspects of htmx behavior including defaults, timeouts, CSS classes, and security settings.

```javascript { .api }
// Main configuration object
const config: {
  // History & Navigation
  historyEnabled: boolean;
  historyCacheSize: number;
  refreshOnHistoryMiss: boolean;
  scrollIntoViewOnBoost: boolean;
  
  // Swap Behavior  
  defaultSwapStyle: HtmxSwapStyle;
  defaultSwapDelay: number;
  defaultSettleDelay: number;
  globalViewTransitions: boolean;
  
  // CSS Classes
  indicatorClass: string;
  requestClass: string;
  addedClass: string;
  settlingClass: string;
  swappingClass: string;
  
  // Security
  allowEval: boolean;
  allowScriptTags: boolean;
  selfRequestsOnly: boolean;
  
  // Request handling
  withCredentials: boolean;
  timeout: number;
  methodsThatUseUrlParams: HttpVerb[];
  
  // WebSocket
  wsReconnectDelay: string | function;
  wsBinaryType: BinaryType;
  
  // Response handling
  responseHandling: HtmxResponseHandlingConfig[];
};

type HtmxSwapStyle = "innerHTML" | "outerHTML" | "beforebegin" | "afterbegin" | "beforeend" | "afterend" | "delete" | "none" | string;
```

[Configuration](./configuration.md)

### Debugging & Utilities

Tools for debugging htmx behavior and utility functions for common operations.

```javascript { .api }
// Enable logging of all htmx events
function logAll(): void;

// Disable htmx event logging
function logNone(): void;

// Custom logger for htmx events
let logger: any;

// Parse timing intervals (e.g., "1s", "500ms")
function parseInterval(str: string): number | undefined;

// Current htmx version
const version: string;

// Location proxy for page reloads
const location: Location;
```

[Debugging & Utilities](./debugging-utilities.md)

## Global Types

```javascript { .api }
// HTTP methods supported by htmx
type HttpVerb = "get" | "head" | "post" | "put" | "delete" | "connect" | "options" | "trace" | "patch";

// Content swap styles
type HtmxSwapStyle = "innerHTML" | "outerHTML" | "beforebegin" | "afterbegin" | "beforeend" | "afterend" | "delete" | "none" | string;

// Complete swap specification
interface HtmxSwapSpecification {
  swapStyle: HtmxSwapStyle;
  swapDelay: number;
  settleDelay: number;
  transition?: boolean;
  ignoreTitle?: boolean;
  head?: string;
  scroll?: "top" | "bottom" | number;
  scrollTarget?: string;
  show?: string;
  showTarget?: string;
  focusScroll?: boolean;
}

// Swap operation options
interface SwapOptions {
  select?: string;
  selectOOB?: string;
  eventInfo?: any;
  anchor?: string;
  contextElement?: Element;
  afterSwapCallback?: swapCallback;
  afterSettleCallback?: swapCallback;
  beforeSwapCallback?: swapCallback;
  title?: string;
  historyRequest?: boolean;
}

type swapCallback = () => any;

// Trigger specification for events
interface HtmxTriggerSpecification {
  trigger: string;
  pollInterval?: number;
  eventFilter?: ConditionalFunction;
  changed?: boolean;
  once?: boolean;
  consume?: boolean;
  delay?: number;
  from?: string;
  target?: string;
  throttle?: number;
  queue?: string;
  root?: string;
  threshold?: string;
}

// Request configuration
interface HtmxRequestConfig {
  boosted: boolean;
  useUrlParams: boolean;
  formData: FormData;
  parameters: any;
  unfilteredFormData: FormData;
  unfilteredParameters: any;
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

// Response information
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

// Validation error
interface HtmxElementValidationError {
  elt: Element;
  message: string;
  validity: ValidityState;
}

// HTTP headers
type HtmxHeaderSpecification = Record<string, string>;

// Response handling configuration
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

// Settlement information
interface HtmxSettleInfo {
  tasks: HtmxSettleTask[];
  elts: Element[];
  title?: string;
}

type HtmxSettleTask = () => void;

// AJAX handler function
type HtmxAjaxHandler = (elt: Element, responseInfo: HtmxResponseInfo) => any;

// Conditional function for event filtering
type ConditionalFunction = ((this: Node, evt: Event) => boolean) & {
  source: string;
};

// Additional AJAX context
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

// Before swap event details
interface HtmxBeforeSwapDetails extends HtmxResponseInfo {
  shouldSwap: boolean;
  serverResponse: any;
  isError: boolean;
  ignoreTitle: boolean;
  selectOverride: string;
  swapOverride: string;
}
```